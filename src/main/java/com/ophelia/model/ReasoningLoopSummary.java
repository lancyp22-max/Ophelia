package com.ophelia.model;

import java.util.List;

public record ReasoningLoopSummary(
        int loopNumber,
        String loopType,
        String summary,
        List<String> newFindings,
        double confidence
) {
}
