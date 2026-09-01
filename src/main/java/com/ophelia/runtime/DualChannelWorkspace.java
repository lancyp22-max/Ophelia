package com.ophelia.runtime;

import java.util.Collections;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * In-memory copy-on-write comparison workspace.
 *
 * <p>This class deliberately has no live actuator and no commit/apply/promote
 * operation. It may stage and compare candidate state only. Consequential
 * mutation remains outside this component and behind the existing authority
 * gate.</p>
 */
public final class DualChannelWorkspace {

    public enum Channel {
        PRIMARY,
        SHADOW
    }

    public enum Relation {
        MATCH,
        DIVERGED,
        ONLY_PRIMARY_CHANGED,
        ONLY_SHADOW_CHANGED
    }

    public record DiffEntry(
            String key,
            String baseValue,
            String primaryValue,
            String shadowValue,
            Relation relation
    ) {}

    private final Map<String, String> base;
    private final EnumMap<Channel, Map<String, String>> overlays = new EnumMap<>(Channel.class);

    public DualChannelWorkspace(Map<String, String> baseSnapshot) {
        Objects.requireNonNull(baseSnapshot, "baseSnapshot");
        this.base = Collections.unmodifiableMap(new LinkedHashMap<>(baseSnapshot));
        overlays.put(Channel.PRIMARY, new LinkedHashMap<>());
        overlays.put(Channel.SHADOW, new LinkedHashMap<>());
    }

    public Map<String, String> baseSnapshot() {
        return base;
    }

    public void stage(Channel channel, String key, String value) {
        Objects.requireNonNull(channel, "channel");
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("key must be non-blank");
        }
        overlays.get(channel).put(key, value);
    }

    public String read(Channel channel, String key) {
        Objects.requireNonNull(channel, "channel");
        Objects.requireNonNull(key, "key");
        Map<String, String> overlay = overlays.get(channel);
        return overlay.containsKey(key) ? overlay.get(key) : base.get(key);
    }

    public Map<String, String> delta(Channel channel) {
        Objects.requireNonNull(channel, "channel");
        return Collections.unmodifiableMap(new LinkedHashMap<>(overlays.get(channel)));
    }

    public Map<String, DiffEntry> compareChangedKeys() {
        Set<String> keys = new LinkedHashSet<>();
        keys.addAll(overlays.get(Channel.PRIMARY).keySet());
        keys.addAll(overlays.get(Channel.SHADOW).keySet());

        Map<String, DiffEntry> result = new LinkedHashMap<>();
        for (String key : keys) {
            String baseValue = base.get(key);
            String primaryValue = read(Channel.PRIMARY, key);
            String shadowValue = read(Channel.SHADOW, key);

            boolean primaryChanged = !Objects.equals(primaryValue, baseValue);
            boolean shadowChanged = !Objects.equals(shadowValue, baseValue);

            Relation relation;
            if (Objects.equals(primaryValue, shadowValue)) {
                relation = Relation.MATCH;
            } else if (primaryChanged && shadowChanged) {
                relation = Relation.DIVERGED;
            } else if (primaryChanged) {
                relation = Relation.ONLY_PRIMARY_CHANGED;
            } else {
                relation = Relation.ONLY_SHADOW_CHANGED;
            }

            result.put(key, new DiffEntry(
                    key,
                    baseValue,
                    primaryValue,
                    shadowValue,
                    relation
            ));
        }
        return Collections.unmodifiableMap(result);
    }

    public void clear(Channel channel) {
        Objects.requireNonNull(channel, "channel");
        overlays.get(channel).clear();
    }

    public void clearAll() {
        overlays.values().forEach(Map::clear);
    }
}
