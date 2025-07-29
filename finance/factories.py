import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute
from decimal import Decimal
from datetime import date, timedelta
import random
from .models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment,
    PaymentStatus,
    CreditCardInvoice
)


class UserFinancialProfileFactory(DjangoModelFactory):
    """Factory for creating user financial profiles."""
    
    class Meta:
        model = UserFinancialProfile
    
    name = Faker('name')
    base_currency = factory.Iterator(['BRL', 'EUR'])
    monthly_income_brl = factory.LazyFunction(lambda: Decimal(random.uniform(2000, 15000)).quantize(Decimal('0.01')))
    monthly_income_eur = factory.LazyFunction(lambda: Decimal(random.uniform(1000, 8000)).quantize(Decimal('0.01')))


class CreditCardFactory(DjangoModelFactory):
    """Factory for creating credit cards."""
    
    class Meta:
        model = CreditCard
    
    issuer_country = factory.Iterator(['Brazil', 'Portugal'])
    currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    fx_fee_percent = factory.LazyFunction(lambda: Decimal(random.uniform(0, 5)).quantize(Decimal('0.01')))
    iof_percent = factory.LazyFunction(lambda: Decimal(random.uniform(0, 6.38)).quantize(Decimal('0.01')))
    cardholder_name = Faker('name')
    final_digits = factory.LazyFunction(lambda: str(random.randint(1000, 9999)))
    is_active = factory.Iterator([True, True, True, False])  # 75% active cards


class ExchangeRateFactory(DjangoModelFactory):
    """Factory for creating exchange rates."""
    
    class Meta:
        model = ExchangeRate
    
    from_currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    to_currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    rate = factory.LazyFunction(lambda: Decimal(random.uniform(0.1, 10.0)).quantize(Decimal('0.000001')))
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(0, 30)))
    
    @factory.post_generation
    def validate_currencies(self, create, extracted, **kwargs):
        """Ensure from_currency and to_currency are different."""
        if self.from_currency == self.to_currency:
            self.rate = Decimal('1.000000')


class FixedPaymentFactory(DjangoModelFactory):
    """Factory for creating fixed payments."""
    
    class Meta:
        model = FixedPayment
    
    country = factory.Iterator(['Brazil', 'Portugal'])
    description = factory.LazyFunction(lambda: random.choice([
        'University Fees',
        'Rent',
        'Insurance',
        'Internet',
        'Phone Bill',
        'Gym Membership',
        'Netflix Subscription',
        'Spotify Premium',
        'Car Insurance',
        'Health Insurance'
    ]))
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(50, 2000)).quantize(Decimal('0.01')))
    currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    frequency = factory.Iterator(['monthly', 'yearly'])
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(0, 365)))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=random.randint(0, 365)) if random.choice([True, False]) else None)
    is_active = factory.Iterator([True, True, True, False])  # 75% active payments


class VariablePaymentFactory(DjangoModelFactory):
    """Factory for creating variable payments."""
    
    class Meta:
        model = VariablePayment
    
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(0, 30)))
    country = factory.Iterator(['Brazil', 'Portugal'])
    description = factory.LazyFunction(lambda: random.choice([
        'Groceries',
        'Restaurant',
        'Transport',
        'Shopping',
        'Entertainment',
        'Coffee',
        'Lunch',
        'Dinner',
        'Movie',
        'Concert',
        'Books',
        'Clothing',
        'Electronics',
        'Pharmacy',
        'Gas'
    ]))
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(5, 500)).quantize(Decimal('0.01')))
    currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    category = factory.Iterator(['food', 'transport', 'entertainment', 'shopping', 'health', 'education', 'utilities', 'other'])
    linked_credit_card = factory.Iterator([True, True, False])  # 66% linked to credit card
    credit_card = factory.SubFactory(CreditCardFactory)
    fx_fee_amount = factory.LazyFunction(lambda: Decimal('0.00'))
    iof_amount = factory.LazyFunction(lambda: Decimal('0.00'))
    
    @factory.post_generation
    def calculate_fees(self, create, extracted, **kwargs):
        """Calculate fees based on credit card settings."""
        if self.linked_credit_card and self.credit_card:
            # Calculate FX fee
            if self.currency != self.credit_card.currency:
                self.fx_fee_amount = (self.amount * self.credit_card.fx_fee_percent) / 100
            else:
                self.fx_fee_amount = Decimal('0.00')
            
            # Calculate IOF (Brazilian tax on foreign transactions)
            if self.credit_card.issuer_country == 'Brazil' and self.currency != 'BRL':
                self.iof_amount = (self.amount * self.credit_card.iof_percent) / 100
            else:
                self.iof_amount = Decimal('0.00')


# Specialized factories for specific scenarios
class BrazilianCreditCardFactory(CreditCardFactory):
    """Factory for Brazilian credit cards with typical IOF rates."""
    
    issuer_country = 'Brazil'
    currency = factory.Iterator(['BRL', 'USD'])
    iof_percent = factory.LazyFunction(lambda: Decimal(random.uniform(6.0, 6.38)).quantize(Decimal('0.01')))


class PortugueseCreditCardFactory(CreditCardFactory):
    """Factory for Portuguese credit cards."""
    
    issuer_country = 'Portugal'
    currency = 'EUR'
    iof_percent = Decimal('0.00')  # No IOF for Portuguese cards


class UniversityPaymentFactory(FixedPaymentFactory):
    """Factory for university payments (typically Brazilian)."""
    
    country = 'Brazil'
    description = factory.LazyFunction(lambda: random.choice([
        'University Tuition',
        'Course Materials',
        'Student Services',
        'Library Fee',
        'Laboratory Fee'
    ]))
    currency = 'BRL'
    frequency = 'monthly'
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(500, 2000)).quantize(Decimal('0.01')))


class RentPaymentFactory(FixedPaymentFactory):
    """Factory for rent payments (typically Portuguese)."""
    
    country = 'Portugal'
    description = 'Rent'
    currency = 'EUR'
    frequency = 'monthly'
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(400, 1200)).quantize(Decimal('0.01')))


class FoodExpenseFactory(VariablePaymentFactory):
    """Factory for food-related expenses."""
    
    description = factory.LazyFunction(lambda: random.choice([
        'Groceries',
        'Restaurant',
        'Coffee',
        'Lunch',
        'Dinner',
        'Takeout',
        'Snacks'
    ]))
    category = 'food'
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(5, 100)).quantize(Decimal('0.01')))


class TransportExpenseFactory(VariablePaymentFactory):
    """Factory for transport-related expenses."""
    
    description = factory.LazyFunction(lambda: random.choice([
        'Metro Ticket',
        'Bus Fare',
        'Taxi',
        'Uber',
        'Gas',
        'Parking',
        'Train Ticket'
    ]))
    category = 'transport'
    amount = factory.LazyFunction(lambda: Decimal(random.uniform(2, 50)).quantize(Decimal('0.01')))


# Factory for realistic exchange rates
class RealisticExchangeRateFactory(ExchangeRateFactory):
    """Factory for realistic exchange rates."""
    
    @factory.post_generation
    def set_realistic_rates(self, create, extracted, **kwargs):
        """Set realistic exchange rates based on currency pairs."""
        if self.from_currency == 'BRL' and self.to_currency == 'EUR':
            self.rate = Decimal(random.uniform(0.15, 0.20)).quantize(Decimal('0.000001'))
        elif self.from_currency == 'EUR' and self.to_currency == 'BRL':
            self.rate = Decimal(random.uniform(5.0, 6.5)).quantize(Decimal('0.000001'))
        elif self.from_currency == 'BRL' and self.to_currency == 'USD':
            self.rate = Decimal(random.uniform(0.18, 0.22)).quantize(Decimal('0.000001'))
        elif self.from_currency == 'USD' and self.to_currency == 'BRL':
            self.rate = Decimal(random.uniform(4.5, 5.5)).quantize(Decimal('0.000001'))
        elif self.from_currency == 'EUR' and self.to_currency == 'USD':
            self.rate = Decimal(random.uniform(1.05, 1.15)).quantize(Decimal('0.000001'))
        elif self.from_currency == 'USD' and self.to_currency == 'EUR':
            self.rate = Decimal(random.uniform(0.85, 0.95)).quantize(Decimal('0.000001'))
        else:
            # Default random rate for other combinations
            self.rate = Decimal(random.uniform(0.1, 10.0)).quantize(Decimal('0.000001'))


class CreditCardInvoiceFactory(DjangoModelFactory):
    """Factory for creating credit card invoices."""
    
    class Meta:
        model = CreditCardInvoice
    
    credit_card = factory.SubFactory(CreditCardFactory)
    
    # Create realistic billing periods (monthly)
    start_date = factory.LazyFunction(lambda: date.today().replace(day=1))
    end_date = factory.LazyFunction(lambda: 
        (date.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    )
    
    # Most invoices are open, some are closed
    is_closed = factory.Iterator([False, False, False, True])  # 75% open invoices
    



class OpenCreditCardInvoiceFactory(CreditCardInvoiceFactory):
    """Factory for open credit card invoices."""
    
    is_closed = False


class ClosedCreditCardInvoiceFactory(CreditCardInvoiceFactory):
    """Factory for closed credit card invoices."""
    
    is_closed = True


class PaymentStatusFactory(DjangoModelFactory):
    """Factory for creating payment status records."""
    
    class Meta:
        model = PaymentStatus
    
    # Randomly choose between fixed, variable, and credit card payment
    payment_type = factory.Iterator(['fixed', 'variable', 'credit_card'])
    
    # Month and year for the payment
    month_year = factory.LazyFunction(lambda: date.today().replace(day=1) - timedelta(days=random.randint(0, 365)))
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=random.randint(1, 30)))
    
    # Status and payment tracking
    status = factory.Iterator(['pending', 'paid', 'overdue'])
    is_paid = factory.LazyAttribute(lambda obj: obj.status == 'paid')
    paid_date = factory.LazyAttribute(lambda obj: date.today() if obj.is_paid else None)
    
    # Amount tracking
    expected_amount = factory.LazyFunction(lambda: Decimal(random.uniform(50, 2000)).quantize(Decimal('0.01')))
    actual_amount = factory.LazyFunction(lambda: Decimal(random.uniform(50, 2000)).quantize(Decimal('0.01')))
    currency = factory.Iterator(['BRL', 'EUR', 'USD'])
    
    # Notes
    notes = factory.LazyFunction(lambda: random.choice([
        'Payment completed',
        'Pending confirmation',
        'Late payment',
        'Partial payment',
        'Payment scheduled',
        'Payment cancelled',
        None
    ]))
    
    @factory.post_generation
    def link_payment(self, create, extracted, **kwargs):
        """Link to either a fixed, variable, or credit card invoice payment."""
        if self.payment_type == 'fixed':
            # Create or get a fixed payment
            if not hasattr(self, 'fixed_payment') or not self.fixed_payment:
                self.fixed_payment = FixedPaymentFactory()
                self.expected_amount = self.fixed_payment.amount
                self.currency = self.fixed_payment.currency
        elif self.payment_type == 'variable':
            # Create or get a variable payment
            if not hasattr(self, 'variable_payment') or not self.variable_payment:
                self.variable_payment = VariablePaymentFactory()
                self.expected_amount = self.variable_payment.amount
                self.currency = self.variable_payment.currency
        elif self.payment_type == 'credit_card':
            # Create or get a credit card invoice
            if not hasattr(self, 'credit_card_invoice') or not self.credit_card_invoice:
                self.credit_card_invoice = CreditCardInvoiceFactory()
                self.expected_amount = self.credit_card_invoice.total_amount
                self.currency = self.credit_card_invoice.credit_card.currency


class FixedPaymentStatusFactory(PaymentStatusFactory):
    """Factory for payment status linked to fixed payments."""
    
    payment_type = 'fixed'
    fixed_payment = factory.SubFactory(FixedPaymentFactory)
    
    @factory.post_generation
    def set_fixed_payment_data(self, create, extracted, **kwargs):
        """Set expected amount and currency from fixed payment."""
        if self.fixed_payment:
            self.expected_amount = self.fixed_payment.amount
            self.currency = self.fixed_payment.currency


class VariablePaymentStatusFactory(PaymentStatusFactory):
    """Factory for payment status linked to variable payments."""
    
    payment_type = 'variable'
    variable_payment = factory.SubFactory(VariablePaymentFactory)
    
    @factory.post_generation
    def set_variable_payment_data(self, create, extracted, **kwargs):
        """Set expected amount and currency from variable payment."""
        if self.variable_payment:
            self.expected_amount = self.variable_payment.amount
            self.currency = self.variable_payment.currency


class CreditCardInvoicePaymentStatusFactory(PaymentStatusFactory):
    """Factory for payment status linked to credit card invoices."""
    
    payment_type = 'credit_card'
    credit_card_invoice = factory.SubFactory(CreditCardInvoiceFactory)
    
    @factory.post_generation
    def set_credit_card_invoice_data(self, create, extracted, **kwargs):
        """Set expected amount and currency from credit card invoice."""
        if self.credit_card_invoice:
            self.expected_amount = self.credit_card_invoice.total_amount
            self.currency = self.credit_card_invoice.credit_card.currency 