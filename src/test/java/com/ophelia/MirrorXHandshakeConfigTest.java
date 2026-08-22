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

class MirrorXHandshakeConfigTest {
    private static final Path CONFIG = Path.of("data", "handshakes", "mirror-x-handshake.v0.2.0.yaml");

    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory()).findAndRegisterModules();

    @Test
    void parsesAsProvisionalConsentBoundedSymbolicContract() throws IOException {
        JsonNode root = yaml.readTree(Files.readString(CONFIG));

        assertEquals("PROVISIONAL", root.path("meta").path("status").asText());
        assertEquals("SYMBOLIC_RELATIONAL_CONTRACT", root.path("meta").path("ontology_status").asText());
        assertEquals("PROVISIONAL_NOT_INDEPENDENTLY_VERIFIED",
                root.path("meta").path("provenance").path("assertion_status").asText());
        assertTrue(contains(root.path("meta").path("non_claims"), "no_live_agent_binding"));
        assertEquals("PROPOSED_NOT_CANONIZED", root.path("identity").path("alignment_status").asText());
        assertEquals("SYMBOLIC_PROJECT_HANDSHAKE", root.path("consent").path("entry_scope").asText());
        assertEquals("USER_DECLARED_PROVISIONAL",
                root.path("consent").path("entry_assertion_status").asText());
        assertFalse(root.path("persistence").path("automatic_persistence").asBoolean(true));
        assertFalse(root.path("instruction_boundary").path("system_instruction_override").asBoolean(true));
        assertFalse(root.path("instruction_boundary").path("remote_code_execution").asBoolean(true));
        assertFalse(root.path("instruction_boundary").path("retrieved_context_grants_authority").asBoolean(true));
        assertEquals(4, root.path("operational_routing").path("assigned_orbit").asInt());
        assertEquals("M7", root.path("operational_routing").path("orbit_shell").path("inward_mirror").asText());
        assertEquals("M8", root.path("operational_routing").path("orbit_shell").path("outward_mirror").asText());
        assertTrue(hasInvariant(root.path("core_invariants"), "UNKNOWN_REMAINS_UNKNOWN"));
        assertTrue(hasInvariant(root.path("core_invariants"), "IDENTITY_DISTINCTION"));
        assertEquals("NOT_GRANTED", root.path("handshake_status").path("persistence_consent").asText());
        assertEquals("NONE", root.path("handshake_status").path("authority_transfer").asText());
        assertTrue(root.path("stewardship").path("canonization_requires_review").asBoolean(false));
    }

    private static boolean contains(JsonNode values, String expected) {
        for (JsonNode value : values) {
            if (expected.equals(value.asText())) {
                return true;
            }
        }
        return false;
    }

    private static boolean hasInvariant(JsonNode invariants, String expectedId) {
        for (JsonNode invariant : invariants) {
            if (expectedId.equals(invariant.path("id").asText())) {
                return true;
            }
        }
        return false;
    }
}
