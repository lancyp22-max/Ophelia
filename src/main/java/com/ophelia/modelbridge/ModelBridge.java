package com.ophelia.modelbridge;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public final class ModelBridge {
    private final Map<String, ModelAdapter> adapters = new ConcurrentHashMap<>();

    public void register(ModelAdapter adapter) {
        if (adapter == null) {
            throw new IllegalArgumentException("adapter must not be null");
        }

        String provider = requireIdentityPart(adapter.provider(), "provider");
        String model = requireIdentityPart(adapter.model(), "model");
        ModelCapabilityManifest manifest = adapter.capabilityManifest();
        if (manifest == null) {
            throw new IllegalArgumentException("capability manifest must not be null");
        }
        if (!provider.equals(manifest.provider()) || !model.equals(manifest.model())) {
            throw new IllegalArgumentException(
                    "adapter identity must match capability manifest identity"
            );
        }

        String key = key(provider, model);
        ModelAdapter previous = adapters.putIfAbsent(key, adapter);
        if (previous != null) {
            throw new IllegalStateException("adapter already registered: " + key);
        }
    }

    public Optional<ModelAdapter> find(String provider, String model) {
        if (provider == null || model == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(adapters.get(key(provider, model)));
    }

    public CapabilityState capabilityState(String provider, String model, String capabilityId) {
        return find(provider, model)
                .map(ModelAdapter::capabilityManifest)
                .map(manifest -> manifest.capabilityState(capabilityId))
                .orElse(CapabilityState.UNKNOWN);
    }

    public boolean supports(String provider, String model, String capabilityId) {
        return capabilityState(provider, model, capabilityId) == CapabilityState.SUPPORTED;
    }

    private static String requireIdentityPart(String value, String label) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(label + " must not be blank");
        }
        return value;
    }

    private static String key(String provider, String model) {
        return provider + ":" + model;
    }
}
