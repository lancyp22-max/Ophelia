package com.ophelia;

import com.ophelia.modelbridge.CapabilityState;
import com.ophelia.modelbridge.ModelAdapter;
import com.ophelia.modelbridge.ModelBridge;
import com.ophelia.modelbridge.ModelCapability;
import com.ophelia.modelbridge.ModelCapabilityManifest;
import com.ophelia.modelbridge.ModelTurnEvent;
import com.ophelia.modelbridge.ModelTurnEventType;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ModelBridgeContractTest {

    @Test
    void unknownCapabilitiesFailClosed() {
        ModelBridge bridge = new ModelBridge();
        bridge.register(adapterWithCapabilities(Map.of(
                "async_tool_calling",
                new ModelCapability("async_tool_calling", CapabilityState.SUPPORTED, "fixture"),
                "fast_mode",
                new ModelCapability("fast_mode", CapabilityState.CONDITIONAL, "fixture")
        )));

        assertTrue(bridge.supports("fixture-provider", "fixture-model", "async_tool_calling"));
        assertFalse(bridge.supports("fixture-provider", "fixture-model", "fast_mode"));
        assertFalse(bridge.supports("fixture-provider", "fixture-model", "not_declared"));
        assertEquals(
                CapabilityState.UNKNOWN,
                bridge.capabilityState("fixture-provider", "fixture-model", "not_declared")
        );
    }

    @Test
    void duplicateAdapterRegistrationIsRejected() {
        ModelBridge bridge = new ModelBridge();
        ModelAdapter adapter = adapterWithCapabilities(Map.of());

        bridge.register(adapter);

        assertThrows(IllegalStateException.class, () -> bridge.register(adapter));
    }

    @Test
    void asyncToolEventsRequireOriginalCallId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new ModelTurnEvent(
                        "turn-1",
                        "event-1",
                        ModelTurnEventType.TOOL_CALL_COMPLETED,
                        null,
                        Instant.parse("2026-09-04T00:00:00Z"),
                        Map.of()
                )
        );

        ModelTurnEvent event = new ModelTurnEvent(
                "turn-1",
                "event-2",
                ModelTurnEventType.TOOL_CALL_COMPLETED,
                "call-9",
                Instant.parse("2026-09-04T00:00:01Z"),
                Map.of("result", "ready")
        );

        assertEquals("turn-1", event.turnId());
        assertEquals("call-9", event.callId());
    }

    @Test
    void steeringDoesNotInventToolCallIdentity() {
        ModelTurnEvent event = new ModelTurnEvent(
                "turn-2",
                "event-3",
                ModelTurnEventType.STEERING,
                null,
                Instant.parse("2026-09-04T00:00:02Z"),
                Map.of("instruction", "change direction")
        );

        assertEquals(ModelTurnEventType.STEERING, event.type());
        assertEquals(null, event.callId());
    }

    private static ModelAdapter adapterWithCapabilities(Map<String, ModelCapability> capabilities) {
        ModelCapabilityManifest manifest = new ModelCapabilityManifest(
                "fixture-manifest",
                "fixture-provider",
                "fixture-model",
                LocalDate.of(2026, 9, 4),
                "fixture-api",
                capabilities,
                List.of("fixture-evidence")
        );

        return new ModelAdapter() {
            @Override
            public String provider() {
                return "fixture-provider";
            }

            @Override
            public String model() {
                return "fixture-model";
            }

            @Override
            public ModelCapabilityManifest capabilityManifest() {
                return manifest;
            }
        };
    }
}
