package com.ophelia.modelbridge;

import java.time.Instant;
import java.util.Map;
import java.util.Objects;

public record ModelTurnEvent(
        String turnId,
        String eventId,
        ModelTurnEventType type,
        String callId,
        Instant occurredAt,
        Map<String, String> metadata
) {
    public ModelTurnEvent {
        if (turnId == null || turnId.isBlank()) {
            throw new IllegalArgumentException("turnId must not be blank");
        }
        if (eventId == null || eventId.isBlank()) {
            throw new IllegalArgumentException("eventId must not be blank");
        }
        type = Objects.requireNonNull(type, "type must not be null");
        occurredAt = Objects.requireNonNull(occurredAt, "occurredAt must not be null");
        metadata = metadata == null ? Map.of() : Map.copyOf(metadata);

        if (requiresCallId(type) && (callId == null || callId.isBlank())) {
            throw new IllegalArgumentException(type + " requires the original callId");
        }
    }

    private static boolean requiresCallId(ModelTurnEventType type) {
        return type == ModelTurnEventType.TOOL_CALL_STARTED
                || type == ModelTurnEventType.TOOL_CALL_COMPLETED
                || type == ModelTurnEventType.TOOL_CALL_FAILED;
    }
}
