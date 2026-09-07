package com.ophelia.model;

import java.util.List;

public record ReasoningLoop(
        String taskId,
        String agent,
        String taskType,
        int maxLoops,
        int currentLoop,
        List<String> stopConditions,
        List<String> guardrails,
        List<ReasoningLoopSummary> loopSummaries,
        ReasoningLoopOutput finalOutput
) {
}
