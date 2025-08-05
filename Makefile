# Personal Financial Tracker - Makefile
# Usage: make <target>

.PHONY: help install setup db-start db-stop app-up migrate superuser run test clean populate populate-minimal shell check format lint backup restore status logs reset quick

# Default target
help:
	@echo "Personal Financial Tracker - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      - Build the Docker app image"
	@echo "  setup        - Start services, run migrations and create the admin user"
	@echo "  db-start     - Start the PostgreSQL container"
	@echo "  db-stop      - Stop and remove containers"
	@echo ""
	@echo "Development:"
	@echo "  run          - Start the application container"
	@echo "  migrate      - Run database migrations"
	@echo "  superuser    - Create admin superuser"
	@echo "  shell        - Open Django shell in the app container"
	@echo "  check        - Run Django system checks"
	@echo ""
	@echo "Data Management:"
	@echo "  populate     - Populate database with realistic sample data"
	@echo "  populate-minimal - Populate database with minimal test data"
	@echo "  clean        - Clear all data from database"
	@echo ""
	@echo "Code Quality:"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run linting checks"
	@echo ""
	@echo "Database:"
	@echo "  backup       - Create database backup"
	@echo "  restore      - Restore database from backup"

# Variables
COMPOSE = docker compose
APP_SERVICE = app
DB_SERVICE = db

# Installation
install:
	@echo "📦 Building Docker app image..."
	@$(COMPOSE) build $(APP_SERVICE)
	@echo "✅ Docker image built successfully"

# Database management
db-start:
	@echo "🐘 Starting PostgreSQL container..."
	@$(COMPOSE) up -d $(DB_SERVICE)
	@echo "✅ Database container started"

db-stop:
	@echo "🐘 Stopping containers..."
	@$(COMPOSE) down
	@echo "✅ Containers stopped"

app-up:
	@echo "🚀 Starting application container..."
	@$(COMPOSE) up -d --build $(APP_SERVICE)

# Django management
migrate:
	@echo "🔄 Running database migrations..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python manage.py migrate
	@echo "✅ Migrations completed successfully"

superuser:
	@echo "👤 Creating superuser..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
	@$(COMPOSE) exec -T $(APP_SERVICE) python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin'); u.save(); print('Password set to: admin')"
	@echo "✅ Superuser created: admin/admin"

run:
	@echo "🚀 Starting application container in the foreground..."
	@$(COMPOSE) up --build $(APP_SERVICE)

shell:
	@echo "🐍 Opening Django shell..."
	@$(COMPOSE) exec $(APP_SERVICE) python manage.py shell

check:
	@echo "🔍 Running system checks..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python manage.py check

# Data management
populate:
	@echo "📊 Populating database with realistic data..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python populate_data.py
	@echo "✅ Data population completed"

populate-minimal:
	@echo "🔧 Populating database with minimal test data..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python populate_data.py --minimal
	@echo "✅ Minimal data population completed"

clean:
	@echo "🗑️  Clearing all data..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python manage.py shell -c "from finance.models import *; VariablePayment.objects.all().delete(); FixedPayment.objects.all().delete(); ExchangeRate.objects.all().delete(); CreditCard.objects.all().delete(); UserFinancialProfile.objects.all().delete(); print('All data cleared')"
	@echo "✅ Database cleared successfully"

# Complete setup
setup: install app-up migrate superuser
	@echo ""
	@echo "🎉 Setup completed successfully!"
	@echo "🌐 Access the application at: http://127.0.0.1:8000/"
	@echo "👤 Login with: admin/admin"
	@echo ""
	@echo "Next steps:"
	@echo "  make run          - Keep the app running in the foreground"
	@echo "  make populate     - Add sample data"
	@echo "  make help         - Show all available commands"

# Code quality
format:
	@echo "🎨 Formatting code..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python -m black .
	@echo "✅ Code formatted successfully"

lint:
	@echo "🔍 Running linting checks..."
	@$(COMPOSE) exec -T $(APP_SERVICE) python -m flake8 .
	@echo "✅ Linting completed"

# Database backup/restore
backup:
	@echo "💾 Creating database backup..."
	@docker compose exec -T db pg_dump -U my_financial_user my_financial_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created successfully"

restore:
	@echo "📥 Restoring database from backup..."
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore file=backup_file.sql"; \
		exit 1; \
	fi
	@docker compose exec -T -i db psql -U my_financial_user my_financial_db < $(file)
	@echo "✅ Database restored successfully"

# Development shortcuts
dev: run
	@echo "🚀 Development server started at http://127.0.0.1:8000/"

test-setup: setup populate
	@echo "🧪 Test environment ready with sample data"

# Utility commands
status:
	@echo "📊 Project Status:"
	@echo "  Database: $$(docker compose ps db | grep -q 'Up' && echo 'Running' || echo 'Stopped')"
	@echo "  Migrations: $$(docker compose exec -T app python manage.py showmigrations | grep -c '\[X\]' 2>/dev/null || echo '0')/$$(docker compose exec -T app python manage.py showmigrations | grep -c '\[ \]' 2>/dev/null || echo '0') applied"
	@echo "  Records:"
	@docker compose exec -T app python manage.py shell -c "from finance.models import *; print('    User Profiles:', UserFinancialProfile.objects.count()); print('    Credit Cards:', CreditCard.objects.count()); print('    Exchange Rates:', ExchangeRate.objects.count()); print('    Fixed Payments:', FixedPayment.objects.count()); print('    Variable Payments:', VariablePayment.objects.count())"

logs:
	@echo "📋 Container logs:"
	@docker compose logs db app

reset: clean populate
	@echo "🔄 Database reset with fresh sample data"

# Quick development workflow
quick: app-up migrate run
	@echo "⚡ Quick start completed - server running at http://127.0.0.1:8000/"
