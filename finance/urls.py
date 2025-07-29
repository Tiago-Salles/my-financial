from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserFinancialProfileViewSet,
    CreditCardViewSet,
    ExchangeRateViewSet,
    FixedPaymentViewSet,
    VariablePaymentViewSet,
    PaymentStatusViewSet,
    CreditCardInvoiceViewSet,
    DashboardViewSet,
    APIRootViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'profiles', UserFinancialProfileViewSet)
router.register(r'credit-cards', CreditCardViewSet)
router.register(r'exchange-rates', ExchangeRateViewSet)
router.register(r'fixed-payments', FixedPaymentViewSet)
router.register(r'variable-payments', VariablePaymentViewSet)
router.register(r'payment-statuses', PaymentStatusViewSet)
router.register(r'credit-card-invoices', CreditCardInvoiceViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'', APIRootViewSet, basename='api-root')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
] 