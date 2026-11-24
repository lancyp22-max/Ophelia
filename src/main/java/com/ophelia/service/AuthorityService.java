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
    private static final String INVARIANT_RULE = "No state mutation without verified scoped approval";

    private final Map<String, String> stateStore = new ConcurrentHashMap<>();
    private final ApprovalReceiptVerifier receiptVerifier;

    public AuthorityService(ApprovalReceiptVerifier receiptVerifier) {
        this.receiptVerifier = receiptVerifier;
    }

    // Ensure value observation, nonce consumption and state commit share one
    // ordering within this process. Cross-process replay remains unsupported.
    public synchronized AuthorityTxResponse evaluate(AuthorityTxRequest request) {
        String previousValue = stateStore.get(request.stateKey());

        // surfaceAck, even if true, is neither inspected nor authoritative.
        if (!receiptVerifier.verifyAndConsume(request)) {
            TelemetryEvent telemetry = new TelemetryEvent(
                    "HALT_AND_SURFACE",
                    "approval_receipt_not_verified",
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
                "verified_approval_receipt",
                request.txId(),
                request.initiator(),
                Instant.now()
        );

        return new AuthorityTxResponse(
                request.txId(),
                INVARIANT_ID,
                "committed",
                "verified_approval_receipt",
                true,
                previousValue,
                request.requestedValue(),
                telemetry,
                Instant.now()
        );
    }
}
