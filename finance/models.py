from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


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
        ('credit_card', 'Credit Card Payment'),
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
    credit_card_invoice = models.ForeignKey('CreditCardInvoice', on_delete=models.CASCADE, null=True, blank=True, related_name='payment_statuses')
    
    # Payment tracking fields
    payment_type = models.CharField(max_length=15, choices=PAYMENT_TYPE_CHOICES)
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
        verbose_name = 'Payment Status'
        verbose_name_plural = 'Payment Statuses'
        unique_together = [
            ['fixed_payment', 'month_year'],
            ['variable_payment', 'month_year'],
            ['credit_card_invoice', 'month_year']
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
        elif self.credit_card_invoice:
            self.payment_type = 'credit_card'
            self.expected_amount = self.credit_card_invoice.total_with_fees
            self.currency = self.credit_card_invoice.credit_card.currency
        
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
        elif self.credit_card_invoice:
            return f"Credit Card Invoice - {self.credit_card_invoice.credit_card.cardholder_name}"
        return "Unknown Payment"
    
    @property
    def payment_country(self):
        """Get the country of the linked payment"""
        if self.fixed_payment:
            return self.fixed_payment.country
        elif self.variable_payment:
            return self.variable_payment.country
        elif self.credit_card_invoice:
            return self.credit_card_invoice.credit_card.issuer_country
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


class CreditCardInvoice(models.Model):
    """
    Model to track credit card invoices with billing periods.
    Each invoice represents a billing cycle for a specific credit card.
    """
    credit_card = models.ForeignKey(CreditCard, on_delete=models.CASCADE, related_name='invoices')
    start_date = models.DateField(help_text="Start date of the billing period")
    end_date = models.DateField(help_text="End date of the billing period")
    is_closed = models.BooleanField(default=False, help_text="Whether this invoice is closed")
    # Note: total_amount and purchases_count are calculated properties, not stored fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Credit Card Invoice'
        verbose_name_plural = 'Credit Card Invoices'
        unique_together = ['credit_card', 'start_date', 'end_date']
        ordering = ['-end_date', '-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['credit_card'],
                condition=models.Q(is_closed=False),
                name='unique_open_invoice_per_credit_card'
            )
        ]
    
    def __str__(self):
        return f"{self.credit_card} - {self.start_date} to {self.end_date} ({'Closed' if self.is_closed else 'Open'})"
    
    @property
    def total_amount(self):
        """Total amount of all payment statuses in this invoice."""
        return self.payment_statuses.aggregate(total=models.Sum('expected_amount'))['total'] or Decimal('0')
    
    @property
    def purchases_count(self):
        """Number of payment statuses in this invoice."""
        return self.payment_statuses.count()
    
    @property
    def total_with_fees(self):
        """Total amount (same as total_amount for invoices)."""
        return self.total_amount
    
    @property
    def billing_period_days(self):
        """Number of days in the billing period."""
        return (self.end_date - self.start_date).days + 1
    
    def recalculate_totals(self):
        """Recalculate totals based on associated payment statuses."""
        # This method is kept for compatibility but totals are now calculated via properties
        pass
    
    def close_invoice(self):
        """Close the invoice and create the next one."""
        if not self.is_closed:
            self.is_closed = True
            self.save(update_fields=['is_closed'])
            
            # Create next invoice automatically
            self.create_next_invoice()
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one open invoice per credit card and handle closing."""
        # Check if this is an update and is_closed is being set to True
        if self.pk:  # This is an update
            try:
                old_instance = CreditCardInvoice.objects.get(pk=self.pk)
                if not old_instance.is_closed and self.is_closed:
                    # is_closed is being changed from False to True
                    # First save the current state
                    super().save(*args, **kwargs)
                    # Then create the next invoice
                    self.create_next_invoice()
                    return
            except CreditCardInvoice.DoesNotExist:
                pass
        
        if not self.is_closed:
            # Close any other open invoices for this credit card
            CreditCardInvoice.objects.filter(
                credit_card=self.credit_card,
                is_closed=False
            ).exclude(id=self.id).update(is_closed=True)
        
        super().save(*args, **kwargs)
    
    def create_next_invoice(self):
        """Create the next invoice for this credit card."""
        # Calculate next billing period
        # Next period starts the day after current end_date
        next_start_date = self.end_date + timedelta(days=1)
        
        # Calculate next end date (last day of next month)
        # For example: if next_start_date is 2025-08-01, we want end_date to be 2025-08-31
        if next_start_date.month == 12:
            next_year = next_start_date.year + 1
            next_month = 1
        else:
            next_year = next_start_date.year
            next_month = next_start_date.month + 1
        
        # Calculate the last day of the next month
        if next_month == 12:
            next_end_date = next_start_date.replace(year=next_year + 1, month=1, day=1) - timedelta(days=1)
        else:
            next_end_date = next_start_date.replace(year=next_year, month=next_month, day=1) - timedelta(days=1)
        
        # Create the next invoice
        CreditCardInvoice.objects.create(
            credit_card=self.credit_card,
            start_date=next_start_date,
            end_date=next_end_date,
            is_closed=False
        )
    
    @classmethod
    def get_open_invoice_for_card(cls, credit_card):
        """Get the open invoice for a specific credit card."""
        return cls.objects.filter(
            credit_card=credit_card,
            is_closed=False
        ).first()
    
    @classmethod
    def get_or_create_open_invoice(cls, credit_card):
        """Get the open invoice for a credit card or create one if none exists."""
        open_invoice = cls.get_open_invoice_for_card(credit_card)
        if not open_invoice:
            # Create a new invoice for the current month
            current_date = timezone.now().date()
            start_date = current_date.replace(day=1)
            
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
            
            open_invoice = cls.objects.create(
                credit_card=credit_card,
                start_date=start_date,
                end_date=end_date,
                is_closed=False
            )
        
        return open_invoice
