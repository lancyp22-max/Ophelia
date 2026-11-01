package com.ophelia.config;

import com.ophelia.service.ApprovalReceiptVerifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Clock;

@Configuration
public class ApprovalReceiptConfiguration {
    @Bean
    public ApprovalReceiptVerifier approvalReceiptVerifier(
            @Value("${OPHELIA_AUTHORITY_PUBLIC_KEY_BASE64:}") String verificationKey,
            @Value("${OPHELIA_AUTHORITY_ISSUER_ID:}") String issuerId) {
        // These must be provisioned by the trusted host, outside agent-controlled
        // tools, files and environments. Unset values mean fail-closed.
        return new ApprovalReceiptVerifier(verificationKey, issuerId, Clock.systemUTC());
    }
}
