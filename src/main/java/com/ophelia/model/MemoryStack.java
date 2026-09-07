package com.ophelia.model;

import java.util.List;

public record MemoryStack(
        String id,
        String purpose,
        String lifespan,
        String compression,
        List<String> loadOrder,
        List<String> retrieves
) {
}
