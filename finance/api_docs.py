"""
Personal Financial Tracker API Documentation

This module contains comprehensive documentation for the Personal Financial Tracker API.
The API provides endpoints for managing financial data including profiles, payments, 
credit cards, and exchange rates.

Base URL: http://localhost:8000/api/

Authentication:
- Token Authentication: Include 'Authorization: Token <your_token>' in headers
- Session Authentication: Use Django's session authentication

Response Format:
All API responses are in JSON format with the following structure:
{
    "success": true/false,
    "message": "Response message",
    "data": {...},
    "errors": [...]
}
"""

API_DOCUMENTATION = {
    "title": "Personal Financial Tracker API",
    "version": "1.0.0",
    "description": "API for managing personal financial data across multiple countries and currencies",
    "base_url": "http://localhost:8000/api/",
    "authentication": {
        "methods": [
            "Token Authentication",
            "Session Authentication"
        ],
        "headers": {
            "Authorization": "Token <your_token>",
            "Content-Type": "application/json"
        }
    },
    "endpoints": {
        "authentication": {
            "login": {
                "url": "/api/auth/login/",
                "method": "POST",
                "description": "Authenticate user and get token",
                "request_body": {
                    "username": "string",
                    "password": "string"
                },
                "response": {
                    "token": "string",
                    "user_id": "integer",
                    "username": "string",
                    "email": "string"
                }
            },
            "register": {
                "url": "/api/auth/register/",
                "method": "POST",
                "description": "Register new user",
                "request_body": {
                    "username": "string",
                    "email": "string",
                    "password": "string"
                },
                "response": {
                    "token": "string",
                    "user_id": "integer",
                    "username": "string",
                    "email": "string",
                    "message": "string"
                }
            },
            "logout": {
                "url": "/api/auth/logout/",
                "method": "POST",
                "description": "Logout user and invalidate token",
                "response": {
                    "message": "string"
                }
            },
            "user_info": {
                "url": "/api/auth/user/",
                "method": "GET",
                "description": "Get current user information",
                "response": {
                    "user_id": "integer",
                    "username": "string",
                    "email": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "date_joined": "datetime",
                    "is_active": "boolean"
                }
            }
        },
        "profiles": {
            "list": {
                "url": "/api/profiles/",
                "method": "GET",
                "description": "Get all user financial profiles",
                "query_params": {
                    "search": "string (optional)",
                    "ordering": "string (optional)"
                }
            },
            "create": {
                "url": "/api/profiles/",
                "method": "POST",
                "description": "Create new user financial profile",
                "request_body": {
                    "name": "string",
                    "base_currency": "BRL|EUR",
                    "monthly_income_brl": "decimal",
                    "monthly_income_eur": "decimal"
                }
            },
            "retrieve": {
                "url": "/api/profiles/{id}/",
                "method": "GET",
                "description": "Get specific user financial profile"
            },
            "update": {
                "url": "/api/profiles/{id}/",
                "method": "PUT",
                "description": "Update user financial profile"
            },
            "delete": {
                "url": "/api/profiles/{id}/",
                "method": "DELETE",
                "description": "Delete user financial profile"
            },
            "current": {
                "url": "/api/profiles/current/",
                "method": "GET",
                "description": "Get current user's financial profile"
            }
        },
        "credit_cards": {
            "list": {
                "url": "/api/credit-cards/",
                "method": "GET",
                "description": "Get all credit cards",
                "query_params": {
                    "search": "string (optional)",
                    "ordering": "string (optional)"
                }
            },
            "create": {
                "url": "/api/credit-cards/",
                "method": "POST",
                "description": "Create new credit card",
                "request_body": {
                    "issuer_country": "Brazil|Portugal",
                    "currency": "BRL|EUR|USD",
                    "fx_fee_percent": "decimal",
                    "iof_percent": "decimal",
                    "cardholder_name": "string",
                    "final_digits": "string (4 digits)",
                    "is_active": "boolean"
                }
            },
            "retrieve": {
                "url": "/api/credit-cards/{id}/",
                "method": "GET",
                "description": "Get specific credit card with related payments"
            },
            "update": {
                "url": "/api/credit-cards/{id}/",
                "method": "PUT",
                "description": "Update credit card"
            },
            "delete": {
                "url": "/api/credit-cards/{id}/",
                "method": "DELETE",
                "description": "Delete credit card"
            },
            "payments": {
                "url": "/api/credit-cards/{id}/payments/",
                "method": "GET",
                "description": "Get payments for specific credit card"
            },
            "active": {
                "url": "/api/credit-cards/active/",
                "method": "GET",
                "description": "Get only active credit cards"
            }
        },
        "exchange_rates": {
            "list": {
                "url": "/api/exchange-rates/",
                "method": "GET",
                "description": "Get all exchange rates",
                "query_params": {
                    "search": "string (optional)",
                    "ordering": "string (optional)"
                }
            },
            "create": {
                "url": "/api/exchange-rates/",
                "method": "POST",
                "description": "Create new exchange rate",
                "request_body": {
                    "from_currency": "BRL|EUR|USD",
                    "to_currency": "BRL|EUR|USD",
                    "rate": "decimal",
                    "date": "date"
                }
            },
            "retrieve": {
                "url": "/api/exchange-rates/{id}/",
                "method": "GET",
                "description": "Get specific exchange rate"
            },
            "update": {
                "url": "/api/exchange-rates/{id}/",
                "method": "PUT",
                "description": "Update exchange rate"
            },
            "delete": {
                "url": "/api/exchange-rates/{id}/",
                "method": "DELETE",
                "description": "Delete exchange rate"
            },
            "latest": {
                "url": "/api/exchange-rates/latest/",
                "method": "GET",
                "description": "Get latest exchange rates"
            },
            "currency_pair": {
                "url": "/api/exchange-rates/currency_pair/",
                "method": "GET",
                "description": "Get exchange rates for specific currency pair",
                "query_params": {
                    "from": "string (currency code)",
                    "to": "string (currency code)"
                }
            }
        },
        "fixed_payments": {
            "list": {
                "url": "/api/fixed-payments/",
                "method": "GET",
                "description": "Get all fixed payments",
                "query_params": {
                    "country": "string (optional)",
                    "currency": "string (optional)",
                    "frequency": "monthly|yearly (optional)",
                    "is_active": "boolean (optional)",
                    "search": "string (optional)",
                    "ordering": "string (optional)"
                }
            },
            "create": {
                "url": "/api/fixed-payments/",
                "method": "POST",
                "description": "Create new fixed payment",
                "request_body": {
                    "country": "Brazil|Portugal",
                    "description": "string",
                    "amount": "decimal",
                    "currency": "BRL|EUR|USD",
                    "frequency": "monthly|yearly",
                    "start_date": "date",
                    "end_date": "date (optional)",
                    "is_active": "boolean"
                }
            },
            "retrieve": {
                "url": "/api/fixed-payments/{id}/",
                "method": "GET",
                "description": "Get specific fixed payment"
            },
            "update": {
                "url": "/api/fixed-payments/{id}/",
                "method": "PUT",
                "description": "Update fixed payment"
            },
            "delete": {
                "url": "/api/fixed-payments/{id}/",
                "method": "DELETE",
                "description": "Delete fixed payment"
            },
            "active": {
                "url": "/api/fixed-payments/active/",
                "method": "GET",
                "description": "Get only active fixed payments"
            },
            "by_country": {
                "url": "/api/fixed-payments/by_country/",
                "method": "GET",
                "description": "Get fixed payments grouped by country"
            }
        },
        "variable_payments": {
            "list": {
                "url": "/api/variable-payments/",
                "method": "GET",
                "description": "Get all variable payments",
                "query_params": {
                    "date_from": "date (optional)",
                    "date_to": "date (optional)",
                    "country": "string (optional)",
                    "currency": "string (optional)",
                    "category": "string (optional)",
                    "linked_credit_card": "boolean (optional)",
                    "credit_card_id": "integer (optional)",
                    "search": "string (optional)",
                    "ordering": "string (optional)"
                }
            },
            "create": {
                "url": "/api/variable-payments/",
                "method": "POST",
                "description": "Create new variable payment",
                "request_body": {
                    "date": "date",
                    "country": "Brazil|Portugal",
                    "description": "string",
                    "amount": "decimal",
                    "currency": "BRL|EUR|USD",
                    "category": "string",
                    "linked_credit_card": "boolean",
                    "credit_card_id": "integer (optional)"
                }
            },
            "retrieve": {
                "url": "/api/variable-payments/{id}/",
                "method": "GET",
                "description": "Get specific variable payment with details"
            },
            "update": {
                "url": "/api/variable-payments/{id}/",
                "method": "PUT",
                "description": "Update variable payment"
            },
            "delete": {
                "url": "/api/variable-payments/{id}/",
                "method": "DELETE",
                "description": "Delete variable payment"
            },
            "recent": {
                "url": "/api/variable-payments/recent/",
                "method": "GET",
                "description": "Get recent variable payments (last 30 days)"
            },
            "by_category": {
                "url": "/api/variable-payments/by_category/",
                "method": "GET",
                "description": "Get variable payments grouped by category"
            },
            "by_country": {
                "url": "/api/variable-payments/by_country/",
                "method": "GET",
                "description": "Get variable payments grouped by country"
            },
            "statistics": {
                "url": "/api/variable-payments/statistics/",
                "method": "GET",
                "description": "Get expense statistics",
                "query_params": {
                    "days": "integer (optional, default: 30)"
                }
            }
        },
        "dashboard": {
            "summary": {
                "url": "/api/dashboard/summary/",
                "method": "GET",
                "description": "Get dashboard summary data with current month statistics"
            },
            "monthly_report": {
                "url": "/api/dashboard/monthly_report/",
                "method": "GET",
                "description": "Get monthly financial report",
                "query_params": {
                    "month": "integer (optional, default: current month)",
                    "year": "integer (optional, default: current year)"
                }
            }
        }
    },
    "models": {
        "UserFinancialProfile": {
            "fields": {
                "id": "integer (primary key)",
                "name": "string",
                "base_currency": "BRL|EUR",
                "monthly_income_brl": "decimal",
                "monthly_income_eur": "decimal",
                "total_monthly_income_base_currency": "decimal (calculated)",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        },
        "CreditCard": {
            "fields": {
                "id": "integer (primary key)",
                "issuer_country": "Brazil|Portugal",
                "currency": "BRL|EUR|USD",
                "fx_fee_percent": "decimal",
                "iof_percent": "decimal",
                "cardholder_name": "string",
                "final_digits": "string (4 digits)",
                "is_active": "boolean",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        },
        "ExchangeRate": {
            "fields": {
                "id": "integer (primary key)",
                "from_currency": "BRL|EUR|USD",
                "to_currency": "BRL|EUR|USD",
                "rate": "decimal",
                "date": "date",
                "created_at": "datetime"
            }
        },
        "FixedPayment": {
            "fields": {
                "id": "integer (primary key)",
                "country": "Brazil|Portugal",
                "description": "string",
                "amount": "decimal",
                "currency": "BRL|EUR|USD",
                "frequency": "monthly|yearly",
                "start_date": "date",
                "end_date": "date (optional)",
                "is_active": "boolean",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        },
        "VariablePayment": {
            "fields": {
                "id": "integer (primary key)",
                "date": "date",
                "country": "Brazil|Portugal",
                "description": "string",
                "amount": "decimal",
                "currency": "BRL|EUR|USD",
                "category": "string",
                "linked_credit_card": "boolean",
                "credit_card": "CreditCard object (nested)",
                "credit_card_id": "integer (optional)",
                "fx_fee_amount": "decimal (calculated)",
                "iof_amount": "decimal (calculated)",
                "total_amount_with_fees": "decimal (calculated)",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        }
    },
    "error_codes": {
        "400": "Bad Request - Invalid request data",
        "401": "Unauthorized - Authentication required",
        "403": "Forbidden - Permission denied",
        "404": "Not Found - Resource not found",
        "500": "Internal Server Error - Server error"
    },
    "examples": {
        "create_profile": {
            "method": "POST",
            "url": "/api/profiles/",
            "headers": {
                "Authorization": "Token your_token_here",
                "Content-Type": "application/json"
            },
            "body": {
                "name": "Tiago Silva",
                "base_currency": "BRL",
                "monthly_income_brl": "5000.00",
                "monthly_income_eur": "1000.00"
            }
        },
        "create_variable_payment": {
            "method": "POST",
            "url": "/api/variable-payments/",
            "headers": {
                "Authorization": "Token your_token_here",
                "Content-Type": "application/json"
            },
            "body": {
                "date": "2024-01-15",
                "country": "Brazil",
                "description": "Supermarket groceries",
                "amount": "150.00",
                "currency": "BRL",
                "category": "food",
                "linked_credit_card": True,
                "credit_card_id": 1
            }
        },
        "get_dashboard_summary": {
            "method": "GET",
            "url": "/api/dashboard/summary/",
            "headers": {
                "Authorization": "Token your_token_here"
            }
        }
    }
}


def get_api_documentation():
    """Return the complete API documentation."""
    return API_DOCUMENTATION


def get_endpoint_documentation(endpoint_name):
    """Return documentation for a specific endpoint."""
    return API_DOCUMENTATION.get("endpoints", {}).get(endpoint_name, {})


def get_model_documentation(model_name):
    """Return documentation for a specific model."""
    return API_DOCUMENTATION.get("models", {}).get(model_name, {}) 