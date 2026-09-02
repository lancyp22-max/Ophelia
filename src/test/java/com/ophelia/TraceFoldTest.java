package com.ophelia;

import com.ophelia.trace.TraceFold;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class TraceFoldTest {

    private final TraceFold fold = new TraceFold();

    private List<TraceFold.Event> sampleEvents() {
        return List.of(
                new TraceFold.Event("evt-01", 10, "task", "task.status", "queued"),
                new TraceFold.Event("evt-02", 20, "observer", "observer.note", "handoff-ready"),
                new TraceFold.Event("evt-03", 30, "task", "task.status", "running")
        );
    }

    @Test
    void rebuildFromSameLogIsDeterministicAcrossInputOrder() {
        TraceFold.ViewSpec spec = new TraceFold.ViewSpec("audit", Set.of());

        TraceFold.Projection forward = fold.fold(sampleEvents(), spec);
        TraceFold.Projection reordered = fold.fold(
                List.of(sampleEvents().get(2), sampleEvents().get(0), sampleEvents().get(1)),
                spec
        );

        assertEquals(forward, reordered);
        assertEquals(TraceFold.Coverage.COMPLETE, forward.coverage());
        assertEquals(0, forward.omittedEventCount());
    }

    @Test
    void consumerViewReportsOmissionsInsteadOfPretendingToBeComplete() {
        TraceFold.ViewSpec spec = new TraceFold.ViewSpec("agent-task-view", Set.of("task"));

        TraceFold.Projection projection = fold.fold(sampleEvents(), spec);

        assertEquals(TraceFold.Coverage.PARTIAL, projection.coverage());
        assertEquals(1, projection.omittedEventCount());
        assertEquals(List.of("evt-01", "evt-02", "evt-03"), projection.sourceEventIds());
        assertEquals(List.of("evt-01", "evt-03"), projection.contributingEventIds());
        assertEquals(Map.of("task.status", "running"), projection.state());
    }

    @Test
    void incrementalReplayMatchesBatchProjection() {
        TraceFold.ViewSpec spec = new TraceFold.ViewSpec("handoff", Set.of("task", "observer"));

        TraceFold.Accumulator accumulator = fold.accumulator(spec);
        for (TraceFold.Event event : sampleEvents()) {
            accumulator.accept(event);
        }

        assertEquals(fold.fold(sampleEvents(), spec), accumulator.snapshot());
    }

    @Test
    void incrementalReplayRejectsReorderingAndDuplicatePosition() {
        TraceFold.Accumulator accumulator =
                fold.accumulator(new TraceFold.ViewSpec("audit", Set.of()));

        accumulator.accept(new TraceFold.Event("evt-b", 20, "task", "x", "1"));

        assertThrows(
                IllegalArgumentException.class,
                () -> accumulator.accept(new TraceFold.Event("evt-a", 10, "task", "x", "2"))
        );
        assertThrows(
                IllegalArgumentException.class,
                () -> accumulator.accept(new TraceFold.Event("evt-b", 20, "task", "x", "3"))
        );
    }

    @Test
    void rawEventChangeChangesSourceAndProjectionHashes() {
        TraceFold.ViewSpec spec = new TraceFold.ViewSpec("audit", Set.of());

        TraceFold.Projection original = fold.fold(sampleEvents(), spec);
        TraceFold.Projection changed = fold.fold(
                List.of(
                        sampleEvents().get(0),
                        sampleEvents().get(1),
                        new TraceFold.Event("evt-03", 30, "task", "task.status", "failed")
                ),
                spec
        );

        assertNotEquals(original.sourceRootHash(), changed.sourceRootHash());
        assertNotEquals(original.projectionHash(), changed.projectionHash());
    }

    @Test
    void projectionStateAndLineageAreImmutable() {
        TraceFold.Projection projection =
                fold.fold(sampleEvents(), new TraceFold.ViewSpec("audit", Set.of()));

        assertThrows(
                UnsupportedOperationException.class,
                () -> projection.state().put("task.status", "forged")
        );
        assertThrows(
                UnsupportedOperationException.class,
                () -> projection.sourceEventIds().add("forged-event")
        );
    }

    @Test
    void publicApiContainsProjectionOnlyNoAuthoritySurface() {
        Set<String> foldMethods = Arrays.stream(TraceFold.class.getDeclaredMethods())
                .filter(method -> Modifier.isPublic(method.getModifiers()))
                .map(Method::getName)
                .collect(Collectors.toSet());

        Set<String> accumulatorMethods = Arrays.stream(TraceFold.Accumulator.class.getDeclaredMethods())
                .filter(method -> Modifier.isPublic(method.getModifiers()))
                .map(Method::getName)
                .collect(Collectors.toSet());

        assertEquals(Set.of("fold", "accumulator"), foldMethods);
        assertEquals(Set.of("accept", "snapshot"), accumulatorMethods);
    }
}
