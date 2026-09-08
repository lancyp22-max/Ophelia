package com.ophelia.modelbridge;

public interface ModelAdapter {
    String provider();

    String model();

    ModelCapabilityManifest capabilityManifest();

    default String adapterKey() {
        return provider() + ":" + model();
    }
}
