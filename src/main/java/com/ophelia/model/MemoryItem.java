package com.ophelia.model;

import java.time.Instant;
import java.util.List;

public record MemoryItem(
        String id,
        String hall,
        String subject,
        String predicate,
        String object,
        Instant validFrom,
        Instant validTo,
        double confidence,
        String source,
        List<String> relatedNodes,
        List<String> safetyTags,
        String residualTrace
) {
}
