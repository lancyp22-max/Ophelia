package com.ophelia.model;

import java.util.List;

public record ReasoningLoopOutput(
        String finalAnswer,
        double confidence,
        List<String> unresolvedQuestions,
        String haltReason
) {
}
