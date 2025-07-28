from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class UserFinancialProfile(models.Model):
    CURRENCY_CHOICES = [
        ('BRL', 'Brazilian Real'),
        ('EUR', 'Euro'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    base_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    monthly_income_brl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_income_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_monthly_income_base_currency(self):
        if self.base_currency == 'EUR':
            return self.monthly_income_eur
        else:
            return self.monthly_income_brl
    
    def __str__(self):
        return f"{self.name} - {self.base_currency}"


class CreditCard(models.Model):
    CURRENCY_CHOICES = [
        ('BRL', 'Brazilian Real'),
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
    ]
    
    COUNTRY_CHOICES = [
        ('Brazil', 'Brazil'),
        ('Portugal', 'Portugal'),
    ]
    
    issuer_country = models.CharField(max_length=20, choices=COUNTRY_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    fx_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    iof_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cardholder_name = models.CharField(max_length=100)
    final_digits = models.CharField(max_length=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.cardholder_name} - {self.final_digits} ({self.currency})"


class ExchangeRate(models.Model):
    CURRENCY_CHOICES = [
        ('BRL', 'Brazilian Real'),
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
    ]
    
    from_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    to_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'date']
    
    def __str__(self):
        return f"{self.from_currency}/{self.to_currency}: {self.rate} ({self.date})"


class FixedPayment(models.Model):
    COUNTRY_CHOICES = [
        ('Brazil', 'Brazil'),
        ('Portugal', 'Portugal'),
    ]
    
    CURRENCY_CHOICES = [
        ('BRL', 'Brazilian Real'),
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
    ]
    
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_currently_active(self):
        today = timezone.now().date()
        if self.end_date and today > self.end_date:
            return False
        return today >= self.start_date
    
    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency} ({self.country})"


class VariablePayment(models.Model):
    COUNTRY_CHOICES = [
        ('Brazil', 'Brazil'),
        ('Portugal', 'Portugal'),
    ]
    
    CURRENCY_CHOICES = [
        ('BRL', 'Brazilian Real'),
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
    ]
    
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('other', 'Other'),
    ]
    
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    linked_credit_card = models.BooleanField(default=False)
    credit_card = models.ForeignKey(CreditCard, on_delete=models.SET_NULL, null=True, blank=True)
    fx_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iof_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.linked_credit_card and self.credit_card:
            # Calculate FX fee
            fx_fee = (self.amount * self.credit_card.fx_fee_percent) / 100
            self.fx_fee_amount = fx_fee
            
            # Calculate IOF (Brazilian tax)
            if self.country == 'Brazil':
                iof = (self.amount * self.credit_card.iof_percent) / 100
                self.iof_amount = iof
            else:
                self.iof_amount = 0
        
        super().save(*args, **kwargs)
    
    @property
    def total_amount_with_fees(self):
        return self.amount + self.fx_fee_amount + self.iof_amount
    
    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency} ({self.date})"


class PaymentStatus(models.Model):
    """
    Model to track payment status for monthly payments.
    This serves as a monthly checklist of payments to be made.
    """
    PAYMENT_TYPE_CHOICES = [
        ('fixed', 'Fixed Payment'),
        ('variable', 'Variable Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Reference to the actual payment
    fixed_payment = models.ForeignKey(FixedPayment, on_delete=models.CASCADE, null=True, blank=True)
    variable_payment = models.ForeignKey(VariablePayment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Payment tracking fields
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    month_year = models.DateField(help_text="Month and year this payment is due (e.g., 2024-01-01 for January 2024)")
    due_date = models.DateField(help_text="Specific due date for this payment")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False, help_text="Checkbox to mark as paid")
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this payment")
    
    # Amount tracking (in case the original payment amount changes)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=VariablePayment.CURRENCY_CHOICES)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [
            ['fixed_payment', 'month_year'],
            ['variable_payment', 'month_year']
        ]
        ordering = ['due_date', 'payment_type']
    
    def save(self, *args, **kwargs):
        # Set payment type based on which payment is linked
        if self.fixed_payment:
            self.payment_type = 'fixed'
            self.expected_amount = self.fixed_payment.amount
            self.currency = self.fixed_payment.currency
        elif self.variable_payment:
            self.payment_type = 'variable'
            self.expected_amount = self.variable_payment.amount
            self.currency = self.variable_payment.currency
        
        # Update status based on is_paid
        if self.is_paid:
            self.status = 'paid'
            if not self.paid_date:
                self.paid_date = timezone.now().date()
        else:
            if self.paid_date:
                self.paid_date = None
            # Check if overdue
            if self.due_date < timezone.now().date():
                self.status = 'overdue'
            else:
                self.status = 'pending'
        
        super().save(*args, **kwargs)
    
    @property
    def payment_description(self):
        """Get the description of the linked payment"""
        if self.fixed_payment:
            return self.fixed_payment.description
        elif self.variable_payment:
            return self.variable_payment.description
        return "Unknown Payment"
    
    @property
    def payment_country(self):
        """Get the country of the linked payment"""
        if self.fixed_payment:
            return self.fixed_payment.country
        elif self.variable_payment:
            return self.variable_payment.country
        return "Unknown"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        return self.due_date < timezone.now().date() and not self.is_paid
    
    def __str__(self):
        payment_desc = self.payment_description
        month_year = self.month_year.strftime('%B %Y')
        status = self.get_status_display()
        return f"{payment_desc} - {month_year} ({status})"
