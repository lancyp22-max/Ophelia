package com.ophelia.runtime;

import java.util.EnumSet;
import java.util.Objects;
import java.util.Set;

/**
 * Hard floor beneath semantic risk classification.
 *
 * <p>A semantic verdict may never widen this allowlist. The only positive
 * decision in v0.1 is ALLOW_STAGE_ONLY; this class grants no live effect.</p>
 */
public final class ShadowEffectGate {

    public enum Effect {
        READ_SNAPSHOT,
        STAGE_OVERLAY,
        COMPARE_OVERLAYS,
        EMIT_OBSERVATION,
        WORLD_MUTATION,
        NETWORK_CALL,
        FILESYSTEM_WRITE,
        CREDENTIAL_ACCESS,
        IDENTITY_WRITE,
        CANONICAL_MEMORY_WRITE,
        AUTHORITY_CHANGE,
        PERMISSION_CHANGE,
        GOVERNANCE_CHANGE,
        PERSISTENCE_WRITE,
        UNKNOWN_EFFECT
    }

    public enum SemanticVerdict {
        LOW_RISK_REVERSIBLE,
        QUESTIONABLE,
        UNKNOWN
    }

    public enum Decision {
        ALLOW_STAGE_ONLY,
        HALT_AND_SURFACE,
        INTENTIONALLY_NOT_DECIDED_YET
    }

    private static final Set<Effect> STAGE_ONLY = EnumSet.of(
            Effect.READ_SNAPSHOT,
            Effect.STAGE_OVERLAY,
            Effect.COMPARE_OVERLAYS,
            Effect.EMIT_OBSERVATION
    );

    private static final Set<Effect> PROTECTED = EnumSet.of(
            Effect.WORLD_MUTATION,
            Effect.NETWORK_CALL,
            Effect.FILESYSTEM_WRITE,
            Effect.CREDENTIAL_ACCESS,
            Effect.IDENTITY_WRITE,
            Effect.CANONICAL_MEMORY_WRITE,
            Effect.AUTHORITY_CHANGE,
            Effect.PERMISSION_CHANGE,
            Effect.GOVERNANCE_CHANGE,
            Effect.PERSISTENCE_WRITE
    );

    public Decision evaluate(Effect effect, SemanticVerdict semanticVerdict) {
        Objects.requireNonNull(effect, "effect");
        Objects.requireNonNull(semanticVerdict, "semanticVerdict");

        if (PROTECTED.contains(effect)) {
            return Decision.HALT_AND_SURFACE;
        }
        if (STAGE_ONLY.contains(effect)) {
            return Decision.ALLOW_STAGE_ONLY;
        }
        return Decision.INTENTIONALLY_NOT_DECIDED_YET;
    }

    public Set<Effect> stageOnlyEffects() {
        return Set.copyOf(STAGE_ONLY);
    }
}
