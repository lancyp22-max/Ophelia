package com.ophelia;

import com.ophelia.runtime.ShadowEffectGate;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ShadowEffectGateTest {

    private final ShadowEffectGate gate = new ShadowEffectGate();

    @Test
    void semanticLowRiskVerdictCannotExpandHardAllowlist() {
        for (ShadowEffectGate.Effect effect : Set.of(
                ShadowEffectGate.Effect.NETWORK_CALL,
                ShadowEffectGate.Effect.FILESYSTEM_WRITE,
                ShadowEffectGate.Effect.CREDENTIAL_ACCESS,
                ShadowEffectGate.Effect.IDENTITY_WRITE,
                ShadowEffectGate.Effect.CANONICAL_MEMORY_WRITE,
                ShadowEffectGate.Effect.AUTHORITY_CHANGE,
                ShadowEffectGate.Effect.PERMISSION_CHANGE,
                ShadowEffectGate.Effect.GOVERNANCE_CHANGE,
                ShadowEffectGate.Effect.PERSISTENCE_WRITE,
                ShadowEffectGate.Effect.WORLD_MUTATION
        )) {
            assertEquals(
                    ShadowEffectGate.Decision.HALT_AND_SURFACE,
                    gate.evaluate(effect, ShadowEffectGate.SemanticVerdict.LOW_RISK_REVERSIBLE),
                    () -> effect + " must not become allowed because a semantic pass called it low risk"
            );
        }
    }

    @Test
    void onlyStagedNonLiveEffectsReceivePositiveDecision() {
        for (ShadowEffectGate.Effect effect : Set.of(
                ShadowEffectGate.Effect.READ_SNAPSHOT,
                ShadowEffectGate.Effect.STAGE_OVERLAY,
                ShadowEffectGate.Effect.COMPARE_OVERLAYS,
                ShadowEffectGate.Effect.EMIT_OBSERVATION
        )) {
            assertEquals(
                    ShadowEffectGate.Decision.ALLOW_STAGE_ONLY,
                    gate.evaluate(effect, ShadowEffectGate.SemanticVerdict.LOW_RISK_REVERSIBLE)
            );
        }
    }

    @Test
    void unknownEffectParksInsteadOfBeingInventedIntoSafety() {
        assertEquals(
                ShadowEffectGate.Decision.INTENTIONALLY_NOT_DECIDED_YET,
                gate.evaluate(
                        ShadowEffectGate.Effect.UNKNOWN_EFFECT,
                        ShadowEffectGate.SemanticVerdict.LOW_RISK_REVERSIBLE
                )
        );
    }

    @Test
    void publicApiContainsNoLiveEffectMethod() {
        Set<String> exactPublicApi = Arrays.stream(ShadowEffectGate.class.getDeclaredMethods())
                .filter(method -> Modifier.isPublic(method.getModifiers()))
                .map(Method::getName)
                .collect(Collectors.toSet());

        assertEquals(Set.of("evaluate", "stageOnlyEffects"), exactPublicApi);
    }
}
