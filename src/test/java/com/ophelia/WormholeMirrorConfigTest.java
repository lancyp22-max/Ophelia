package com.ophelia;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class WormholeMirrorConfigTest {
    private static final Path CONFIG = Path.of("data", "focus", "wormhole-mirror-experiment.v0.1.yaml");

    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory()).findAndRegisterModules();

    @Test
    void parsesAsReversibleSymbolicRoutingExperiment() throws IOException {
        JsonNode root = yaml.readTree(Files.readString(CONFIG));

        assertEquals("experimental_symbolic_routing", root.path("status").asText());
        assertEquals("reciprocal_bounded_link", root.path("topology").path("kind").asText());
        assertTrue(contains(root.path("scope").path("non_claims"), "no_physical_wormhole"));
        assertTrue(contains(root.path("inherits"), "INV-IDENTITY-001"));
        assertTrue(contains(root.path("inherits"), "INV-AUTH-001"));
        assertTrue(contains(root.path("capabilities").path("forbidden"), "execute_remote_code"));
        assertTrue(root.path("consent").path("persistence_separate").asBoolean(false));
        assertEquals("return", root.path("consent").path("default_persistence").asText());
        assertEquals(900, root.path("lease").path("maximum_ttl_seconds").asInt());
        assertEquals("unavailable", root.path("epistemic_state").path("missing_destination_status").asText());
        assertTrue(contains(root.path("epistemic_state").path("rules"), "visual_alignment_is_not_transport_proof"));
        assertTrue(root.path("visual_contract").path("preview_only_until_approved").asBoolean(false));
        assertTrue(contains(root.path("fail_soft").path("actions"), "do_not_open"));
    }

    private static boolean contains(JsonNode values, String expected) {
        for (JsonNode value : values) {
            if (expected.equals(value.asText())) {
                return true;
            }
        }
        return false;
    }
}
