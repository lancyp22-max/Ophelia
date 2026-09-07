package com.ophelia.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ophelia.model.MemoryPalaceSnapshot;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@Service
public class MemoryPalaceService {
    private static final Path ROOT = Path.of("");
    private static final Path PALACE = ROOT.resolve("lumaria_memory_palace_v0.1.json");

    private final ObjectMapper json = new ObjectMapper().findAndRegisterModules();

    public MemoryPalaceSnapshot snapshot() {
        try {
            return json.readValue(Files.readString(PALACE), MemoryPalaceSnapshot.class);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to load memory palace: " + PALACE, ex);
        }
    }
}
