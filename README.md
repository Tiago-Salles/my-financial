# Personal Financial Tracker

A comprehensive Django application for tracking personal finances across multiple countries and currencies, specifically designed for Brazilian users living in Portugal, with a complete REST API for external frontend integration.

## Features

### 🏦 Financial Profile Management
- **User Profile**: Set your base currency (BRL/EUR) and monthly income in both currencies
- **Multi-Country Support**: Track expenses in Brazil and Portugal
- **Multi-Currency Support**: Handle BRL, EUR, and USD transactions

### 💳 Credit Card Management
- **Card Information**: Store credit card details with issuer country and currency
- **Fee Tracking**: Automatic calculation of FX fees and IOF (Brazilian tax on foreign transactions)
- **Security**: Only store last 4 digits of card numbers

### 💰 Payment Tracking
- **Fixed Payments**: Recurring payments (monthly/yearly) with start/end dates
- **Variable Payments**: One-time expenses with categories and credit card linking
- **Automatic Fee Calculation**: FX fees and IOF are calculated automatically when credit cards are linked

### 💱 Exchange Rate Management
- **Rate Tracking**: Store and manage exchange rates between currencies
- **Date-based Rates**: Historical exchange rate data for accurate conversions

### 📊 Dashboard & Analytics
- **Monthly Overview**: Income, expenses, fees, and balance calculations
- **Country-wise Breakdown**: Expenses grouped by country and currency
- **Investment Recommendations**: AI-powered suggestions based on monthly balance
- **Quick Actions**: Easy access to add new entries

### 🌐 REST API
- **Complete API**: Full CRUD operations for all models
- **Authentication**: JWT and Token-based authentication systems
- **Filtering & Search**: Advanced query capabilities
- **Dashboard Data**: Financial summaries and analytics endpoints
- **CORS Support**: Configured for frontend development
- **Documentation**: Interactive Swagger/OpenAPI documentation

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- PostgreSQL 12+ (or Docker for containerized setup)
- Make (for using the Makefile commands)

### Installation

#### Option 1: Using Makefile (Recommended)

1. **Complete setup with one command**
   ```bash
   make setup
   ```
   This will:
   - Install dependencies
   - Start PostgreSQL database
   - Run migrations
   - Create admin user (admin/admin)

2. **Start the development server**
   ```bash
   make run
   ```

3. **Populate with sample data**
   ```bash
   make populate
   ```

4. **Access the application**
   - Admin Interface: http://127.0.0.1:8000/admin/
   - Swagger Documentation: http://127.0.0.1:8000/swagger/
   - ReDoc Documentation: http://127.0.0.1:8000/redoc/
   - API Documentation: http://127.0.0.1:8000/api/docs/overview/
   - Interactive API: http://127.0.0.1:8000/api/
   - Login: admin/admin

#### Option 2: Manual Setup

1. **Clone and navigate to the project**
   ```bash
   cd my-financial
   ```

2. **Start PostgreSQL database**
   ```bash
   docker compose up -d db
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your settings if needed
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

## API Integration

The application provides a comprehensive REST API for external frontend integration:

### Quick API Test

```bash
# Register a user with JWT
curl -X POST http://localhost:8000/api/auth/jwt/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Get profiles with JWT (use access token from registration)
curl -X GET http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer <your_jwt_token>"

# Or use legacy token authentication
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser2", "email": "test2@example.com", "password": "testpass123"}'

curl -X GET http://localhost:8000/api/profiles/ \
  -H "Authorization: Token <your_token>"
```

### API Features

- **Authentication**: JWT and Token-based authentication with register/login endpoints
- **CRUD Operations**: Full Create, Read, Update, Delete for all models
- **Filtering & Search**: Query parameters for filtering and searching data
- **Dashboard Data**: Endpoints for financial summaries and analytics
- **CORS Support**: Configured for frontend development servers
- **Documentation**: Interactive Swagger/OpenAPI documentation

### Available Endpoints

- **JWT Authentication**: `/api/auth/jwt/register/`, `/api/auth/jwt/login/`, `/api/auth/jwt/refresh/`
- **Legacy Token Authentication**: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/`
- **Profiles**: `/api/profiles/` - User financial profiles
- **Credit Cards**: `/api/credit-cards/` - Credit card management
- **Exchange Rates**: `/api/exchange-rates/` - Currency conversion rates
- **Fixed Payments**: `/api/fixed-payments/` - Recurring payments
- **Variable Payments**: `/api/variable-payments/` - One-time expenses
- **Dashboard**: `/api/dashboard/summary/` - Financial summaries

For complete API documentation, see [API_README.md](API_README.md).

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Admin Interface: http://127.0.0.1:8000/admin/
   - Dashboard: http://127.0.0.1:8000/admin/finance/userfinancialprofile/

#### Option 3: Local PostgreSQL

1. **Install PostgreSQL locally**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create database and user**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE my_financial_db;
   CREATE USER my_financial_user WITH PASSWORD 'my_financial_password';
   GRANT ALL PRIVILEGES ON DATABASE my_financial_db TO my_financial_user;
   \q
   ```

3. **Follow steps 1, 3-9 from Option 2**

## Quick Start with Makefile

The project includes a comprehensive Makefile for easy management:

```bash
# Show all available commands
make help

# Complete setup (recommended for first time)
make setup

# Start development server
make run

# Populate with realistic sample data
make populate

# Check project status
make status

# Clear all data
make clean

# Reset with fresh data
make reset
```

## Usage Guide

### 1. Set Up Your Profile
1. Go to **User Financial Profiles** in the admin
2. Create your profile with:
   - Your name
   - Base currency (BRL or EUR)
   - Monthly income in both currencies

### 2. Add Credit Cards
1. Go to **Credit Cards** in the admin
2. Add your credit cards with:
   - Issuer country (Brazil/Portugal)
   - Currency
   - FX fee percentage
   - IOF percentage (for Brazilian cards)
   - Cardholder name and last 4 digits

### 3. Add Exchange Rates
1. Go to **Exchange Rates** in the admin
2. Add current exchange rates for currency conversions

### 4. Add Fixed Payments
1. Go to **Fixed Payments** in the admin
2. Add recurring payments like:
   - University fees (Brazil)
   - Rent (Portugal)
   - Insurance payments
   - Subscription services

### 5. Track Variable Expenses
1. Go to **Variable Payments** in the admin
2. Add daily expenses with:
   - Date and description
   - Amount and currency
   - Category (food, transport, etc.)
   - Link to credit card if applicable

### 6. Monitor Your Finances
- Visit the dashboard to see monthly summaries
- Check investment recommendations
- Monitor fees and taxes paid
- Track balance across countries

## Key Features for Brazilian Users in Portugal

### 🇧🇷 Brazilian Obligations
- **University Payments**: Track monthly university fees in BRL
- **Brazilian Credit Cards**: Automatic IOF calculation on foreign transactions
- **Tax Tracking**: Monitor all Brazilian taxes and fees

### 🇵🇹 Portuguese Expenses
- **Daily Living**: Track food, transport, and entertainment expenses
- **Fixed Costs**: Rent, utilities, and other recurring payments
- **Cross-border Transactions**: Handle EUR/USD transactions with Brazilian cards

### 💱 Currency Management
- **Multi-currency Income**: Track income in both BRL and EUR
- **Exchange Rate Tracking**: Historical rates for accurate conversions
- **Fee Calculation**: Automatic FX and IOF fee calculations

## Dashboard Features

### 📈 Monthly Overview
- **Income**: Total monthly income in base currency
- **Expenses**: Total expenses with transaction count
- **Fees**: Breakdown of FX fees and IOF taxes
- **Balance**: Monthly surplus/deficit with visual indicators

### 🗺️ Country-wise Breakdown
- Expenses grouped by country and currency
- Fee calculations per country
- Visual indicators for spending patterns

### 💡 Smart Recommendations
- **Investment Suggestions**: Based on monthly balance
- **Emergency Fund**: Recommendations for savings
- **Budget Optimization**: Tips for reducing expenses

## Database Management

### PostgreSQL Setup
- **Docker**: Use `docker-compose up -d db` for easy setup
- **Local**: Install PostgreSQL and create database manually
- **Environment Variables**: Configure database connection via `.env` file

### Backup and Restore
```bash
# Backup
pg_dump -h localhost -U my_financial_user my_financial_db > backup.sql

# Restore
psql -h localhost -U my_financial_user my_financial_db < backup.sql
```

## Security Features

- **Card Security**: Only last 4 digits stored
- **User Authentication**: Django admin authentication
- **Data Privacy**: PostgreSQL database with proper access controls
- **Environment Variables**: Secure configuration management
- **Backup Ready**: Easy to backup PostgreSQL database

## Technical Details

### Models
- `UserFinancialProfile`: User's financial information
- `CreditCard`: Credit card details and fees
- `ExchangeRate`: Currency exchange rates
- `FixedPayment`: Recurring payments
- `VariablePayment`: One-time expenses

### Factory Boy Integration
The project uses Factory Boy for generating realistic test data:

- **Comprehensive Factories**: Each model has a corresponding factory
- **Specialized Factories**: Brazilian/Portuguese credit cards, university payments, rent, etc.
- **Realistic Data**: Exchange rates, fees, and amounts based on real-world scenarios
- **Easy Population**: Use `make populate` to create sample data

### Makefile Commands
- **Development**: `make run`, `make shell`, `make check`
- **Database**: `make db-start`, `make db-stop`, `make migrate`
- **Data**: `make populate`, `make clean`, `make reset`
- **Quality**: `make format`, `make lint`
- **Backup**: `make backup`, `make restore`

### Admin Features
- **Comprehensive CRUD**: Full create, read, update, delete operations
- **Advanced Filtering**: Filter by country, currency, category, date
- **Search Functionality**: Search across all fields
- **Custom Dashboard**: Beautiful financial overview
- **Quick Actions**: Easy access to common operations

### Calculations
- **Automatic Fee Calculation**: FX and IOF fees calculated on save
- **Balance Tracking**: Real-time monthly balance
- **Currency Conversion**: Support for multiple currencies
- **Investment Logic**: Smart recommendations based on surplus

## Contributing

This is a personal financial tracker designed for specific use cases. Feel free to fork and adapt for your own needs.

## License

This project is for personal use. Please ensure compliance with local financial regulations when using this application. 