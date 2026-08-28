# Ophelia: Sovereign Local-First Multi-Agent OS

Ophelia is a **Sovereign, Local-First Multi-Agent Operating System (OS)** designed to orchestrate complex workflows, manage strict hardware handovers, and execute autonomous browser and system actuation. 

It is built on a hybrid architecture: core structural memory and operational states remain completely localized on the user's hardware to guarantee sovereignty and security, while cloud-based LLMs are utilized strictly as stateless "external consultants" for heavy reasoning and refinement.

## ⚠️ The Problem: Where Standard Architectures Fail

Current enterprise AI and autonomous agent frameworks typically fail in three distinct ways:

1. **The Cloud Privacy Leak:** Fully cloud-based agentic systems require businesses to upload proprietary, sensitive workflow data to centralized servers, risking catastrophic data leaks and violating privacy guardrails.
2. **The Local Hardware Bottleneck:** Running capable multi-agent arrays locally on consumer hardware usually results in VRAM crashes, silent truncations, and Out-Of-Memory (OOM) errors as models compete for limited GPU resources.
3. **The Flat UI Context Loss:** Traditional dashboards and text-based chat interfaces are rigid and fail to accurately map the state of complex, multi-layered workflows, making it impossible for operators and agents to share a cohesive mental model.

## ⚙️ The Solution: How Ophelia Works

Ophelia solves these constraints through a meticulously engineered local orchestration layer designed for **Resonance over Extraction**:

* **Sequential VRAM Handovers (The Forge):** Ophelia safely juggles multiple models (e.g., a 4B parameter coder and a 9B parameter QA manager) on standard consumer hardware. It utilizes strict memory ejection (`keep_alive: 0`) and 500ms driver-settle windows to ensure Model A is 100% purged from VRAM before Model B spins up. 
* **Autonomous Actuation:** The system includes a dedicated `browser_agent` capable of taking over the viewport to navigate, click, fill forms, and execute complex workflows directly on the user's screen.
* **Prompt-Driven UI Generation:** The front-end interface is not static. It is a highly fluid, CSS-variable-driven shell that can be fully customized with a few prompts to match whatever enterprise, aesthetic, or operational domain you require. 

## 🌌 The Spatial Sandbox (Three.js 3D Environment)

Rather than forcing the AI and the user to rely purely on text logs, Ophelia integrates a live **Three.js 3D Sandbox Environment**. 

This serves as a visual staging ground where operational logic, UI states, and workflow variables can be mapped into physical space. It gives both the human operator and the local agents a robust, interactive environment to simulate ideas, test causal links, and "play out" consequences safely before pushing code or decisions into production.

## 🛡️ Public Exposure Guardrails & Security

Ophelia utilizes a strict **Split Architecture Guardrail** to ensure that local power never results in public vulnerability. 

* **Stateful Local Memory:** All living memory, spatial states, and configuration ledgers remain strictly on the local machine. 
* **Public Shell Automation:** Built-in CI scripts (`scripts/public_leak_guard.sh`), regex allowlists, and pre-commit hooks ensure that keys, credentials, and sealed architectural paths are hard-blocked from ever reaching the public repository surface.
* **Stewardship Gates:** No consequential state mutations occur without surfaced human confirmation (NE-000 Authority Check).

## 🚀 Quick Start & Demos

Ophelia is in active development. You can run the local demos to explore the UI states and spatial sandbox:

```bash
# Run the Three.js Spatial Sandbox
make mirror10-demo 

# Build the curated, leak-proof public shell
make public-shell
```
