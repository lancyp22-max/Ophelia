package com.ophelia.model;

import java.time.Instant;
import java.util.List;

public record TemporalFact(
        String subject,
        String predicate,
        String object,
        Instant validFrom,
        Instant validTo,
        String sourceLane,
        List<String> safetyTags
) {
}
