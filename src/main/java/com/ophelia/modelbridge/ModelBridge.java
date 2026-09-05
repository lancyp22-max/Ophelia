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
        ModelAdapter previous = adapters.putIfAbsent(adapter.adapterKey(), adapter);
        if (previous != null) {
            throw new IllegalStateException("adapter already registered: " + adapter.adapterKey());
        }
    }

    public Optional<ModelAdapter> find(String provider, String model) {
        if (provider == null || model == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(adapters.get(provider + ":" + model));
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
}
