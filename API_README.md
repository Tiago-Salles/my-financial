# Personal Financial Tracker API

A comprehensive REST API for managing personal financial data across multiple countries and currencies, built with Django REST Framework.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual environment

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd my-financial

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Start PostgreSQL (using Docker)
docker-compose up -d db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

## 🔐 Authentication

The API supports both Token and JWT Authentication:

### Token Authentication
Include the token in the Authorization header:
```
Authorization: Token <your_token>
```

### JWT Authentication (Recommended)
Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

#### JWT Register User
```http
POST /api/auth/jwt/register/
Content-Type: application/json

{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password"
}
```

#### JWT Login
```http
POST /api/auth/jwt/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

#### JWT Refresh Token
```http
POST /api/auth/jwt/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

#### JWT Verify Token
```http
POST /api/auth/jwt/verify/
Content-Type: application/json

{
    "token": "your_access_token"
}
```

#### JWT Logout
```http
POST /api/auth/jwt/logout/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

#### JWT Get User Info
```http
GET /api/auth/jwt/user/
Authorization: Bearer <your_jwt_token>
```

#### Legacy Token Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password"
}
```

#### Legacy Token Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

#### Legacy Token Logout
```http
POST /api/auth/logout/
Authorization: Token <your_token>
```

#### Legacy Token Get User Info
```http
GET /api/auth/user/
Authorization: Token <your_token>
```

## 📊 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Core Endpoints

#### User Financial Profiles
- `GET /api/profiles/` - List all profiles
- `POST /api/profiles/` - Create new profile
- `GET /api/profiles/{id}/` - Get specific profile
- `PUT /api/profiles/{id}/` - Update profile
- `DELETE /api/profiles/{id}/` - Delete profile
- `GET /api/profiles/current/` - Get current user's profile

#### Credit Cards
- `GET /api/credit-cards/` - List all credit cards
- `POST /api/credit-cards/` - Create new credit card
- `GET /api/credit-cards/{id}/` - Get specific credit card
- `PUT /api/credit-cards/{id}/` - Update credit card
- `DELETE /api/credit-cards/{id}/` - Delete credit card
- `GET /api/credit-cards/active/` - Get active credit cards
- `GET /api/credit-cards/{id}/payments/` - Get payments for credit card

#### Exchange Rates
- `GET /api/exchange-rates/` - List all exchange rates
- `POST /api/exchange-rates/` - Create new exchange rate
- `GET /api/exchange-rates/{id}/` - Get specific exchange rate
- `PUT /api/exchange-rates/{id}/` - Update exchange rate
- `DELETE /api/exchange-rates/{id}/` - Delete exchange rate
- `GET /api/exchange-rates/latest/` - Get latest exchange rates
- `GET /api/exchange-rates/currency_pair/?from=BRL&to=EUR` - Get rates for currency pair

#### Fixed Payments
- `GET /api/fixed-payments/` - List all fixed payments
- `POST /api/fixed-payments/` - Create new fixed payment
- `GET /api/fixed-payments/{id}/` - Get specific fixed payment
- `PUT /api/fixed-payments/{id}/` - Update fixed payment
- `DELETE /api/fixed-payments/{id}/` - Delete fixed payment
- `GET /api/fixed-payments/active/` - Get active fixed payments
- `GET /api/fixed-payments/by_country/` - Get payments grouped by country

#### Variable Payments
- `GET /api/variable-payments/` - List all variable payments
- `POST /api/variable-payments/` - Create new variable payment
- `GET /api/variable-payments/{id}/` - Get specific variable payment
- `PUT /api/variable-payments/{id}/` - Update variable payment
- `DELETE /api/variable-payments/{id}/` - Delete variable payment
- `GET /api/variable-payments/recent/` - Get recent payments (last 30 days)
- `GET /api/variable-payments/by_category/` - Get payments grouped by category
- `GET /api/variable-payments/by_country/` - Get payments grouped by country
- `GET /api/variable-payments/statistics/?days=30` - Get expense statistics

#### Payment Status (Monthly Checklist)
- `GET /api/payment-status/` - List all payment status records
- `POST /api/payment-status/` - Create new payment status record
- `GET /api/payment-status/{id}/` - Get specific payment status record
- `PUT /api/payment-status/{id}/` - Update payment status record
- `DELETE /api/payment-status/{id}/` - Delete payment status record
- `GET /api/payment-status/pending/` - Get pending payments
- `GET /api/payment-status/paid/` - Get paid payments
- `GET /api/payment-status/overdue/` - Get overdue payments
- `GET /api/payment-status/by_month/` - Get payments by month
- `GET /api/payment-status/summary/` - Get payment status summary

#### Dashboard
- `GET /api/dashboard/summary/` - Get dashboard summary
- `GET /api/dashboard/monthly_report/?month=7&year=2024` - Get monthly report

## 📋 Data Models

### UserFinancialProfile
```json
{
    "id": 1,
    "name": "Tiago Silva",
    "base_currency": "BRL",
    "monthly_income_brl": "8000.00",
    "monthly_income_eur": "2500.00",
    "total_monthly_income_base_currency": 8000.0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### CreditCard
```json
{
    "id": 1,
    "issuer_country": "Brazil",
    "currency": "BRL",
    "fx_fee_percent": "2.99",
    "iof_percent": "6.38",
    "cardholder_name": "Tiago Silva",
    "final_digits": "1234",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### VariablePayment
```json
{
    "id": 1,
    "date": "2024-01-15",
    "country": "Brazil",
    "description": "Supermarket groceries",
    "amount": "150.00",
    "currency": "BRL",
    "category": "food",
    "linked_credit_card": true,
    "credit_card": {
        "id": 1,
        "cardholder_name": "Tiago Silva",
        "final_digits": "1234"
    },
    "fx_fee_amount": "4.49",
    "iof_amount": "9.57",
    "total_amount_with_fees": "163.06",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### FixedPayment
```json
{
    "id": 1,
    "country": "Brazil",
    "description": "Rent",
    "amount": "2000.00",
    "currency": "BRL",
    "frequency": "monthly",
    "start_date": "2024-01-01",
    "end_date": null,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### ExchangeRate
```json
{
    "id": 1,
    "from_currency": "BRL",
    "to_currency": "EUR",
    "rate": "0.18",
    "date": "2024-01-15",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### PaymentStatus
```json
{
    "id": 1,
    "fixed_payment": 1,
    "variable_payment": null,
    "payment_type": "fixed",
    "month_year": "2024-01-01",
    "due_date": "2024-01-15",
    "status": "pending",
    "is_paid": false,
    "paid_date": null,
    "expected_amount": "2000.00",
    "actual_amount": null,
    "currency": "BRL",
    "notes": "Payment scheduled",
    "payment_description": "Rent",
    "payment_country": "Brazil",
    "is_overdue": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🔍 Query Parameters

### Filtering
Most endpoints support filtering via query parameters:

```http
GET /api/variable-payments/?country=Brazil&currency=BRL&category=food&date_from=2024-01-01&date_to=2024-01-31
```

### Search
```http
GET /api/credit-cards/?search=tiago
```

### Ordering
```http
GET /api/variable-payments/?ordering=-date
GET /api/variable-payments/?ordering=amount
```

### Pagination
All list endpoints support pagination:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/variable-payments/?page=2",
    "previous": null,
    "results": [...]
}
```

## 📈 Dashboard Data

### Summary Endpoint
```http
GET /api/dashboard/summary/
Authorization: Token <your_token>
```

Returns:
```json
{
    "profile": {...},
    "summary": {
        "total_monthly_income": 8000.0,
        "total_monthly_expenses": 3500.0,
        "total_monthly_fees": 150.0,
        "monthly_balance": 4350.0,
        "expenses_by_country": [...],
        "expenses_by_category": [...],
        "expenses_by_currency": [...]
    },
    "recent_expenses": [...],
    "active_fixed_payments": [...],
    "credit_cards": [...],
    "exchange_rates": [...]
}
```

### Statistics Endpoint
```http
GET /api/variable-payments/statistics/?days=30
Authorization: Token <your_token>
```

Returns:
```json
{
    "total_expenses": 3500.0,
    "total_fees": 150.0,
    "average_daily_expense": 116.67,
    "expenses_by_category": [...],
    "expenses_by_country": [...],
    "expenses_by_currency": [...]
}
```

## 🌐 CORS Configuration

The API is configured to accept requests from common frontend development servers:

- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue CLI)

## 📚 Documentation

### Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/swagger/` - Interactive API documentation with testing capabilities
- **ReDoc**: `http://localhost:8000/redoc/` - Alternative documentation interface
- **OpenAPI Schema**: `http://localhost:8000/swagger.json` - Raw OpenAPI schema

### API Documentation
- `GET /api/docs/` - Complete API documentation
- `GET /api/docs/overview/` - API overview
- `GET /api/docs/endpoints/{endpoint_name}/` - Specific endpoint docs
- `GET /api/docs/models/{model_name}/` - Model documentation

### Interactive Documentation
Visit `http://localhost:8000/api/` in your browser for interactive API documentation.

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Using the Makefile
make lint
make format
```

### Database Management
```bash
# Using the Makefile
make db-start
make migrate
make populate
```

## 🚀 Deployment

### Environment Variables
```bash
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=my_financial_db
DB_USER=my_financial_user
DB_PASSWORD=my_financial_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Production Settings
- Set `DEBUG=False`
- Use strong `DJANGO_SECRET_KEY`
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production
- Set up proper CORS origins

## 📝 Example Usage

### JavaScript/Fetch with JWT
```javascript
// Register user with JWT
const response = await fetch('http://localhost:8000/api/auth/jwt/register/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'user',
        email: 'user@example.com',
        password: 'password123'
    })
});

const { access, refresh } = await response.json();

// Get profiles with JWT
const profilesResponse = await fetch('http://localhost:8000/api/profiles/', {
    headers: {
        'Authorization': `Bearer ${access}`
    }
});

const profiles = await profilesResponse.json();

// Refresh token when needed
const refreshResponse = await fetch('http://localhost:8000/api/auth/jwt/refresh/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        refresh: refresh
    })
});

const { access: newAccess } = await refreshResponse.json();
```

### JavaScript/Fetch with Legacy Token
```javascript
// Register user with legacy token
const response = await fetch('http://localhost:8000/api/auth/register/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'user',
        email: 'user@example.com',
        password: 'password123'
    })
});

const { token } = await response.json();

// Get profiles with legacy token
const profilesResponse = await fetch('http://localhost:8000/api/profiles/', {
    headers: {
        'Authorization': `Token ${token}`
    }
});

const profiles = await profilesResponse.json();
```

### Python/Requests with JWT
```python
import requests

# Register user with JWT
response = requests.post('http://localhost:8000/api/auth/jwt/register/', json={
    'username': 'user',
    'email': 'user@example.com',
    'password': 'password123'
})

access_token = response.json()['access']
refresh_token = response.json()['refresh']

# Get profiles with JWT
headers = {'Authorization': f'Bearer {access_token}'}
profiles = requests.get('http://localhost:8000/api/profiles/', headers=headers).json()

# Refresh token when needed
refresh_response = requests.post('http://localhost:8000/api/auth/jwt/refresh/', json={
    'refresh': refresh_token
})
new_access_token = refresh_response.json()['access']
```

### Python/Requests with Legacy Token
```python
import requests

# Register user with legacy token
response = requests.post('http://localhost:8000/api/auth/register/', json={
    'username': 'user',
    'email': 'user@example.com',
    'password': 'password123'
})

token = response.json()['token']

# Get profiles with legacy token
headers = {'Authorization': f'Token {token}'}
profiles = requests.get('http://localhost:8000/api/profiles/', headers=headers).json()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 