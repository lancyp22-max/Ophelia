package com.ophelia.model;

import java.time.Instant;

public record AuthorityTxResponse(
        String txId,
        String invariant,
        String status,
        String reason,
        boolean committed,
        String previousValue,
        String currentValue,
        TelemetryEvent telemetry,
        Instant processedAt
) {
}
