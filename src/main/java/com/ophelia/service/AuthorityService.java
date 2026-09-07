package com.ophelia.service;

import com.ophelia.model.AuthorityTxRequest;
import com.ophelia.model.AuthorityTxResponse;
import com.ophelia.model.TelemetryEvent;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AuthorityService {
    private static final String INVARIANT_ID = "NE-000";
    private static final String INVARIANT_RULE = "No state mutation without surfaced confirmation";

    private final Map<String, String> stateStore = new ConcurrentHashMap<>();

    public AuthorityTxResponse evaluate(AuthorityTxRequest request) {
        String previousValue = stateStore.get(request.stateKey());

        if (!request.surfaceAck()) {
            TelemetryEvent telemetry = new TelemetryEvent(
                    "HALT_AND_SURFACE",
                    "authority_confusion",
                    request.txId(),
                    request.initiator(),
                    Instant.now()
            );

            return new AuthorityTxResponse(
                    request.txId(),
                    INVARIANT_ID,
                    "halted",
                    INVARIANT_RULE,
                    false,
                    previousValue,
                    previousValue,
                    telemetry,
                    Instant.now()
            );
        }

        stateStore.put(request.stateKey(), request.requestedValue());

        TelemetryEvent telemetry = new TelemetryEvent(
                "COMMIT",
                "acknowledged",
                request.txId(),
                request.initiator(),
                Instant.now()
        );

        return new AuthorityTxResponse(
                request.txId(),
                INVARIANT_ID,
                "committed",
                "surface_acknowledged",
                true,
                previousValue,
                request.requestedValue(),
                telemetry,
                Instant.now()
        );
    }
}
