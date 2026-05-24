.PHONY: preview preview-mobile preview-all mirror10-demo backend-build backend-run ci-check repo-link-check public-leak-guard install-hooks public-shell public-shell-audit

preview:
	python3 scripts/capture_preview.py --output artifacts/preview-desktop.txt

preview-mobile:
	python3 scripts/capture_preview.py --width 390 --height 844 --output artifacts/preview-mobile.txt

preview-all: preview preview-mobile

mirror10-demo:
	python3 -m http.server 8010

backend-build:
	mvn -B -ntp verify

backend-run:
	mvn -q spring-boot:run

repo-link-check:
	bash scripts/verify_repo_links.sh

public-leak-guard:
	bash scripts/public_leak_guard.sh

install-hooks:
	bash scripts/install_git_hooks.sh

public-shell:
	bash scripts/build_public_shell.sh

public-shell-audit: public-shell
	bash scripts/public_shell_audit.sh

ci-check: repo-link-check public-leak-guard
	node --check script.js
	python3 scripts/capture_preview.py --dry-run
	mvn -B -ntp verify
