package com.ophelia.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.ophelia.model.SeedDto;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class SeedService {
    private static final Path ROOT = Path.of("");
    private static final Path SAMPLE_SEED = ROOT.resolve("seeds/sample-seed.json");
    private static final Path CANONICAL = ROOT.resolve("lumaria_canonical_index.yaml");
    private static final Path SUBSTRATE = ROOT.resolve("ophelia_lumaria_substrate.yaml");
    private static final Path OPERATIONAL = ROOT.resolve("lumaria_operational_index_v1.yaml");
    private static final Path HEALTH = ROOT.resolve("lumaria_health_check.yaml");

    private final ObjectMapper json = new ObjectMapper();
    private final ObjectMapper yaml = new ObjectMapper(new YAMLFactory());

    public SeedDto sample() {
        try {
            return json.readValue(Files.readString(SAMPLE_SEED), SeedDto.class);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to load seed: " + SAMPLE_SEED, ex);
        }
    }

    public Map<String, Object> canonicalIndex() {
        return readYaml(CANONICAL);
    }

    public Map<String, Object> substrate() {
        return readYaml(SUBSTRATE);
    }

    public Map<String, Object> operationalIndex() {
        return readYaml(OPERATIONAL);
    }

    public Map<String, Object> healthCheck() {
        return readYaml(HEALTH);
    }

    public Map<String, Object> integrity() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("root", readText("lumaria_integrity_hash.txt"));
        payload.put("archive", readText("library/lumarian_archive/lumaria_integrity_hash.txt"));
        payload.put("coldSnapshot", readText("backups/cold_snapshot/lumaria_integrity_hash.txt"));
        return payload;
    }

    private Map<String, Object> readYaml(Path path) {
        try {
            return yaml.readValue(Files.readString(path), new TypeReference<>() {});
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to load yaml: " + path, ex);
        }
    }

    private String readText(String relativePath) {
        try {
            return Files.readString(ROOT.resolve(relativePath)).trim();
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to read text: " + relativePath, ex);
        }
    }
}
