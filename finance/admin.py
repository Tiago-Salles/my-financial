from django.contrib import admin
from django.db.models import Sum, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from .models import (
    UserFinancialProfile, 
    CreditCard, 
    ExchangeRate, 
    FixedPayment, 
    VariablePayment,
    PaymentStatus
)


class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['cardholder_name', 'issuer_country', 'currency', 'final_digits', 'fx_fee_percent', 'iof_percent', 'is_active']
    list_filter = ['issuer_country', 'currency', 'is_active']
    search_fields = ['cardholder_name', 'final_digits']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Card Information', {
            'fields': ('cardholder_name', 'final_digits', 'issuer_country', 'currency')
        }),
        ('Fees & Taxes', {
            'fields': ('fx_fee_percent', 'iof_percent')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'date']
    list_filter = ['from_currency', 'to_currency', 'date']
    search_fields = ['from_currency', 'to_currency']
    readonly_fields = ['created_at']
    ordering = ['-date', 'from_currency', 'to_currency']
    
    fieldsets = (
        ('Rate Information', {
            'fields': ('from_currency', 'to_currency', 'rate', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class FixedPaymentAdmin(admin.ModelAdmin):
    list_display = ['description', 'country', 'amount', 'currency', 'frequency', 'start_date', 'end_date', 'is_active']
    list_filter = ['country', 'currency', 'frequency', 'is_active', 'start_date']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('description', 'amount', 'currency', 'country')
        }),
        ('Schedule', {
            'fields': ('frequency', 'start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class VariablePaymentAdmin(admin.ModelAdmin):
    list_display = ['description', 'date', 'country', 'amount', 'currency', 'category', 'linked_credit_card', 'total_amount_with_fees_display']
    list_filter = ['country', 'currency', 'category', 'linked_credit_card', 'date']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at', 'fx_fee_amount', 'iof_amount']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('description', 'amount', 'currency', 'country', 'category', 'date')
        }),
        ('Credit Card', {
            'fields': ('linked_credit_card', 'credit_card')
        }),
        ('Fees (Auto-calculated)', {
            'fields': ('fx_fee_amount', 'iof_amount'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_with_fees_display(self, obj):
        """Display total amount with fees in a formatted way."""
        total = obj.total_amount_with_fees
        base = obj.amount

        if total != base:
            return format_html(
                f'<span style="color: #d9534f;">{float(total)}</span> <small>(+{float(total - base)} fees)</small>',                
            )
        return "{:.2f}".format(float(total))

    total_amount_with_fees_display.short_description = 'Total Amount'


class UserFinancialProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_currency', 'monthly_income_brl', 'monthly_income_eur', 'total_monthly_income_display']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('name', 'base_currency')
        }),
        ('Monthly Income', {
            'fields': ('monthly_income_brl', 'monthly_income_eur')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_monthly_income_display(self, obj):
        """Display total monthly income in base currency."""
        return f"{obj.total_monthly_income_base_currency} {obj.base_currency}"
    total_monthly_income_display.short_description = 'Total Monthly Income'


class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = [
        'payment_description', 'month_year', 'due_date', 'status', 'is_paid', 
        'expected_amount', 'currency', 'payment_country'
    ]
    list_filter = [
        'status', 'is_paid', 'payment_type', 'currency', 
        'month_year', 'due_date'
    ]
    search_fields = ['payment_description', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'payment_description', 'payment_country']
    date_hierarchy = 'month_year'
    list_editable = ['is_paid', 'status']
    
    fieldsets = (
        ('Payment Reference', {
            'fields': ('fixed_payment', 'variable_payment', 'payment_type')
        }),
        ('Payment Tracking', {
            'fields': ('month_year', 'due_date', 'status', 'is_paid', 'paid_date')
        }),
        ('Amount Information', {
            'fields': ('expected_amount', 'actual_amount', 'currency')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance."""
        return super().get_queryset(request).select_related(
            'fixed_payment', 'variable_payment'
        )
    
    def payment_description(self, obj):
        """Display the payment description."""
        return obj.payment_description
    payment_description.short_description = 'Payment Description'
    
    def payment_country(self, obj):
        """Display the payment country."""
        return obj.payment_country
    payment_country.short_description = 'Country'


# Register models
admin.site.register(UserFinancialProfile, UserFinancialProfileAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
admin.site.register(FixedPayment, FixedPaymentAdmin)
admin.site.register(VariablePayment, VariablePaymentAdmin)
admin.site.register(PaymentStatus, PaymentStatusAdmin)
