from rest_framework import serializers
from decimal import Decimal
from .models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment,
    PaymentStatus,
    CreditCardInvoice
)


class UserFinancialProfileSerializer(serializers.ModelSerializer):
    """Serializer for user financial profiles."""
    
    total_monthly_income_base_currency = serializers.ReadOnlyField()
    
    class Meta:
        model = UserFinancialProfile
        fields = [
            'id', 'name', 'base_currency', 'monthly_income_brl', 
            'monthly_income_eur', 'total_monthly_income_base_currency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreditCardSerializer(serializers.ModelSerializer):
    """Serializer for credit cards."""
    
    class Meta:
        model = CreditCard
        fields = [
            'id', 'issuer_country', 'currency', 'fx_fee_percent', 
            'iof_percent', 'cardholder_name', 'final_digits', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for exchange rates."""
    
    class Meta:
        model = ExchangeRate
        fields = [
            'id', 'from_currency', 'to_currency', 'rate', 
            'date', 'created_at'
        ]
        read_only_fields = ['created_at']


class FixedPaymentSerializer(serializers.ModelSerializer):
    """Serializer for fixed payments."""
    
    class Meta:
        model = FixedPayment
        fields = [
            'id', 'country', 'description', 'amount', 'currency',
            'frequency', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VariablePaymentSerializer(serializers.ModelSerializer):
    """Serializer for variable payments with nested credit card."""
    
    credit_card = CreditCardSerializer(read_only=True)
    credit_card_id = serializers.PrimaryKeyRelatedField(
        queryset=CreditCard.objects.all(),
        source='credit_card',
        required=False,
        allow_null=True
    )
    total_amount_with_fees = serializers.ReadOnlyField()
    
    class Meta:
        model = VariablePayment
        fields = [
            'id', 'date', 'country', 'description', 'amount', 
            'currency', 'category', 'linked_credit_card',
            'credit_card', 'credit_card_id', 'fx_fee_amount',
            'iof_amount', 'total_amount_with_fees',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'fx_fee_amount', 'iof_amount']


class CreditCardInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for credit card invoices."""
    
    credit_card = CreditCardSerializer(read_only=True)
    credit_card_id = serializers.PrimaryKeyRelatedField(
        queryset=CreditCard.objects.all(),
        source='credit_card',
        required=True
    )
    total_amount = serializers.ReadOnlyField()
    purchases_count = serializers.ReadOnlyField()
    total_with_fees = serializers.ReadOnlyField()
    billing_period_days = serializers.ReadOnlyField()
    
    class Meta:
        model = CreditCardInvoice
        fields = [
            'id', 'credit_card', 'credit_card_id', 'start_date', 'end_date',
            'is_closed', 'total_amount', 'purchases_count', 'total_with_fees',
            'billing_period_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount', 'purchases_count']


class CreditCardInvoiceDetailSerializer(CreditCardInvoiceSerializer):
    """Detailed serializer for credit card invoices with payment statuses."""
    
    payment_statuses = serializers.SerializerMethodField()
    
    class Meta(CreditCardInvoiceSerializer.Meta):
        fields = CreditCardInvoiceSerializer.Meta.fields + ['payment_statuses']
    
    def get_payment_statuses(self, obj):
        """Get payment statuses for this invoice."""
        payment_statuses = obj.payment_statuses.all()
        return PaymentStatusSerializer(payment_statuses, many=True).data


class PaymentStatusSerializer(serializers.ModelSerializer):
    """Serializer for payment status tracking."""
    
    payment_description = serializers.ReadOnlyField()
    payment_country = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    credit_card_invoice = CreditCardInvoiceSerializer(read_only=True)
    credit_card_invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=CreditCardInvoice.objects.all(),
        source='credit_card_invoice',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = PaymentStatus
        fields = [
            'id', 'fixed_payment', 'variable_payment', 'credit_card_invoice', 'credit_card_invoice_id',
            'payment_type', 'month_year', 'due_date', 'status', 'is_paid', 'paid_date',
            'expected_amount', 'actual_amount', 'currency', 'notes',
            'payment_description', 'payment_country', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'payment_description', 
            'payment_country', 'is_overdue'
        ]


class PaymentStatusDetailSerializer(PaymentStatusSerializer):
    """Detailed serializer for payment status with nested payment information."""
    
    fixed_payment = FixedPaymentSerializer(read_only=True)
    variable_payment = VariablePaymentSerializer(read_only=True)
    
    class Meta(PaymentStatusSerializer.Meta):
        fields = PaymentStatusSerializer.Meta.fields


# Detailed serializers for specific use cases
class CreditCardDetailSerializer(CreditCardSerializer):
    """Detailed serializer for credit cards with related payments."""
    
    variable_payments = serializers.SerializerMethodField()
    
    class Meta(CreditCardSerializer.Meta):
        fields = CreditCardSerializer.Meta.fields + ['variable_payments']
    
    def get_variable_payments(self, obj):
        """Get variable payments for this credit card."""
        payments = obj.variablepayment_set.all()[:10]  # Limit to 10 most recent
        return VariablePaymentSerializer(payments, many=True).data


class VariablePaymentDetailSerializer(VariablePaymentSerializer):
    """Detailed serializer for variable payments."""
    
    class Meta(VariablePaymentSerializer.Meta):
        fields = VariablePaymentSerializer.Meta.fields


# Summary and dashboard serializers
class FinancialSummarySerializer(serializers.Serializer):
    """Serializer for financial summary data."""
    
    total_monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_monthly_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_monthly_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses_by_country = serializers.ListField()
    expenses_by_category = serializers.ListField()
    expenses_by_currency = serializers.ListField()


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data."""
    
    profile = UserFinancialProfileSerializer(required=False, allow_null=True)
    summary = FinancialSummarySerializer()
    recent_expenses = VariablePaymentSerializer(many=True)
    active_fixed_payments = FixedPaymentSerializer(many=True)
    credit_cards = CreditCardSerializer(many=True)
    exchange_rates = ExchangeRateSerializer(many=True)
    
    def to_representation(self, instance):
        """Custom representation to handle dictionary data."""
        data = super().to_representation(instance)
        
        # Handle the summary data which contains dictionaries
        if 'summary' in data and isinstance(data['summary'], dict):
            summary_data = data['summary']
            # Convert dictionary lists to proper format
            if 'expenses_by_country' in summary_data:
                summary_data['expenses_by_country'] = list(summary_data['expenses_by_country'])
            if 'expenses_by_category' in summary_data:
                summary_data['expenses_by_category'] = list(summary_data['expenses_by_category'])
            if 'expenses_by_currency' in summary_data:
                summary_data['expenses_by_currency'] = list(summary_data['expenses_by_currency'])
        
        return data


# Statistics serializers
class ExpenseStatisticsSerializer(serializers.Serializer):
    """Serializer for expense statistics."""
    
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_daily_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses_by_category = serializers.DictField()
    expenses_by_country = serializers.DictField()
    expenses_by_currency = serializers.DictField()


class MonthlyReportSerializer(serializers.Serializer):
    """Serializer for monthly financial reports."""
    
    month = serializers.CharField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions_count = serializers.IntegerField()
    top_categories = serializers.ListField()
    top_countries = serializers.ListField()


# API Response serializers
class APIResponseSerializer(serializers.Serializer):
    """Generic API response serializer."""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False)
    errors = serializers.ListField(required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """Paginated response serializer."""
    
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.ListField()


# Filter and search serializers
class VariablePaymentFilterSerializer(serializers.Serializer):
    """Serializer for variable payment filters."""
    
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    country = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    linked_credit_card = serializers.BooleanField(required=False)
    credit_card_id = serializers.IntegerField(required=False)


class FixedPaymentFilterSerializer(serializers.Serializer):
    """Serializer for fixed payment filters."""
    
    country = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    frequency = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False) 