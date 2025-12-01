POETRY ?= poetry
RUFF ?= $(POETRY) run ruff

migrate:
	alembic upgrade head

# Run ruff linter
lint:
	@echo "Running ruff..."
	$(RUFF) check .


# Run ruff auto-fixable changes
lint-fix:
	@echo "Running ruff --fix..."
	$(RUFF) check --fix .
