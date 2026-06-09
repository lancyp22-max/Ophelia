package com.ophelia.model;

import java.util.List;

public record MemoryPalaceSnapshot(
        String version,
        String principle,
        List<MemoryStack> stack,
        List<MemoryHall> halls,
        List<MemoryDrawer> drawers,
        List<MemoryItem> items,
        List<TemporalFact> temporalFacts,
        List<String> retrievalRules
) {
}
