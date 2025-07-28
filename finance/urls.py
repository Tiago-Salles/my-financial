from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserFinancialProfileViewSet,
    CreditCardViewSet,
    ExchangeRateViewSet,
    FixedPaymentViewSet,
    VariablePaymentViewSet,
    PaymentStatusViewSet,
    DashboardViewSet,
    APIRootViewSet
)
from .auth_views import (
    login_view,
    register_view,
    logout_view,
    user_info_view
)
from .jwt_views import (
    jwt_register_view,
    jwt_login_view,
    jwt_logout_view,
    jwt_user_info_view,
    jwt_refresh_view,
    jwt_verify_view
)
from .docs_views import (
    api_docs_view,
    endpoint_docs_view,
    model_docs_view,
    api_overview_view
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'profiles', UserFinancialProfileViewSet, basename='profile')
router.register(r'credit-cards', CreditCardViewSet, basename='credit-card')
router.register(r'exchange-rates', ExchangeRateViewSet, basename='exchange-rate')
router.register(r'fixed-payments', FixedPaymentViewSet, basename='fixed-payment')
router.register(r'variable-payments', VariablePaymentViewSet, basename='variable-payment')
router.register(r'payment-status', PaymentStatusViewSet, basename='payment-status')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'', APIRootViewSet, basename='api-root')

app_name = 'finance_api'

urlpatterns = [
    path('api/', include(router.urls)),
    # Authentication endpoints
    path('api/auth/login/', login_view, name='api_login'),
    path('api/auth/register/', register_view, name='api_register'),
    path('api/auth/logout/', logout_view, name='api_logout'),
    path('api/auth/user/', user_info_view, name='api_user_info'),
    # JWT Authentication endpoints
    path('api/auth/jwt/register/', jwt_register_view, name='jwt_register'),
    path('api/auth/jwt/login/', jwt_login_view, name='jwt_login'),
    path('api/auth/jwt/logout/', jwt_logout_view, name='jwt_logout'),
    path('api/auth/jwt/user/', jwt_user_info_view, name='jwt_user_info'),
    path('api/auth/jwt/refresh/', jwt_refresh_view, name='jwt_refresh'),
    path('api/auth/jwt/verify/', jwt_verify_view, name='jwt_verify'),
    # Documentation endpoints
    path('api/docs/', api_docs_view, name='api_docs'),
    path('api/docs/overview/', api_overview_view, name='api_overview'),
    path('api/docs/endpoints/<str:endpoint_name>/', endpoint_docs_view, name='endpoint_docs'),
    path('api/docs/models/<str:model_name>/', model_docs_view, name='model_docs'),
] 