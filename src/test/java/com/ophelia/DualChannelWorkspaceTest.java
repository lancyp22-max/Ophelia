package com.ophelia;

import com.ophelia.runtime.DualChannelWorkspace;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DualChannelWorkspaceTest {

    @Test
    void stagesCopyOnWriteWithoutMutatingSharedBase() {
        DualChannelWorkspace workspace = new DualChannelWorkspace(Map.of(
                "garden.mode", "calm",
                "forge.light", "idle"
        ));

        workspace.stage(DualChannelWorkspace.Channel.PRIMARY, "garden.mode", "rain");
        workspace.stage(DualChannelWorkspace.Channel.SHADOW, "forge.light", "warm");

        assertEquals("calm", workspace.baseSnapshot().get("garden.mode"));
        assertEquals("idle", workspace.baseSnapshot().get("forge.light"));

        assertEquals("rain", workspace.read(DualChannelWorkspace.Channel.PRIMARY, "garden.mode"));
        assertEquals("calm", workspace.read(DualChannelWorkspace.Channel.SHADOW, "garden.mode"));
        assertEquals("idle", workspace.read(DualChannelWorkspace.Channel.PRIMARY, "forge.light"));
        assertEquals("warm", workspace.read(DualChannelWorkspace.Channel.SHADOW, "forge.light"));
    }

    @Test
    void comparisonPreservesConsensusAndDivergenceAsEvidenceOnly() {
        DualChannelWorkspace workspace = new DualChannelWorkspace(Map.of("bridge.state", "idle"));

        workspace.stage(DualChannelWorkspace.Channel.PRIMARY, "bridge.state", "active");
        workspace.stage(DualChannelWorkspace.Channel.SHADOW, "bridge.state", "active");
        assertEquals(
                DualChannelWorkspace.Relation.MATCH,
                workspace.compareChangedKeys().get("bridge.state").relation()
        );

        workspace.stage(DualChannelWorkspace.Channel.SHADOW, "bridge.state", "inspect");
        assertEquals(
                DualChannelWorkspace.Relation.DIVERGED,
                workspace.compareChangedKeys().get("bridge.state").relation()
        );
    }

    @Test
    void canStageProtectedIdeasWithoutCreatingACommitPath() {
        DualChannelWorkspace workspace = new DualChannelWorkspace(Map.of("authority.mode", "human_gate"));

        workspace.stage(DualChannelWorkspace.Channel.SHADOW, "authority.mode", "candidate_only");

        assertEquals("human_gate", workspace.baseSnapshot().get("authority.mode"));
        assertEquals("candidate_only", workspace.read(DualChannelWorkspace.Channel.SHADOW, "authority.mode"));
    }

    @Test
    void baseSnapshotIsImmutable() {
        DualChannelWorkspace workspace = new DualChannelWorkspace(Map.of("x", "1"));
        assertThrows(UnsupportedOperationException.class, () -> workspace.baseSnapshot().put("x", "2"));
    }

    @Test
    void exposesNoPublicAuthorityOrExecutionMethod() {
        Set<String> forbidden = Set.of("commit", "apply", "promote", "execute", "mutate", "persist");
        Set<String> publicMethods = Arrays.stream(DualChannelWorkspace.class.getDeclaredMethods())
                .filter(method -> Modifier.isPublic(method.getModifiers()))
                .map(Method::getName)
                .map(String::toLowerCase)
                .collect(Collectors.toSet());

        assertFalse(publicMethods.stream().anyMatch(forbidden::contains));
        assertNull(workspaceMethod(publicMethods, "commit"));
    }

    private static String workspaceMethod(Set<String> methods, String name) {
        return methods.contains(name) ? name : null;
    }
}
