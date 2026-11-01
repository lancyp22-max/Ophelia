package com.ophelia.service;

import com.ophelia.model.ApprovalReceipt;
import com.ophelia.model.AuthorityTxRequest;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyFactory;
import java.security.MessageDigest;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.X509EncodedKeySpec;
import java.time.Clock;
import java.time.Instant;
import java.util.Base64;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.Map;

/**
 * Verification-only side of the approval boundary. No signing private key or
 * receipt-issuance endpoint lives in this service. A missing trusted public key
 * denies every state mutation, including ones with surfaceAck=true.
 *
 * The replay ledger is process-local; deployment MUST provide a durable,
 * shared replay store before claiming crash-safe/multi-instance one-time use.
 */
public final class ApprovalReceiptVerifier {
    public static final String ACTION = "STATE_MUTATION";
    private static final int MAX_RECEIPT_LIFETIME_SECONDS = 120;
    private static final int MAX_FUTURE_SKEW_SECONDS = 30;
    private static final int MAX_ACTIVE_NONCES = 10_000;

    private final PublicKey trustedKey;
    private final String trustedIssuer;
    private final Clock authorityClock;
    private final Map<String, Instant> spentNonces = new HashMap<>();

    public ApprovalReceiptVerifier(String publicKeyBase64, String issuerId, Clock authorityClock) {
        this.authorityClock = java.util.Objects.requireNonNull(authorityClock, "authorityClock");
        this.trustedIssuer = issuerId == null ? "" : issuerId.trim();
        if (publicKeyBase64 == null || publicKeyBase64.isBlank() || trustedIssuer.isBlank()) {
            // An unconfigured verifier can only deny; never silently fall back to surfaceAck.
            this.trustedKey = null;
            return;
        }
        try {
            byte[] keyBytes = Base64.getDecoder().decode(publicKeyBase64.trim());
            this.trustedKey = KeyFactory.getInstance("Ed25519")
                    .generatePublic(new X509EncodedKeySpec(keyBytes));
        } catch (GeneralSecurityException | IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid authority verification public key", e);
        }
    }

    public boolean verifyAndConsume(AuthorityTxRequest request) {
        if (trustedKey == null || request == null || request.receipt() == null) {
            return false;
        }
        ApprovalReceipt receipt = request.receipt();
        if (!nonBlank(request.txId()) || !nonBlank(request.initiator())
                || !nonBlank(request.stateKey()) || !nonBlank(request.requestedValue())
                || !nonBlank(request.sessionId()) || !nonBlank(receipt.receiptId())
                || !nonBlank(receipt.nonce()) || !nonBlank(receipt.signature())
                || !trustedIssuer.equals(receipt.issuerId()) || !ACTION.equals(receipt.action())
                || !request.stateKey().equals(receipt.stateKey())
                || !request.sessionId().equals(receipt.sessionId())
                || receipt.issuedAt() == null || receipt.expiresAt() == null) {
            return false;
        }

        Instant now = authorityClock.instant();
        if (receipt.issuedAt().isAfter(now.plusSeconds(MAX_FUTURE_SKEW_SECONDS))
                || !receipt.expiresAt().isAfter(now)
                || !receipt.expiresAt().isAfter(receipt.issuedAt())
                || receipt.expiresAt().isAfter(
                        receipt.issuedAt().plusSeconds(MAX_RECEIPT_LIFETIME_SECONDS))) {
            return false;
        }

        if (!requestHash(request).equals(receipt.requestHash())
                || !valueHash(request.requestedValue()).equals(receipt.requestedValueHash())) {
            return false;
        }

        try {
            Signature verifier = Signature.getInstance("Ed25519");
            verifier.initVerify(trustedKey);
            verifier.update(signingPayload(receipt));
            if (!verifier.verify(Base64.getUrlDecoder().decode(receipt.signature()))) {
                return false;
            }
        } catch (GeneralSecurityException | IllegalArgumentException e) {
            return false;
        }

        return consumeNonce(receipt.issuerId() + ":" + receipt.nonce(), receipt.expiresAt(), now);
    }

    /** Canonical request hash; the approval broker MUST bind exactly these fields. */
    public static String requestHash(AuthorityTxRequest request) {
        return hexSha256(pack("ophelia-state-request/v1", ACTION, request.txId(),
                request.initiator(), request.stateKey(), request.requestedValue(),
                request.sessionId()));
    }

    public static String valueHash(String value) {
        return hexSha256(value.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * Versioned, length-prefixed bytes to sign in a separately isolated broker.
     * Never accept the verification key, issuer trust decision or signing secret
     * from the HTTP request itself.
     */
    public static byte[] signingPayload(ApprovalReceipt receipt) {
        return pack("ophelia-approval-receipt/v1", receipt.receiptId(),
                receipt.requestHash(), receipt.action(), receipt.stateKey(),
                receipt.requestedValueHash(), receipt.sessionId(),
                receipt.issuedAt().toString(), receipt.expiresAt().toString(),
                receipt.nonce(), receipt.issuerId());
    }

    private synchronized boolean consumeNonce(String nonceKey, Instant expiresAt, Instant now) {
        spentNonces.entrySet().removeIf(entry -> !entry.getValue().isAfter(now));
        if (spentNonces.containsKey(nonceKey) || spentNonces.size() >= MAX_ACTIVE_NONCES) {
            return false;
        }
        spentNonces.put(nonceKey, expiresAt);
        return true;
    }

    private static boolean nonBlank(String value) {
        return value != null && !value.isBlank();
    }

    private static String hexSha256(byte[] data) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }

    private static byte[] pack(String... fields) {
        try {
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();
            DataOutputStream out = new DataOutputStream(buffer);
            for (String field : fields) {
                byte[] bytes = java.util.Objects.requireNonNull(field, "signed field")
                        .getBytes(StandardCharsets.UTF_8);
                out.writeInt(bytes.length);
                out.write(bytes);
            }
            out.flush();
            return buffer.toByteArray();
        } catch (IOException e) {
            throw new IllegalStateException("Could not encode receipt", e);
        }
    }
}
