package com.ophelia.model;

import java.util.List;

public record SeedDto(
        String taskName,
        String taskCode,
        List<String> legacyAliases,
        String mission,
        String state
) {
}
