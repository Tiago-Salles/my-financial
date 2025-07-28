from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment,
    PaymentStatus
)
from .serializers import (
    UserFinancialProfileSerializer,
    CreditCardSerializer,
    CreditCardDetailSerializer,
    ExchangeRateSerializer,
    FixedPaymentSerializer,
    VariablePaymentSerializer,
    VariablePaymentDetailSerializer,
    PaymentStatusSerializer,
    PaymentStatusDetailSerializer,
    FinancialSummarySerializer,
    DashboardSerializer,
    ExpenseStatisticsSerializer,
    MonthlyReportSerializer,
    VariablePaymentFilterSerializer,
    FixedPaymentFilterSerializer,
    APIResponseSerializer
)


class UserFinancialProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user financial profiles."""
    
    queryset = UserFinancialProfile.objects.all()
    serializer_class = UserFinancialProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'base_currency', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current user's financial profile."""
        profile = UserFinancialProfile.objects.first()
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        return Response({'error': 'No profile found'}, status=status.HTTP_404_NOT_FOUND)


class CreditCardViewSet(viewsets.ModelViewSet):
    """ViewSet for credit cards."""
    
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['cardholder_name', 'final_digits']
    ordering_fields = ['cardholder_name', 'issuer_country', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CreditCardDetailSerializer
        return CreditCardSerializer
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get payments for a specific credit card."""
        credit_card = self.get_object()
        payments = VariablePayment.objects.filter(credit_card=credit_card)
        serializer = VariablePaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active credit cards."""
        active_cards = CreditCard.objects.filter(is_active=True)
        serializer = self.get_serializer(active_cards, many=True)
        return Response(serializer.data)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """ViewSet for exchange rates."""
    
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['from_currency', 'to_currency']
    ordering_fields = ['date', 'from_currency', 'to_currency']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest exchange rates."""
        latest_rates = ExchangeRate.objects.filter(
            date=ExchangeRate.objects.latest('date').date
        )
        serializer = self.get_serializer(latest_rates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def currency_pair(self, request):
        """Get exchange rates for a specific currency pair."""
        from_currency = request.query_params.get('from')
        to_currency = request.query_params.get('to')
        
        if not from_currency or not to_currency:
            return Response(
                {'error': 'Both from_currency and to_currency are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rates = ExchangeRate.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency
        ).order_by('-date')
        
        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)


class FixedPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for fixed payments."""
    
    queryset = FixedPayment.objects.all()
    serializer_class = FixedPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description']
    ordering_fields = ['description', 'amount', 'start_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = FixedPayment.objects.all()
        
        # Apply filters
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        
        currency = self.request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)
        
        frequency = self.request.query_params.get('frequency')
        if frequency:
            queryset = queryset.filter(frequency=frequency)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active fixed payments."""
        active_payments = FixedPayment.objects.filter(is_active=True)
        serializer = self.get_serializer(active_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get fixed payments grouped by country."""
        payments = FixedPayment.objects.values('country').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        )
        return Response(payments)


class VariablePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for variable payments."""
    
    queryset = VariablePayment.objects.all()
    serializer_class = VariablePaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'description', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VariablePaymentDetailSerializer
        return VariablePaymentSerializer
    
    def get_queryset(self):
        queryset = VariablePayment.objects.all()
        
        # Apply filters
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        
        currency = self.request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        linked_credit_card = self.request.query_params.get('linked_credit_card')
        if linked_credit_card is not None:
            queryset = queryset.filter(linked_credit_card=linked_credit_card.lower() == 'true')
        
        credit_card_id = self.request.query_params.get('credit_card_id')
        if credit_card_id:
            queryset = queryset.filter(credit_card_id=credit_card_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent variable payments (last 30 days)."""
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_payments = VariablePayment.objects.filter(date__gte=thirty_days_ago)
        serializer = self.get_serializer(recent_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get variable payments grouped by category."""
        payments = VariablePayment.objects.values('category').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        )
        return Response(payments)
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get variable payments grouped by country."""
        payments = VariablePayment.objects.values('country').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        )
        return Response(payments)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get expense statistics."""
        # Get date range from query params or default to last 30 days
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        payments = VariablePayment.objects.filter(date__gte=start_date)
        
        total_expenses = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_fees = (payments.aggregate(
            total=Sum('fx_fee_amount')
        )['total'] or Decimal('0')) + (payments.aggregate(
            total=Sum('iof_amount')
        )['total'] or Decimal('0'))
        
        expenses_by_category = payments.values('category').annotate(
            total=Sum('amount')
        )
        
        expenses_by_country = payments.values('country').annotate(
            total=Sum('amount')
        )
        
        expenses_by_currency = payments.values('currency').annotate(
            total=Sum('amount')
        )
        
        data = {
            'total_expenses': total_expenses,
            'total_fees': total_fees,
            'average_daily_expense': total_expenses / days if days > 0 else 0,
            'expenses_by_category': list(expenses_by_category),
            'expenses_by_country': list(expenses_by_country),
            'expenses_by_currency': list(expenses_by_currency),
        }
        
        serializer = ExpenseStatisticsSerializer(data)
        return Response(serializer.data)


class PaymentStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for payment status tracking."""
    
    queryset = PaymentStatus.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['payment_description', 'notes']
    ordering_fields = ['due_date', 'month_year', 'status', 'is_paid', 'created_at']
    ordering = ['due_date', 'payment_type']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentStatusDetailSerializer
        return PaymentStatusSerializer
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return PaymentStatus.objects.select_related(
            'fixed_payment', 'variable_payment'
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending payments."""
        pending_payments = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue payments."""
        overdue_payments = self.get_queryset().filter(status='overdue')
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def paid(self, request):
        """Get all paid payments."""
        paid_payments = self.get_queryset().filter(status='paid')
        serializer = self.get_serializer(paid_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """Get payments grouped by month."""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = self.get_queryset()
        
        if month and year:
            queryset = queryset.filter(
                month_year__year=year,
                month_year__month=month
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment status summary."""
        queryset = self.get_queryset()
        
        summary = {
            'total_payments': queryset.count(),
            'pending_payments': queryset.filter(status='pending').count(),
            'paid_payments': queryset.filter(status='paid').count(),
            'overdue_payments': queryset.filter(status='overdue').count(),
            'cancelled_payments': queryset.filter(status='cancelled').count(),
            'total_expected_amount': queryset.aggregate(
                total=Sum('expected_amount')
            )['total'] or Decimal('0'),
            'total_actual_amount': queryset.filter(
                actual_amount__isnull=False
            ).aggregate(
                total=Sum('actual_amount')
            )['total'] or Decimal('0'),
        }
        
        return Response(summary)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard data."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get dashboard summary data."""
        # Get current month data
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Get user profile
        try:
            profile = UserFinancialProfile.objects.first()
        except UserFinancialProfile.DoesNotExist:
            profile = None
        
        # Calculate monthly expenses
        monthly_expenses = VariablePayment.objects.filter(
            date__year=current_year,
            date__month=current_month
        )
        
        # Calculate fixed payments for current month
        fixed_payments = FixedPayment.objects.filter(
            is_active=True,
            start_date__lte=now.date()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now.date())
        )
        
        # Calculate totals
        monthly_income = profile.total_monthly_income_base_currency if profile else 0
        total_expenses = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0
        total_fees = (monthly_expenses.aggregate(
            total=Sum('fx_fee_amount')
        )['total'] or 0) + (monthly_expenses.aggregate(
            total=Sum('iof_amount')
        )['total'] or 0)
        monthly_balance = monthly_income - total_expenses - total_fees
        
        # Group expenses
        expenses_by_country = monthly_expenses.values('country', 'currency').annotate(
            total_amount=Sum('amount'),
            total_fees=Sum('fx_fee_amount')
        )
        # Add IOF fees separately
        for expense in expenses_by_country:
            expense['total_fees'] += monthly_expenses.filter(
                country=expense['country'],
                currency=expense['currency']
            ).aggregate(total=Sum('iof_amount'))['total'] or 0
        
        expenses_by_category = monthly_expenses.values('category').annotate(
            total=Sum('amount')
        )
        
        expenses_by_currency = monthly_expenses.values('currency').annotate(
            total=Sum('amount')
        )
        
        data = {
            'profile': UserFinancialProfileSerializer(profile).data if profile else None,
            'summary': {
                'total_monthly_income': monthly_income,
                'total_monthly_expenses': total_expenses,
                'total_monthly_fees': total_fees,
                'monthly_balance': monthly_balance,
                'expenses_by_country': list(expenses_by_country),
                'expenses_by_category': list(expenses_by_category),
                'expenses_by_currency': list(expenses_by_currency),
            },
            'recent_expenses': VariablePaymentSerializer(
                monthly_expenses[:10], many=True
            ).data,
            'active_fixed_payments': FixedPaymentSerializer(
                fixed_payments, many=True
            ).data,
            'credit_cards': CreditCardSerializer(
                CreditCard.objects.filter(is_active=True), many=True
            ).data,
            'exchange_rates': ExchangeRateSerializer(
                ExchangeRate.objects.filter(date=now.date())[:10], many=True
            ).data,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Get monthly financial report."""
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))
        
        # Get data for specified month
        payments = VariablePayment.objects.filter(
            date__year=year,
            date__month=month
        )
        
        profile = UserFinancialProfile.objects.first()
        income = profile.total_monthly_income_base_currency if profile else 0
        expenses = payments.aggregate(total=Sum('amount'))['total'] or 0
        fees = (payments.aggregate(
            total=Sum('fx_fee_amount')
        )['total'] or 0) + (payments.aggregate(
            total=Sum('iof_amount')
        )['total'] or 0)
        balance = income - expenses - fees
        
        # Get top categories and countries
        top_categories = payments.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        top_countries = payments.values('country').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        data = {
            'month': month,
            'year': year,
            'income': income,
            'expenses': expenses,
            'fees': fees,
            'balance': balance,
            'transactions_count': payments.count(),
            'top_categories': list(top_categories),
            'top_countries': list(top_countries),
        }
        
        serializer = MonthlyReportSerializer(data)
        return Response(serializer.data)


class APIRootViewSet(viewsets.ViewSet):
    """Root API view with available endpoints."""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def root(self, request):
        """API root with available endpoints."""
        data = {
            'message': 'Personal Financial Tracker API',
            'version': '1.0.0',
            'endpoints': {
                'profiles': '/api/profiles/',
                'credit_cards': '/api/credit-cards/',
                'exchange_rates': '/api/exchange-rates/',
                'fixed_payments': '/api/fixed-payments/',
                'variable_payments': '/api/variable-payments/',
                'dashboard': '/api/dashboard/',
            },
            'authentication': 'Token or Session authentication required',
            'documentation': '/api/docs/',
        }
        return Response(data)
