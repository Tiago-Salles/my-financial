from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path, re_path
from django.urls import include

# Schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Personal Financial Tracker API",
        default_version='v1',
        description="A comprehensive REST API for managing personal financial data across multiple countries and currencies",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@financial-tracker.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include('finance.urls')),
    ],
)

# Swagger URL patterns
swagger_urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# OpenAPI schema configuration
openapi_schema_config = {
    'info': {
        'title': 'Personal Financial Tracker API',
        'version': '1.0.0',
        'description': """
        # Personal Financial Tracker API
        
        A comprehensive REST API for managing personal financial data across multiple countries and currencies.
        
        ## Features
        
        - **Multi-country support**: Track finances in Brazil and Portugal
        - **Multi-currency support**: Handle BRL, EUR, and USD
        - **Credit card management**: Track FX fees and IOF taxes
        - **Fixed and variable payments**: Comprehensive payment tracking
        - **Exchange rate tracking**: Historical currency conversion rates
        - **Dashboard and analytics**: Financial summaries and reports
        
        ## Authentication
        
        The API supports both Token and JWT authentication:
        
        - **Token Authentication**: Include `Authorization: Token <your_token>` in headers
        - **JWT Authentication**: Include `Authorization: Bearer <your_jwt_token>` in headers
        
        ## Quick Start
        
        1. Register a user: `POST /api/auth/jwt/register/`
        2. Login to get tokens: `POST /api/auth/jwt/login/`
        3. Use the access token in subsequent requests
        4. Refresh tokens when needed: `POST /api/auth/jwt/refresh/`
        """,
        'contact': {
            'name': 'API Support',
            'email': 'support@financial-tracker.com',
        },
        'license': {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT',
        },
    },
    'servers': [
        {
            'url': 'http://localhost:8000',
            'description': 'Development server',
        },
        {
            'url': 'https://api.financial-tracker.com',
            'description': 'Production server',
        },
    ],
    'components': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            },
            'TokenAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Token authentication: Token <your_token>',
            },
        },
    },
    'security': [
        {'BearerAuth': []},
        {'TokenAuth': []},
    ],
    'tags': [
        {
            'name': 'Authentication',
            'description': 'User authentication and authorization endpoints',
        },
        {
            'name': 'Profiles',
            'description': 'User financial profile management',
        },
        {
            'name': 'Credit Cards',
            'description': 'Credit card management and fee tracking',
        },
        {
            'name': 'Exchange Rates',
            'description': 'Currency conversion rate management',
        },
        {
            'name': 'Fixed Payments',
            'description': 'Recurring payment management',
        },
        {
            'name': 'Variable Payments',
            'description': 'One-time expense tracking',
        },
        {
            'name': 'Dashboard',
            'description': 'Financial summaries and analytics',
        },
    ],
}

# Custom response schemas
custom_responses = {
    '400': openapi.Response(
        description='Bad Request',
        examples={
            'application/json': {
                'error': 'Invalid request data',
                'details': 'Field validation errors'
            }
        }
    ),
    '401': openapi.Response(
        description='Unauthorized',
        examples={
            'application/json': {
                'error': 'Authentication credentials were not provided',
                'detail': 'Invalid token or credentials'
            }
        }
    ),
    '403': openapi.Response(
        description='Forbidden',
        examples={
            'application/json': {
                'error': 'You do not have permission to perform this action',
                'detail': 'Insufficient permissions'
            }
        }
    ),
    '404': openapi.Response(
        description='Not Found',
        examples={
            'application/json': {
                'error': 'Resource not found',
                'detail': 'The requested resource does not exist'
            }
        }
    ),
    '500': openapi.Response(
        description='Internal Server Error',
        examples={
            'application/json': {
                'error': 'Internal server error',
                'detail': 'An unexpected error occurred'
            }
        }
    ),
}

# Common request/response schemas
common_schemas = {
    'UserProfile': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Registration date'),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Account status'),
        }
    ),
    'JWTResponse': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        }
    ),
    'ErrorResponse': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
            'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed error information'),
        }
    ),
    'SuccessResponse': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Response data'),
        }
    ),
} 