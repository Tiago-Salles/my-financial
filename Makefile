# Personal Financial Tracker - Makefile
# Usage: make <target>

.PHONY: help install setup db-start db-stop migrate superuser run test clean populate populate-minimal shell check format lint

# Default target
help:
	@echo "Personal Financial Tracker - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      - Install all dependencies"
	@echo "  setup        - Complete project setup (install + db + migrate + superuser)"
	@echo "  db-start     - Start PostgreSQL database with Docker"
	@echo "  db-stop      - Stop PostgreSQL database"
	@echo ""
	@echo "Development:"
	@echo "  run          - Start development server"
	@echo "  migrate      - Run database migrations"
	@echo "  superuser    - Create admin superuser"
	@echo "  shell        - Open Django shell"
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
PYTHON = python
MANAGE = $(PYTHON) manage.py
VENV = venv/bin/activate

# Installation
install:
	@echo "📦 Installing dependencies..."
	@bash -c "source $(VENV) && pip install -r requirements.txt"
	@echo "✅ Dependencies installed successfully"

# Database management
db-start:
	@echo "🐘 Starting PostgreSQL database..."
	@docker compose up -d db
	@echo "✅ Database started successfully"

db-stop:
	@echo "🐘 Stopping PostgreSQL database..."
	@docker compose down
	@echo "✅ Database stopped successfully"

# Django management
migrate:
	@echo "🔄 Running database migrations..."
	@bash -c "source $(VENV) && $(MANAGE) migrate"
	@echo "✅ Migrations completed successfully"

superuser:
	@echo "👤 Creating superuser..."
	@bash -c "source $(VENV) && $(MANAGE) createsuperuser --username admin --email admin@example.com --noinput"
	@bash -c "source $(VENV) && $(MANAGE) shell -c \"from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin'); u.save(); print('Password set to: admin')\""
	@echo "✅ Superuser created: admin/admin"

run:
	@echo "🚀 Starting development server..."
	@bash -c "source $(VENV) && $(MANAGE) runserver"

shell:
	@echo "🐍 Opening Django shell..."
	@bash -c "source $(VENV) && $(MANAGE) shell"

check:
	@echo "🔍 Running system checks..."
	@bash -c "source $(VENV) && $(MANAGE) check"

# Data management
populate:
	@echo "📊 Populating database with realistic data..."
	@bash -c "source $(VENV) && $(PYTHON) populate_data.py"
	@echo "✅ Data population completed"

populate-minimal:
	@echo "🔧 Populating database with minimal test data..."
	@bash -c "source $(VENV) && $(PYTHON) populate_data.py --minimal"
	@echo "✅ Minimal data population completed"

clean:
	@echo "🗑️  Clearing all data..."
	@bash -c "source $(VENV) && $(MANAGE) shell -c \"from finance.models import *; VariablePayment.objects.all().delete(); FixedPayment.objects.all().delete(); ExchangeRate.objects.all().delete(); CreditCard.objects.all().delete(); UserFinancialProfile.objects.all().delete(); print('All data cleared')\""
	@echo "✅ Database cleared successfully"

# Complete setup
setup: install db-start migrate superuser
	@echo ""
	@echo "🎉 Setup completed successfully!"
	@echo "🌐 Access the application at: http://127.0.0.1:8000/admin/"
	@echo "👤 Login with: admin/admin"
	@echo ""
	@echo "Next steps:"
	@echo "  make run          - Start the development server"
	@echo "  make populate     - Add sample data"
	@echo "  make help         - Show all available commands"

# Code quality
format:
	@echo "🎨 Formatting code..."
	@bash -c "source $(VENV) && black ."
	@echo "✅ Code formatted successfully"

lint:
	@echo "🔍 Running linting checks..."
	@bash -c "source $(VENV) && flake8 ."
	@echo "✅ Linting completed"

# Database backup/restore
backup:
	@echo "💾 Creating database backup..."
	@pg_dump -h localhost -U my_financial_user my_financial_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created successfully"

restore:
	@echo "📥 Restoring database from backup..."
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore file=backup_file.sql"; \
		exit 1; \
	fi
	@psql -h localhost -U my_financial_user my_financial_db < $(file)
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
	@echo "  Migrations: $$(bash -c \"source $(VENV) && $(MANAGE) showmigrations | grep -c '\[X\]'\" 2>/dev/null || echo '0')/$$(bash -c \"source $(VENV) && $(MANAGE) showmigrations | grep -c '\[ \]'\" 2>/dev/null || echo '0') applied"
	@echo "  Records:"
	@bash -c "source $(VENV) && $(MANAGE) shell -c \"from finance.models import *; print('    User Profiles:', UserFinancialProfile.objects.count()); print('    Credit Cards:', CreditCard.objects.count()); print('    Exchange Rates:', ExchangeRate.objects.count()); print('    Fixed Payments:', FixedPayment.objects.count()); print('    Variable Payments:', VariablePayment.objects.count())\""

logs:
	@echo "📋 Database logs:"
	@docker compose logs db

reset: clean populate
	@echo "🔄 Database reset with fresh sample data"

# Quick development workflow
quick: db-start migrate run
	@echo "⚡ Quick start completed - server running at http://127.0.0.1:8000/" 