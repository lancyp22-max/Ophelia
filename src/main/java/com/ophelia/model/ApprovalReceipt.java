package com.ophelia.model;

import java.time.Instant;

/**
 * Signed, single-use authorization from an external trusted approval broker.
 * The request caller supplies this receipt, but does not get to sign it.
 * signature is unpadded Base64URL Ed25519 over the versioned payload.
 */
public record ApprovalReceipt(
        String receiptId,
        String requestHash,
        String action,
        String stateKey,
        String requestedValueHash,
        String sessionId,
        Instant issuedAt,
        Instant expiresAt,
        String nonce,
        String issuerId,
        String signature
) {
}
