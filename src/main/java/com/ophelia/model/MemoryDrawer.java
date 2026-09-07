package com.ophelia.model;

import java.util.List;

public record MemoryDrawer(
        String id,
        String hall,
        String name,
        String description,
        List<String> relatedNodes,
        List<String> safetyTags
) {
}
