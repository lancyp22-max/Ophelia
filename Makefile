.PHONY: policy-maturity-check preview preview-mobile preview-all mirror10-demo context-brief world-model-packet task-guideposts task-guidepost-check scene-action-bus-check dual-channel-check shadow-sandbox-probe canon-receipt-check agent-work-observability-check friction-ledger-check friction-ledger-summary repo-audit-window semantic-packet-check semantic-packet-benchmark kernel-check actions-runtime-check world-module-check decision-boundary-check correction-ledger-check backend-build backend-run ci-check repo-link-check public-leak-guard public-leak-guard-test install-hooks public-shell public-shell-audit

preview:
	python3 scripts/capture_preview.py --output artifacts/preview-desktop.txt

preview-mobile:
	python3 scripts/capture_preview.py --width 390 --height 844 --output artifacts/preview-mobile.txt

preview-all: preview preview-mobile

mirror10-demo:
	python3 -m http.server 8010

context-brief:
	python3 scripts/context_brief.py

world-model-packet:
	python3 scripts/world_model_packet.py

task-guideposts:
	@test -n "$(TASK)" || (echo 'usage: make task-guideposts TASK="describe the current task"' && exit 2)
	python3 scripts/task_guidepost_scan.py --task "$(TASK)"

task-guidepost-check:
	python3 scripts/task_guidepost_scan.py --check

scene-action-bus-check:
	python3 scripts/check_scene_action_bus.py

dual-channel-check:
	python3 scripts/check_dual_channel.py

policy-maturity-check:
	python3 scripts/check_policy_maturity.py

shadow-sandbox-probe:
	bash scripts/probe_shadow_sandbox.sh

canon-receipt-check:
	python3 scripts/check_canon_receipt.py

agent-work-observability-check:
	python3 scripts/check_agent_work_observability.py

friction-ledger-check:
	python3 scripts/friction_ledger.py --check

friction-ledger-summary:
	python3 scripts/friction_ledger.py --summary

repo-audit-window:
	python3 scripts/repo_audit_window.py --hours "$(or $(HOURS),24)" $(if $(END),--end "$(END)",)

semantic-packet-check:
	python3 scripts/semantic_packet.py --check

semantic-packet-benchmark:
	python3 scripts/semantic_packet.py --benchmark

kernel-check:
	mvn -B -ntp -Dtest=LumariaKernelConfigTest test

actions-runtime-check:
	python3 scripts/check_github_actions_runtime.py

world-module-check:
	python3 scripts/check_world_module.py

decision-boundary-check:
	python3 scripts/check_decision_boundaries.py

correction-ledger-check:
	python3 scripts/check_correction_ledger.py

backend-build:
	mvn -B -ntp verify

backend-run:
	mvn -q spring-boot:run

repo-link-check:
	bash scripts/verify_repo_links.sh

public-leak-guard:
	bash scripts/public_leak_guard.sh

public-leak-guard-test:
	bash scripts/test_public_leak_guard.sh

install-hooks:
	bash scripts/install_git_hooks.sh

public-shell:
	bash scripts/build_public_shell.sh

public-shell-audit: public-shell
	bash scripts/public_shell_audit.sh

ci-check: repo-link-check public-leak-guard
	bash scripts/test_public_leak_guard.sh
	node --check script.js
	python3 scripts/check_world_module.py
	python3 scripts/check_decision_boundaries.py
	python3 scripts/check_correction_ledger.py
	python3 scripts/task_guidepost_scan.py --check
	python3 scripts/check_scene_action_bus.py
	python3 scripts/check_dual_channel.py
	python3 scripts/check_policy_maturity.py
	python3 scripts/check_canon_receipt.py
	python3 scripts/check_agent_work_observability.py
	python3 scripts/friction_ledger.py --check
	python3 scripts/repo_audit_window.py --hours 24 --end 2026-08-24T18:01:00Z --check >/dev/null
	python3 scripts/semantic_packet.py --check
	python3 scripts/check_github_actions_runtime.py
	python3 scripts/capture_preview.py --dry-run
	mvn -B -ntp verify
