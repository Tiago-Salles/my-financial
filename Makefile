# Personal Financial Tracker - Makefile
# Every target runs through docker compose. Usage: make <target> [ARGS="..."]

SHELL := /bin/bash
.DEFAULT_GOAL := help

# --- Configuration ---------------------------------------------------------
COMPOSE      ?= docker compose
APP          ?= app
DB           ?= db
NGINX        ?= nginx
SERVICE      ?=
ARGS         ?=
BACKUP_DIR   ?= backups

# Pull DB credentials (and everything else) from .env when it exists so the
# Makefile never hardcodes values that already live in one place.
ifneq (,$(wildcard .env))
include .env
export
endif

DB_NAME ?= my_financial_db
DB_USER ?= my_financial_user

# Run a command in the app service: exec into it when it is up, otherwise spin
# up a throwaway container so targets like `make test` work with nothing running.
# Used as a recipe prefix:  $(IN_APP) python manage.py migrate
IN_APP = @if [ -n "$$($(COMPOSE) ps -q --status running $(APP) 2>/dev/null)" ]; then \
		set -- exec -T; \
	else \
		echo "ℹ️  $(APP) is not running - using a one-off container"; \
		set -- run --rm; \
	fi; $(COMPOSE) "$$@" $(APP)

MANAGE = python manage.py

# --- Help ------------------------------------------------------------------
.PHONY: help
help: ## Show this help
	@echo "Personal Financial Tracker - docker compose targets"
	@echo ""
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make up                        # start the whole stack"
	@echo "  make logs SERVICE=app          # follow one service"
	@echo "  make manage ARGS=\"showmigrations\""
	@echo "  make test ARGS=\"finance.tests.test_models\""
	@echo "  make restore file=backups/backup_20250101_120000.sql"

# --- Environment -----------------------------------------------------------
.PHONY: env
env: ## Create .env from env.example if missing
	@if [ -f .env ]; then \
		echo "✅ .env already exists"; \
	else \
		cp env.example .env; \
		echo "✅ .env created from env.example - review the values"; \
	fi

.PHONY: config
config: ## Render the resolved compose configuration
	@$(COMPOSE) config

# --- Stack lifecycle -------------------------------------------------------
.PHONY: build
build: ## Build images (SERVICE=app to limit)
	@echo "📦 Building images..."
	@$(COMPOSE) build $(SERVICE)
	@echo "✅ Build complete"

.PHONY: pull
pull: ## Pull upstream images
	@$(COMPOSE) pull $(SERVICE)

.PHONY: up
up: env ## Start the stack in the background
	@echo "🚀 Starting services..."
	@$(COMPOSE) up -d $(SERVICE)
	@echo "✅ Services started"

.PHONY: up-build
up-build: env ## Rebuild and start the stack in the background
	@$(COMPOSE) up -d --build $(SERVICE)

.PHONY: run
run: env ## Start the stack in the foreground (Ctrl-C to stop)
	@$(COMPOSE) up --build $(SERVICE)

.PHONY: down
down: ## Stop and remove containers
	@echo "🛑 Stopping services..."
	@$(COMPOSE) down
	@echo "✅ Services stopped"

.PHONY: down-volumes
down-volumes: ## Stop containers and DELETE volumes (destroys the database)
	@echo "⚠️  This removes the postgres volume."
	@read -p "Type 'yes' to continue: " ans; [ "$$ans" = "yes" ] || { echo "Aborted"; exit 1; }
	@$(COMPOSE) down -v
	@echo "✅ Containers and volumes removed"

.PHONY: stop start restart
stop: ## Stop containers without removing them
	@$(COMPOSE) stop $(SERVICE)

start: ## Start previously stopped containers
	@$(COMPOSE) start $(SERVICE)

restart: ## Restart services
	@$(COMPOSE) restart $(SERVICE)

.PHONY: ps
ps: ## Show container status
	@$(COMPOSE) ps

.PHONY: logs
logs: ## Follow logs (SERVICE=app to limit)
	@$(COMPOSE) logs -f --tail=100 $(SERVICE)

.PHONY: sh
sh: ## Open a shell in the app container
	@$(COMPOSE) exec $(APP) bash || $(COMPOSE) exec $(APP) sh

.PHONY: db-shell
db-shell: ## Open psql in the database container
	@$(COMPOSE) exec $(DB) psql -U $(DB_USER) -d $(DB_NAME)

.PHONY: nginx-reload
nginx-reload: ## Reload the nginx configuration
	@$(COMPOSE) exec $(NGINX) nginx -s reload
	@echo "✅ nginx reloaded"

# --- Database readiness ----------------------------------------------------
.PHONY: db-up wait-db
db-up: ## Start only the database service
	@$(COMPOSE) up -d $(DB)

wait-db: db-up ## Block until postgres accepts connections
	@echo "⏳ Waiting for postgres..."
	@for i in $$(seq 1 60); do \
		if $(COMPOSE) exec -T $(DB) pg_isready -U $(DB_USER) -d $(DB_NAME) >/dev/null 2>&1; then \
			echo "✅ Database ready"; exit 0; \
		fi; \
		sleep 1; \
	done; \
	echo "❌ Database not ready after 60s"; exit 1

# --- Django ----------------------------------------------------------------
.PHONY: manage
manage: ## Run any manage.py command: make manage ARGS="showmigrations"
	$(IN_APP) $(MANAGE) $(ARGS)

.PHONY: migrate
migrate: wait-db ## Apply database migrations
	@echo "🔄 Applying migrations..."
	$(IN_APP) $(MANAGE) migrate
	@echo "✅ Migrations applied"

.PHONY: makemigrations
makemigrations: ## Create new migrations
	$(IN_APP) $(MANAGE) makemigrations $(ARGS)

.PHONY: superuser
superuser: ## Create the admin/admin superuser (idempotent)
	@echo "👤 Ensuring superuser exists..."
	$(IN_APP) $(MANAGE) shell -c "from django.contrib.auth.models import User; u, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'}); u.is_staff = u.is_superuser = True; u.set_password('admin'); u.save(); print('superuser ready: admin/admin')"

.PHONY: shell
shell: ## Open the Django shell
	@$(COMPOSE) exec $(APP) $(MANAGE) shell

.PHONY: check
check: ## Run Django system checks
	$(IN_APP) $(MANAGE) check

.PHONY: collectstatic
collectstatic: ## Collect static files
	$(IN_APP) $(MANAGE) collectstatic --noinput

.PHONY: test
test: wait-db ## Run the test suite (ARGS to target specific tests)
	@echo "🧪 Running tests..."
	$(IN_APP) $(MANAGE) test $(ARGS)

# --- Setup workflows -------------------------------------------------------
.PHONY: setup
setup: env build up wait-db migrate superuser ## Full first-time setup
	@echo ""
	@echo "🎉 Setup complete"
	@echo "🌐 App:   http://127.0.0.1:8000/"
	@echo "🌐 Nginx: http://127.0.0.1/"
	@echo "👤 Login: admin/admin"
	@echo ""
	@echo "Next: make populate | make logs | make help"

.PHONY: dev
dev: up wait-db migrate ## Start the stack and follow app logs
	@$(COMPOSE) logs -f $(APP)

.PHONY: rebuild
rebuild: ## Rebuild images from scratch and restart
	@$(COMPOSE) build --no-cache $(SERVICE)
	@$(COMPOSE) up -d $(SERVICE)

# --- Data ------------------------------------------------------------------
.PHONY: populate
populate: ## Populate the database with realistic sample data
	$(IN_APP) python populate_data.py

.PHONY: populate-minimal
populate-minimal: ## Populate the database with minimal test data
	$(IN_APP) python populate_data.py --minimal

.PHONY: clean-data
clean-data: ## Delete all finance records (keeps schema and users)
	@echo "⚠️  This deletes all finance records."
	@read -p "Type 'yes' to continue: " ans; [ "$$ans" = "yes" ] || { echo "Aborted"; exit 1; }
	$(IN_APP) $(MANAGE) shell -c "from finance.models import *; VariablePayment.objects.all().delete(); FixedPayment.objects.all().delete(); ExchangeRate.objects.all().delete(); CreditCard.objects.all().delete(); UserFinancialProfile.objects.all().delete(); print('All data cleared')"

.PHONY: reset
reset: clean-data populate ## Wipe data and repopulate

.PHONY: reset-db
reset-db: down-volumes up wait-db migrate superuser ## Destroy the volume and rebuild the database

# --- Code quality ----------------------------------------------------------
.PHONY: format
format: ## Format code with black
	$(IN_APP) python -m black .

.PHONY: lint
lint: ## Lint with flake8
	$(IN_APP) python -m flake8 .

# --- Backup / restore ------------------------------------------------------
.PHONY: backup
backup: ## Dump the database to backups/
	@mkdir -p $(BACKUP_DIR)
	@f=$(BACKUP_DIR)/backup_$$(date +%Y%m%d_%H%M%S).sql; \
	$(COMPOSE) exec -T $(DB) pg_dump -U $(DB_USER) $(DB_NAME) > $$f && \
	echo "✅ Backup written to $$f"

.PHONY: restore
restore: ## Restore from a dump: make restore file=backups/<file>.sql
	@if [ -z "$(file)" ]; then echo "Usage: make restore file=backups/backup_*.sql"; exit 1; fi
	@if [ ! -f "$(file)" ]; then echo "❌ No such file: $(file)"; exit 1; fi
	@$(COMPOSE) exec -T $(DB) psql -U $(DB_USER) -d $(DB_NAME) < $(file)
	@echo "✅ Restored from $(file)"

# --- Status ----------------------------------------------------------------
.PHONY: status
status: ## Show container status, migrations and record counts
	@echo "📊 Services:"
	@$(COMPOSE) ps
	@if [ -z "$$($(COMPOSE) ps -q --status running $(APP) 2>/dev/null)" ]; then \
		echo ""; echo "ℹ️  $(APP) is not running - start it with 'make up' for migration and record counts"; \
		exit 0; \
	fi; \
	echo ""; echo "📊 Migrations:"; \
	$(COMPOSE) exec -T $(APP) $(MANAGE) showmigrations \
		| awk '/\[X\]/{a++} /\[ \]/{p++} END{printf "  %d applied, %d pending\n", a, p}'; \
	echo ""; echo "📊 Records:"; \
	$(COMPOSE) exec -T $(APP) $(MANAGE) shell -c "from finance.models import *; print('  User Profiles:', UserFinancialProfile.objects.count()); print('  Credit Cards:', CreditCard.objects.count()); print('  Exchange Rates:', ExchangeRate.objects.count()); print('  Fixed Payments:', FixedPayment.objects.count()); print('  Variable Payments:', VariablePayment.objects.count())"

.PHONY: prune
prune: ## Remove stopped containers, dangling images and unused build cache
	@docker system prune -f
