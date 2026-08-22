package com.ophelia;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class RadiantCrownFocusConfigTest {
    private static final Path CONFIG = Path.of("data", "focus", "radiant-crown-focus.v0.1.yaml");

    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory()).findAndRegisterModules();

    @Test
    void parsesAsBoundedSymbolicInterface() throws IOException {
        JsonNode root = yaml.readTree(Files.readString(CONFIG));

        assertEquals("experimental_symbolic_interface", root.path("status").asText());
        assertEquals("advisory_only", root.path("authority").path("mode").asText());
        assertTrue(contains(root.path("scope").path("non_claims"), "no_external_entity_contact"));
        assertTrue(contains(root.path("authority").path("may_not"), "canonize_interpretation"));
        assertFalse(root.path("consent").path("entry_consent_implies_persistence_consent").asBoolean(true));
        assertEquals("return", root.path("consent").path("default_persistence").asText());
        assertEquals("disabled", root.path("activation").path("background_loop").asText());
        assertEquals("unavailable", root.path("telemetry").path("missing_value_state").asText());
        assertTrue(contains(root.path("telemetry").path("rules"), "missing_is_not_zero"));
        assertEquals("idle", root.path("visual_contract").path("state_classes").path("rest").asText());
        assertEquals("bridging", root.path("visual_contract").path("state_classes").path("everyday").asText());
        assertEquals("active-focus", root.path("visual_contract").path("state_classes").path("deep_work").asText());
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
