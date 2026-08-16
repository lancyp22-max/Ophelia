package com.ophelia.model;

import java.util.List;

public record MemoryHall(
        String id,
        String lumarianName,
        String purpose,
        String channel,
        List<String> accepts,
        List<String> rejects,
        List<String> linkedMirrors
) {
}
