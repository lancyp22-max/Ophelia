package com.ophelia.model;

import java.time.Instant;

public record TelemetryEvent(
        String event,
        String reason,
        String txId,
        String initiator,
        Instant emittedAt
) {
}
