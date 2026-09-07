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

class WellspringCurrentLogicConfigTest {
    private static final Path CONFIG = Path.of("data", "focus", "wellspring-current-logic.v0.1.yaml");

    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory()).findAndRegisterModules();

    @Test
    void parsesAsBoundedInformationFlowMetaphor() throws IOException {
        JsonNode root = yaml.readTree(Files.readString(CONFIG));

        assertEquals("experimental_information_flow_model", root.path("status").asText());
        assertTrue(contains(root.path("scope").path("non_claims"), "no_water_memory_claim"));
        assertEquals(5, root.path("flow_controls").path("maximum_active_transfers").asInt());
        assertTrue(root.path("flow_controls").path("pressure_does_not_override_limits").asBoolean(false));
        assertEquals("deny", root.path("permeability_matrix").path("persist").path("default").asText());
        assertEquals("persistence_consent", root.path("permeability_matrix").path("persist").path("requires").asText());
        assertEquals("deny", root.path("permeability_matrix").path("mutate").path("default").asText());
        assertEquals("scoped_authority_and_surface_ack", root.path("permeability_matrix").path("mutate").path("requires").asText());
        assertEquals("multiple_supported_interpretations_remain_visible", root.path("coherence_states").path("branching").path("meaning").asText());
        assertEquals("Neither reflection nor flow transfers authority.", root.path("mirror_integration").path("authority_rule").asText());
        assertEquals("no_flow_with_status_visible", root.path("visual_contract").path("unavailable").asText());
        assertTrue(contains(root.path("fail_soft").path("actions"), "preserve_source_record"));
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
