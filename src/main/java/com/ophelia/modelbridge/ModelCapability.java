package com.ophelia.modelbridge;

import java.util.Objects;

public record ModelCapability(
        String id,
        CapabilityState state,
        String evidence
) {
    public ModelCapability {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("capability id must not be blank");
        }
        state = Objects.requireNonNull(state, "capability state must not be null");
        evidence = evidence == null ? "" : evidence;
    }
}
