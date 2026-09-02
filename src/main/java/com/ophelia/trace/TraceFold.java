package com.ophelia.trace;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Deterministic, non-authoritative projection over a caller-supplied event stream.
 *
 * <p>The event stream remains the source of truth. A projection is a rebuildable
 * runtime view only: it contains no persistence, approval, promotion, or mutation
 * path into canonical memory.</p>
 */
public final class TraceFold {

    public static final String SCHEMA_VERSION = "0.1";

    public enum Coverage {
        COMPLETE,
        PARTIAL
    }

    public record Event(
            String eventId,
            long sequence,
            String type,
            String key,
            String value
    ) {
        public Event {
            requireText(eventId, "eventId");
            if (sequence < 0) {
                throw new IllegalArgumentException("sequence must be >= 0");
            }
            requireText(type, "type");
            requireText(key, "key");
            Objects.requireNonNull(value, "value");
        }
    }

    /**
     * Empty includedEventTypes means "include every event type".
     */
    public record ViewSpec(
            String viewId,
            Set<String> includedEventTypes
    ) {
        public ViewSpec {
            requireText(viewId, "viewId");
            Objects.requireNonNull(includedEventTypes, "includedEventTypes");

            TreeSet<String> normalized = new TreeSet<>();
            for (String type : includedEventTypes) {
                requireText(type, "includedEventTypes entry");
                normalized.add(type);
            }
            includedEventTypes = Collections.unmodifiableSet(normalized);
        }

        boolean accepts(String type) {
            return includedEventTypes.isEmpty() || includedEventTypes.contains(type);
        }
    }

    public record Projection(
            String schemaVersion,
            String viewId,
            List<String> sourceEventIds,
            List<String> contributingEventIds,
            String sourceRootHash,
            String projectionHash,
            Coverage coverage,
            int omittedEventCount,
            Map<String, String> state
    ) {
        public Projection {
            sourceEventIds = List.copyOf(sourceEventIds);
            contributingEventIds = List.copyOf(contributingEventIds);
            state = Collections.unmodifiableMap(new LinkedHashMap<>(state));
        }
    }

    private static final Comparator<Event> EVENT_ORDER =
            Comparator.comparingLong(Event::sequence).thenComparing(Event::eventId);

    public Projection fold(List<Event> events, ViewSpec spec) {
        Objects.requireNonNull(events, "events");
        Objects.requireNonNull(spec, "spec");

        List<Event> ordered = new ArrayList<>(events);
        if (ordered.stream().anyMatch(Objects::isNull)) {
            throw new IllegalArgumentException("events must not contain null");
        }
        ordered.sort(EVENT_ORDER);

        Accumulator accumulator = accumulator(spec);
        for (Event event : ordered) {
            accumulator.accept(event);
        }
        return accumulator.snapshot();
    }

    public Accumulator accumulator(ViewSpec spec) {
        return new Accumulator(Objects.requireNonNull(spec, "spec"));
    }

    public final class Accumulator {
        private final ViewSpec spec;
        private final Map<String, String> state = new TreeMap<>();
        private final List<String> sourceEventIds = new ArrayList<>();
        private final List<String> contributingEventIds = new ArrayList<>();
        private final StringBuilder sourceCanonical = new StringBuilder();
        private Event lastEvent;
        private int omittedEventCount;

        private Accumulator(ViewSpec spec) {
            this.spec = spec;
        }

        /**
         * Accepts events only in canonical order so incremental replay cannot hide
         * reordering. Use {@link TraceFold#fold(List, ViewSpec)} for unordered input.
         */
        public void accept(Event event) {
            Objects.requireNonNull(event, "event");

            if (lastEvent != null && EVENT_ORDER.compare(lastEvent, event) >= 0) {
                throw new IllegalArgumentException(
                        "incremental events must be strictly ordered by (sequence, eventId)"
                );
            }

            sourceEventIds.add(event.eventId());
            appendEvent(sourceCanonical, event);

            if (spec.accepts(event.type())) {
                state.put(event.key(), event.value());
                contributingEventIds.add(event.eventId());
            } else {
                omittedEventCount++;
            }

            lastEvent = event;
        }

        public Projection snapshot() {
            String sourceRootHash = sha256(sourceCanonical.toString());
            Coverage coverage = omittedEventCount == 0 ? Coverage.COMPLETE : Coverage.PARTIAL;
            String projectionHash = sha256(canonicalProjection(
                    spec,
                    sourceRootHash,
                    sourceEventIds,
                    contributingEventIds,
                    coverage,
                    omittedEventCount,
                    state
            ));

            return new Projection(
                    SCHEMA_VERSION,
                    spec.viewId(),
                    sourceEventIds,
                    contributingEventIds,
                    sourceRootHash,
                    projectionHash,
                    coverage,
                    omittedEventCount,
                    state
            );
        }
    }

    private static void appendEvent(StringBuilder target, Event event) {
        appendPart(target, Long.toString(event.sequence()));
        appendPart(target, event.eventId());
        appendPart(target, event.type());
        appendPart(target, event.key());
        appendPart(target, event.value());
    }

    private static String canonicalProjection(
            ViewSpec spec,
            String sourceRootHash,
            List<String> sourceEventIds,
            List<String> contributingEventIds,
            Coverage coverage,
            int omittedEventCount,
            Map<String, String> state
    ) {
        StringBuilder canonical = new StringBuilder();
        appendPart(canonical, SCHEMA_VERSION);
        appendPart(canonical, spec.viewId());
        appendPart(canonical, sourceRootHash);
        appendPart(canonical, coverage.name());
        appendPart(canonical, Integer.toString(omittedEventCount));

        for (String type : spec.includedEventTypes()) {
            appendPart(canonical, "type");
            appendPart(canonical, type);
        }
        for (String eventId : sourceEventIds) {
            appendPart(canonical, "source");
            appendPart(canonical, eventId);
        }
        for (String eventId : contributingEventIds) {
            appendPart(canonical, "contrib");
            appendPart(canonical, eventId);
        }
        for (Map.Entry<String, String> entry : state.entrySet()) {
            appendPart(canonical, entry.getKey());
            appendPart(canonical, entry.getValue());
        }
        return canonical.toString();
    }

    private static void appendPart(StringBuilder target, String value) {
        target.append(value.length()).append(':').append(value);
    }

    private static String sha256(String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder(bytes.length * 2);
            for (byte item : bytes) {
                hex.append(Character.forDigit((item >>> 4) & 0x0f, 16));
                hex.append(Character.forDigit(item & 0x0f, 16));
            }
            return hex.toString();
        } catch (NoSuchAlgorithmException exc) {
            throw new IllegalStateException("SHA-256 unavailable", exc);
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " must be non-blank");
        }
    }
}
