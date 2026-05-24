package com.ophelia.controller;

import com.ophelia.model.AuthorityTxRequest;
import com.ophelia.model.AuthorityTxResponse;
import com.ophelia.model.SeedDto;
import com.ophelia.service.AuthorityService;
import com.ophelia.service.SeedService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/seeds")
public class SeedController {
    private final SeedService seedService;
    private final AuthorityService authorityService;

    public SeedController(SeedService seedService, AuthorityService authorityService) {
        this.seedService = seedService;
        this.authorityService = authorityService;
    }

    @GetMapping("/sample")
    public SeedDto sample() {
        return seedService.sample();
    }

    @GetMapping("/canonical")
    public Map<String, Object> canonical() {
        return seedService.canonicalIndex();
    }

    @GetMapping("/substrate")
    public Map<String, Object> substrate() {
        return seedService.substrate();
    }

    @GetMapping("/operational")
    public Map<String, Object> operational() {
        return seedService.operationalIndex();
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return seedService.healthCheck();
    }

    @GetMapping("/integrity")
    public Map<String, Object> integrity() {
        return seedService.integrity();
    }

    @PostMapping("/authority/verify")
    public AuthorityTxResponse verifyAuthority(@Valid @RequestBody AuthorityTxRequest request) {
        return authorityService.evaluate(request);
    }
}
