package com.ophelia;

import com.ophelia.model.ApprovalReceipt;
import com.ophelia.model.AuthorityTxRequest;
import com.ophelia.service.ApprovalReceiptVerifier;
import com.ophelia.service.AuthorityService;
import org.junit.jupiter.api.Test;

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Signature;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Base64;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AuthorityReceiptTest {
    private static final Instant NOW = Instant.parse("2026-11-01T18:00:00Z");
    private static final String ISSUER = "isolated-local-approval-broker";

    private KeyPair keyPair() throws Exception {
        return KeyPairGenerator.getInstance("Ed25519").generateKeyPair();
    }

    private ApprovalReceiptVerifier verifier(KeyPair keyPair) {
        return new ApprovalReceiptVerifier(
                Base64.getEncoder().encodeToString(keyPair.getPublic().getEncoded()),
                ISSUER,
                Clock.fixed(NOW, ZoneOffset.UTC));
    }

    private AuthorityTxRequest request(boolean oldAck, String value, String session) {
        return new AuthorityTxRequest("tx-1", "agent", "roamer.mode", value, oldAck, session, null);
    }

    private AuthorityTxRequest withReceipt(AuthorityTxRequest r, ApprovalReceipt receipt) {
        return new AuthorityTxRequest(r.txId(), r.initiator(), r.stateKey(),
                r.requestedValue(), r.surfaceAck(), r.sessionId(), receipt);
    }

    private ApprovalReceipt signed(KeyPair pair, AuthorityTxRequest request,
                                    String nonce, Instant issued, Instant expires,
                                    String issuer) throws Exception {
        ApprovalReceipt unsigned = new ApprovalReceipt(
                "receipt-1", ApprovalReceiptVerifier.requestHash(request),
                ApprovalReceiptVerifier.ACTION, request.stateKey(),
                ApprovalReceiptVerifier.valueHash(request.requestedValue()),
                request.sessionId(), issued, expires, nonce, issuer, "");
        Signature signer = Signature.getInstance("Ed25519");
        signer.initSign(pair.getPrivate());
        signer.update(ApprovalReceiptVerifier.signingPayload(unsigned));
        String signature = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(signer.sign());
        return new ApprovalReceipt(unsigned.receiptId(), unsigned.requestHash(),
                unsigned.action(), unsigned.stateKey(), unsigned.requestedValueHash(),
                unsigned.sessionId(), unsigned.issuedAt(), unsigned.expiresAt(),
                unsigned.nonce(), unsigned.issuerId(), signature);
    }

    @Test
    void oldBooleanNeverGrantsAuthorizationAndUnconfiguredVerifierFailsClosed() throws Exception {
        AuthorityTxRequest legacy = request(true, "explore", null);
        AuthorityService service = new AuthorityService(verifier(keyPair()));
        assertEquals("halted", service.evaluate(legacy).status());
        assertFalse(service.evaluate(legacy).committed());

        ApprovalReceiptVerifier unconfigured =
                new ApprovalReceiptVerifier("", "", Clock.fixed(NOW, ZoneOffset.UTC));
        assertFalse(unconfigured.verifyAndConsume(legacy));
    }

    @Test
    void validSignedReceiptCommitsOnceAndReplayHalts() throws Exception {
        KeyPair pair = keyPair();
        AuthorityService service = new AuthorityService(verifier(pair));
        AuthorityTxRequest base = request(false, "explore", "session-1");
        AuthorityTxRequest approved = withReceipt(base,
                signed(pair, base, "nonce-1", NOW.minusSeconds(1),
                        NOW.plusSeconds(60), ISSUER));

        assertTrue(service.evaluate(approved).committed());
        var replay = service.evaluate(approved);
        assertFalse(replay.committed());
        assertEquals("explore", replay.currentValue());
        assertEquals("HALT_AND_SURFACE", replay.telemetry().event());
    }

    @Test
    void tamperingWithValueOrSessionInvalidatesApproval() throws Exception {
        KeyPair pair = keyPair();
        ApprovalReceiptVerifier verifier = verifier(pair);
        AuthorityTxRequest base = request(true, "explore", "session-1");
        ApprovalReceipt receipt = signed(pair, base, "nonce-2", NOW, NOW.plusSeconds(60), ISSUER);
        assertFalse(verifier.verifyAndConsume(withReceipt(
                request(true, "overwrite", "session-1"), receipt)));
        assertFalse(verifier.verifyAndConsume(withReceipt(
                request(true, "explore", "session-2"), receipt)));
        assertTrue(verifier.verifyAndConsume(withReceipt(base, receipt)));
    }

    @Test
    void invalidSignatureUnknownIssuerExpiryAndExcessiveLifetimeDeny() throws Exception {
        KeyPair pair = keyPair();
        KeyPair attacker = keyPair();
        ApprovalReceiptVerifier verifier = verifier(pair);
        AuthorityTxRequest base = request(true, "explore", "session-1");
        assertFalse(verifier.verifyAndConsume(withReceipt(base,
                signed(attacker, base, "nonce-3", NOW, NOW.plusSeconds(60), ISSUER))));
        assertFalse(verifier.verifyAndConsume(withReceipt(base,
                signed(pair, base, "nonce-4", NOW, NOW.plusSeconds(60), "unexpected-issuer"))));
        assertFalse(verifier.verifyAndConsume(withReceipt(base,
                signed(pair, base, "nonce-5", NOW.minusSeconds(120), NOW.minusSeconds(1), ISSUER))));
        assertFalse(verifier.verifyAndConsume(withReceipt(base,
                signed(pair, base, "nonce-6", NOW, NOW.plusSeconds(3600), ISSUER))));
        assertFalse(verifier.verifyAndConsume(withReceipt(base,
                signed(pair, base, "nonce-7", NOW.plusSeconds(120),
                        NOW.plusSeconds(130), ISSUER))));
    }
}
