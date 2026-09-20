package com.ophelia.modelbridge;

public enum ModelTurnEventType {
    INPUT,
    STEERING,
    TOOL_CALL_STARTED,
    TOOL_CALL_COMPLETED,
    TOOL_CALL_FAILED,
    CONFIGURATION_UPDATE,
    MODEL_OUTPUT,
    CANCELLED
}
