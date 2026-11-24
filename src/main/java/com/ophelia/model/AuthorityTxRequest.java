package com.ophelia.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;

public record AuthorityTxRequest(
        @NotBlank String txId,
        @NotBlank String initiator,
        @NotBlank String stateKey,
        @NotBlank String requestedValue,
        // Deprecated compatibility field: NEVER proof of authorization.
        boolean surfaceAck,
        String sessionId,
        @Valid ApprovalReceipt receipt
) {
}
