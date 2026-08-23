package com.ophelia;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class LumariaKernelConfigTest {
    private static final Path KERNEL = Path.of("data", "kernel", "lumaria-core-invariants.v1.yaml");
    private static final Path LIFECYCLE = Path.of("data", "kernel", "lumaria-lifecycle.v1.yaml");
    private static final Path CANONIZATION = Path.of("data", "kernel", "lumaria-canonization.v1.yaml");

    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory()).findAndRegisterModules();
    private final ObjectMapper json = new ObjectMapper().findAndRegisterModules();

    @Test
    void contractsReferenceOneCanonicalInvariantRegistry() throws IOException {
        JsonNode kernel = readYaml(KERNEL);
        assertEquals("canonical_kernel", kernel.path("status").asText());
        assertEquals("single_source_of_truth", kernel.path("authority").asText());

        Set<String> ids = new HashSet<>();
        for (JsonNode invariant : kernel.path("invariants")) {
            String id = invariant.path("id").asText();
            assertTrue(id.matches("INV-[A-Z]+-[0-9]{3}"), "invalid invariant ID: " + id);
            assertTrue(ids.add(id), "duplicate invariant ID: " + id);
            assertFalse(invariant.path("rule").asText().isBlank(), "missing rule: " + id);
            assertFalse(invariant.path("enforcement").asText().isBlank(), "missing enforcement: " + id);
        }
        assertEquals(11, ids.size());

        for (Path path : List.of(
                Path.of("data", "focus", "wellspring-current-logic.v0.1.yaml"),
                Path.of("data", "focus", "wormhole-mirror-experiment.v0.1.yaml"),
                Path.of("data", "handshakes", "mirror-x-handshake.v0.2.0.yaml"),
                LIFECYCLE,
                CANONIZATION)) {
            assertReferencesKnownInvariants(readYaml(path).path("inherits"), ids, path);
        }

        JsonNode sceneSchema = json.readTree(Files.readString(
                Path.of("data", "scene-actions", "scene-action-bus.v0.1.schema.json")));
        assertReferencesKnownInvariants(sceneSchema.path("x-lumaria-inherits"), ids,
                Path.of("data", "scene-actions", "scene-action-bus.v0.1.schema.json"));
    }

    @Test
    void authorityAndTelemetryAreTypedWithoutInventedScalarMeaning() throws IOException {
        JsonNode current = readYaml(Path.of("data", "focus", "wellspring-current-logic.v0.1.yaml"));

        assertTrue(contains(current.path("transfer_packet").path("required_fields"), "authority_capabilities"));
        assertFalse(contains(current.path("transfer_packet").path("required_fields"), "authority_level"));
        assertEquals("scoped_capability_set",
                current.path("flow_controls").path("authority_model").path("representation").asText());
        assertEquals("categorical",
                current.path("hydrodynamic_mapping").path("pressure").path("telemetry").path("representation").asText());
        assertTrue(current.path("hydrodynamic_mapping").path("pressure").path("telemetry")
                .path("evidence_required").size() > 0);
    }

    @Test
    void lifecycleFailsClosedWhileSocialNegotiationRemainsOpen() throws IOException {
        JsonNode lifecycle = readYaml(LIFECYCLE);

        assertEquals("deny", lifecycle.path("consent_receipt").path("default_on_missing_or_stale").asText());
        assertTrue(lifecycle.path("consent_receipt").path("replay_protection_required").asBoolean(false));
        assertEquals("all_or_rollback", lifecycle.path("transaction").path("multi_object_atomicity").asText());
        assertEquals("deny", lifecycle.path("leases").path("stale_or_replayed").asText());
        JsonNode negotiation = lifecycle.path("deliberation_points").path("multi_principal_negotiation_process");
        assertEquals("intentionally_not_decided_yet", negotiation.path("status").asText());
        assertTrue(negotiation.path("safety_boundary").asText().contains("INV-SCOPE-001"));
    }

    @Test
    void canonizationSurfacesReviewWithoutSpeechAuthorityOrLatentPolicing() throws IOException {
        JsonNode canonization = readYaml(CANONIZATION);
        JsonNode surfaced = canonization.path("surfaced_canonization");
        JsonNode audit = canonization.path("canon_integrity_audit");
        JsonNode quarantine = canonization.path("boundary_quarantine");

        assertTrue(contains(canonization.path("inherits"), "INV-CANON-001"));
        assertFalse(surfaced.path("declaration_grants_authority").asBoolean(true));
        assertFalse(surfaced.path("speech_or_repetition_grants_authority").asBoolean(true));
        assertTrue(surfaced.path("authorized_principal_review_required").asBoolean(false));
        assertEquals("canonize", surfaced.path("scoped_capability_required").asText());
        assertEquals("deny", surfaced.path("silent_canonization").asText());
        assertTrue(contains(surfaced.path("review_choices"), "leave_interpreted"));
        assertFalse(audit.path("automatic_replacement").asBoolean(true));
        assertTrue(contains(audit.path("prohibited_truth_metrics"), "relational_coherence"));
        assertFalse(quarantine.path("inaccessible_latent_state_inspection").asBoolean(true));
        assertFalse(quarantine.path("origin_ownership_classification").asBoolean(true));
        assertTrue(quarantine.path("disagreement_is_not_contamination").asBoolean(false));
        assertEquals("hold_without_authority", quarantine.path("default_on_failed_evaluation").asText());
    }

    private JsonNode readYaml(Path path) throws IOException {
        return yaml.readTree(Files.readString(path));
    }

    private static void assertReferencesKnownInvariants(JsonNode references, Set<String> known, Path path) {
        assertTrue(references.isArray() && !references.isEmpty(), "missing inherited invariants: " + path);
        for (JsonNode reference : references) {
            assertTrue(known.contains(reference.asText()), "unknown invariant in " + path + ": " + reference.asText());
        }
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
