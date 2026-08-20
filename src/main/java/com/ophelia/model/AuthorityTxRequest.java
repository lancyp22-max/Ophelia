package com.ophelia.model;

import jakarta.validation.constraints.NotBlank;

public record AuthorityTxRequest(
        @NotBlank String txId,
        @NotBlank String initiator,
        @NotBlank String stateKey,
        @NotBlank String requestedValue,
        boolean surfaceAck
) {
}
