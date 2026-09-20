package com.ophelia.modelbridge;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public record ModelCapabilityManifest(
        String manifestId,
        String provider,
        String model,
        LocalDate observedAt,
        String apiFamily,
        Map<String, ModelCapability> capabilities,
        List<String> evidence
) {
    public ModelCapabilityManifest {
        if (manifestId == null || manifestId.isBlank()) {
            throw new IllegalArgumentException("manifestId must not be blank");
        }
        if (provider == null || provider.isBlank()) {
            throw new IllegalArgumentException("provider must not be blank");
        }
        if (model == null || model.isBlank()) {
            throw new IllegalArgumentException("model must not be blank");
        }
        observedAt = Objects.requireNonNull(observedAt, "observedAt must not be null");
        apiFamily = apiFamily == null ? "" : apiFamily;
        capabilities = capabilities == null ? Map.of() : Map.copyOf(capabilities);
        evidence = evidence == null ? List.of() : List.copyOf(evidence);
    }

    public CapabilityState capabilityState(String capabilityId) {
        ModelCapability capability = capabilities.get(capabilityId);
        return capability == null ? CapabilityState.UNKNOWN : capability.state();
    }

    public boolean supports(String capabilityId) {
        return capabilityState(capabilityId) == CapabilityState.SUPPORTED;
    }
}
