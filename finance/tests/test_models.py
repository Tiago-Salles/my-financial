from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ..models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment,
    PaymentStatus,
    CreditCardInvoice
)
from ..factories import (
    UserFinancialProfileFactory,
    CreditCardFactory,
    ExchangeRateFactory,
    FixedPaymentFactory,
    VariablePaymentFactory,
    PaymentStatusFactory,
    CreditCardInvoiceFactory,
    BrazilianCreditCardFactory,
    PortugueseCreditCardFactory,
    UniversityPaymentFactory,
    RentPaymentFactory,
    FoodExpenseFactory,
    TransportExpenseFactory,
    RealisticExchangeRateFactory,
    OpenCreditCardInvoiceFactory,
    ClosedCreditCardInvoiceFactory,
    FixedPaymentStatusFactory,
    VariablePaymentStatusFactory,
    CreditCardInvoicePaymentStatusFactory
)


class UserFinancialProfileModelTest(TestCase):
    """Test cases for UserFinancialProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_financial_profile(self):
        """Test creating a user financial profile."""
        profile = UserFinancialProfileFactory(user=self.user)
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.name)
        self.assertIn(profile.base_currency, ['BRL', 'EUR'])
        self.assertGreaterEqual(profile.monthly_income_brl, 0)
        self.assertGreaterEqual(profile.monthly_income_eur, 0)
    
    def test_total_monthly_income_base_currency_eur(self):
        """Test total monthly income calculation for EUR base currency."""
        profile = UserFinancialProfileFactory(
            base_currency='EUR',
            monthly_income_eur=Decimal('5000.00'),
            monthly_income_brl=Decimal('25000.00')
        )
        self.assertEqual(profile.total_monthly_income_base_currency, Decimal('5000.00'))
    
    def test_total_monthly_income_base_currency_brl(self):
        """Test total monthly income calculation for BRL base currency."""
        profile = UserFinancialProfileFactory(
            base_currency='BRL',
            monthly_income_eur=Decimal('5000.00'),
            monthly_income_brl=Decimal('25000.00')
        )
        self.assertEqual(profile.total_monthly_income_base_currency, Decimal('25000.00'))
    
    def test_string_representation(self):
        """Test string representation of the model."""
        profile = UserFinancialProfileFactory()
        expected = f"{profile.name} - {profile.base_currency}"
        self.assertEqual(str(profile), expected)


class CreditCardModelTest(TestCase):
    """Test cases for CreditCard model."""
    
    def test_create_credit_card(self):
        """Test creating a credit card."""
        card = CreditCardFactory()
        self.assertIsNotNone(card.id)
        self.assertIn(card.issuer_country, ['Brazil', 'Portugal'])
        self.assertIn(card.currency, ['BRL', 'EUR', 'USD'])
        self.assertGreaterEqual(card.fx_fee_percent, 0)
        self.assertGreaterEqual(card.iof_percent, 0)
        self.assertIsNotNone(card.cardholder_name)
        self.assertIsNotNone(card.final_digits)
        self.assertIsInstance(card.is_active, bool)
    
    def test_brazilian_credit_card_factory(self):
        """Test Brazilian credit card factory with typical IOF rates."""
        card = BrazilianCreditCardFactory()
        self.assertEqual(card.issuer_country, 'Brazil')
        self.assertIn(card.currency, ['BRL', 'USD'])
        self.assertGreaterEqual(card.iof_percent, 6.0)
        self.assertLessEqual(card.iof_percent, 6.38)
    
    def test_portuguese_credit_card_factory(self):
        """Test Portuguese credit card factory."""
        card = PortugueseCreditCardFactory()
        self.assertEqual(card.issuer_country, 'Portugal')
        self.assertEqual(card.currency, 'EUR')
        self.assertEqual(card.iof_percent, Decimal('0.00'))
    
    def test_string_representation(self):
        """Test string representation of the model."""
        card = CreditCardFactory()
        expected = f"{card.cardholder_name} - {card.final_digits} ({card.currency})"
        self.assertEqual(str(card), expected)


class ExchangeRateModelTest(TestCase):
    """Test cases for ExchangeRate model."""
    
    def test_create_exchange_rate(self):
        """Test creating an exchange rate."""
        rate = ExchangeRateFactory()
        self.assertIsNotNone(rate.id)
        self.assertIn(rate.from_currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(rate.to_currency, ['BRL', 'EUR', 'USD'])
        self.assertGreater(rate.rate, 0)
        self.assertIsInstance(rate.date, date)
    
    def test_unique_together_constraint(self):
        """Test unique together constraint for from_currency, to_currency, and date."""
        rate1 = ExchangeRateFactory(
            from_currency='BRL',
            to_currency='EUR',
            date=date.today(),
            rate=Decimal('5.50')
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with self.assertRaises(IntegrityError):
            ExchangeRateFactory(
                from_currency='BRL',
                to_currency='EUR',
                date=date.today(),
                rate=Decimal('5.60')
            )
    
    def test_realistic_exchange_rate_factory(self):
        """Test realistic exchange rate factory."""
        rate = RealisticExchangeRateFactory()
        self.assertIsNotNone(rate.id)
        # Test that same currency has rate of 1.0
        if rate.from_currency == rate.to_currency:
            self.assertEqual(rate.rate, Decimal('1.000000'))
    
    def test_string_representation(self):
        """Test string representation of the model."""
        rate = ExchangeRateFactory()
        expected = f"{rate.from_currency}/{rate.to_currency}: {rate.rate} ({rate.date})"
        self.assertEqual(str(rate), expected)


class FixedPaymentModelTest(TestCase):
    """Test cases for FixedPayment model."""
    
    def test_create_fixed_payment(self):
        """Test creating a fixed payment."""
        payment = FixedPaymentFactory()
        self.assertIsNotNone(payment.id)
        self.assertIn(payment.country, ['Brazil', 'Portugal'])
        self.assertIsNotNone(payment.description)
        self.assertGreater(payment.amount, 0)
        self.assertIn(payment.currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(payment.frequency, ['monthly', 'yearly'])
        self.assertIsInstance(payment.is_active, bool)
    
    def test_is_currently_active_property(self):
        """Test is_currently_active property."""
        # Active payment with future end date
        active_payment = FixedPaymentFactory(
            is_active=True,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30)
        )
        self.assertTrue(active_payment.is_currently_active)
        
        # Inactive payment
        inactive_payment = FixedPaymentFactory(is_active=False)
        self.assertFalse(inactive_payment.is_currently_active)
        
        # Active payment with past end date
        expired_payment = FixedPaymentFactory(
            is_active=True,
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=1)
        )
        self.assertFalse(expired_payment.is_currently_active)
    
    def test_university_payment_factory(self):
        """Test university payment factory."""
        payment = UniversityPaymentFactory()
        self.assertEqual(payment.country, 'Brazil')
        self.assertEqual(payment.currency, 'BRL')
        self.assertEqual(payment.frequency, 'monthly')
        self.assertGreaterEqual(payment.amount, 500)
        self.assertLessEqual(payment.amount, 2000)
    
    def test_rent_payment_factory(self):
        """Test rent payment factory."""
        payment = RentPaymentFactory()
        self.assertEqual(payment.country, 'Portugal')
        self.assertEqual(payment.description, 'Rent')
        self.assertEqual(payment.currency, 'EUR')
        self.assertEqual(payment.frequency, 'monthly')
        self.assertGreaterEqual(payment.amount, 400)
        self.assertLessEqual(payment.amount, 1200)
    
    def test_string_representation(self):
        """Test string representation of the model."""
        payment = FixedPaymentFactory()
        expected = f"{payment.description} ({payment.currency})"
        self.assertEqual(str(payment), expected)


class VariablePaymentModelTest(TestCase):
    """Test cases for VariablePayment model."""
    
    def test_create_variable_payment(self):
        """Test creating a variable payment."""
        payment = VariablePaymentFactory()
        self.assertIsNotNone(payment.id)
        self.assertIsInstance(payment.date, date)
        self.assertIn(payment.country, ['Brazil', 'Portugal'])
        self.assertIsNotNone(payment.description)
        self.assertGreater(payment.amount, 0)
        self.assertIn(payment.currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(payment.category, [
            'food', 'transport', 'entertainment', 'health', 
            'education', 'shopping', 'bills', 'other'
        ])
        self.assertIsInstance(payment.linked_credit_card, bool)
    
    def test_total_amount_with_fees_property(self):
        """Test total_amount_with_fees property."""
        payment = VariablePaymentFactory(
            amount=Decimal('100.00'),
            fx_fee_amount=Decimal('5.00'),
            iof_amount=Decimal('2.00')
        )
        expected_total = Decimal('107.00')  # 100 + 5 + 2
        self.assertEqual(payment.total_amount_with_fees, expected_total)
    
    def test_save_method_calculates_fees(self):
        """Test that save method calculates fees for credit card payments."""
        credit_card = CreditCardFactory(
            fx_fee_percent=Decimal('2.5'),
            iof_percent=Decimal('6.38')
        )
        payment = VariablePaymentFactory(
            amount=Decimal('100.00'),
            linked_credit_card=True,
            credit_card=credit_card
        )
        
        # Fees should be calculated automatically
        expected_fx_fee = Decimal('2.50')  # 2.5% of 100
        expected_iof = Decimal('6.38')     # 6.38% of 100
        self.assertEqual(payment.fx_fee_amount, expected_fx_fee)
        self.assertEqual(payment.iof_amount, expected_iof)
    
    def test_food_expense_factory(self):
        """Test food expense factory."""
        payment = FoodExpenseFactory()
        self.assertEqual(payment.category, 'food')
        self.assertIn(payment.description, [
            'Groceries', 'Restaurant', 'Coffee', 'Lunch', 
            'Dinner', 'Takeout', 'Snacks'
        ])
        self.assertGreaterEqual(payment.amount, 5)
        self.assertLessEqual(payment.amount, 100)
    
    def test_transport_expense_factory(self):
        """Test transport expense factory."""
        payment = TransportExpenseFactory()
        self.assertEqual(payment.category, 'transport')
        self.assertIn(payment.description, [
            'Metro Ticket', 'Bus Fare', 'Taxi', 'Uber', 
            'Gas', 'Parking', 'Train Ticket'
        ])
        self.assertGreaterEqual(payment.amount, 2)
        self.assertLessEqual(payment.amount, 50)
    
    def test_string_representation(self):
        """Test string representation of the model."""
        payment = VariablePaymentFactory()
        expected = f"{payment.description} - {payment.amount} {payment.currency}"
        self.assertEqual(str(payment), expected)


class PaymentStatusModelTest(TestCase):
    """Test cases for PaymentStatus model."""
    
    def test_create_payment_status(self):
        """Test creating a payment status."""
        status = PaymentStatusFactory()
        self.assertIsNotNone(status.id)
        self.assertIn(status.payment_type, ['fixed', 'variable', 'credit_card'])
        self.assertIsInstance(status.month_year, date)
        self.assertIsInstance(status.due_date, date)
        self.assertIn(status.status, ['pending', 'paid', 'overdue', 'cancelled'])
        self.assertIsInstance(status.is_paid, bool)
        self.assertGreater(status.expected_amount, 0)
        self.assertIn(status.currency, ['BRL', 'EUR', 'USD'])
    
    def test_save_method_sets_payment_type(self):
        """Test that save method sets payment type based on linked payment."""
        fixed_payment = FixedPaymentFactory()
        status = PaymentStatusFactory(
            fixed_payment=fixed_payment,
            variable_payment=None,
            credit_card_invoice=None
        )
        self.assertEqual(status.payment_type, 'fixed')
        
        variable_payment = VariablePaymentFactory()
        status = PaymentStatusFactory(
            fixed_payment=None,
            variable_payment=variable_payment,
            credit_card_invoice=None
        )
        self.assertEqual(status.payment_type, 'variable')
        
        credit_card_invoice = CreditCardInvoiceFactory()
        status = PaymentStatusFactory(
            fixed_payment=None,
            variable_payment=None,
            credit_card_invoice=credit_card_invoice
        )
        self.assertEqual(status.payment_type, 'credit_card')
    
    def test_payment_description_property(self):
        """Test payment_description property."""
        fixed_payment = FixedPaymentFactory(description="Rent")
        status = FixedPaymentStatusFactory(fixed_payment=fixed_payment)
        self.assertEqual(status.payment_description, "Rent")
        
        variable_payment = VariablePaymentFactory(description="Groceries")
        status = VariablePaymentStatusFactory(variable_payment=variable_payment)
        self.assertEqual(status.payment_description, "Groceries")
        
        credit_card = CreditCardFactory(cardholder_name="John Doe")
        invoice = CreditCardInvoiceFactory(credit_card=credit_card)
        status = CreditCardInvoicePaymentStatusFactory(credit_card_invoice=invoice)
        self.assertEqual(status.payment_description, "John Doe Credit Card")
    
    def test_payment_country_property(self):
        """Test payment_country property."""
        fixed_payment = FixedPaymentFactory(country="Brazil")
        status = FixedPaymentStatusFactory(fixed_payment=fixed_payment)
        self.assertEqual(status.payment_country, "Brazil")
        
        variable_payment = VariablePaymentFactory(country="Portugal")
        status = VariablePaymentStatusFactory(variable_payment=variable_payment)
        self.assertEqual(status.payment_country, "Portugal")
        
        credit_card = CreditCardFactory(issuer_country="Brazil")
        invoice = CreditCardInvoiceFactory(credit_card=credit_card)
        status = CreditCardInvoicePaymentStatusFactory(credit_card_invoice=invoice)
        self.assertEqual(status.payment_country, "Brazil")
    
    def test_is_overdue_property(self):
        """Test is_overdue property."""
        # Not overdue
        status = PaymentStatusFactory(
            due_date=date.today() + timedelta(days=5),
            status='pending'
        )
        self.assertFalse(status.is_overdue)
        
        # Overdue
        status = PaymentStatusFactory(
            due_date=date.today() - timedelta(days=5),
            status='pending'
        )
        self.assertTrue(status.is_overdue)
        
        # Paid (not overdue even if past due date)
        status = PaymentStatusFactory(
            due_date=date.today() - timedelta(days=5),
            status='paid'
        )
        self.assertFalse(status.is_overdue)
    
    def test_unique_together_constraints(self):
        """Test unique together constraints."""
        fixed_payment = FixedPaymentFactory()
        month_year = date.today().replace(day=1)
        
        # Create first payment status
        PaymentStatusFactory(
            fixed_payment=fixed_payment,
            month_year=month_year
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with self.assertRaises(IntegrityError):
            PaymentStatusFactory(
                fixed_payment=fixed_payment,
                month_year=month_year
            )
    
    def test_string_representation(self):
        """Test string representation of the model."""
        status = PaymentStatusFactory()
        expected = f"{status.payment_type.title()} - {status.month_year.strftime('%B %Y')}"
        self.assertEqual(str(status), expected)


class CreditCardInvoiceModelTest(TestCase):
    """Test cases for CreditCardInvoice model."""
    
    def test_create_credit_card_invoice(self):
        """Test creating a credit card invoice."""
        invoice = CreditCardInvoiceFactory()
        self.assertIsNotNone(invoice.id)
        self.assertIsInstance(invoice.credit_card, CreditCard)
        self.assertIsInstance(invoice.start_date, date)
        self.assertIsInstance(invoice.end_date, date)
        self.assertIsInstance(invoice.is_closed, bool)
    
    def test_total_amount_property(self):
        """Test total_amount property."""
        invoice = CreditCardInvoiceFactory()
        # Create some variable payments linked to this invoice's credit card
        VariablePaymentFactory.create_batch(
            3,
            credit_card=invoice.credit_card,
            date=invoice.start_date + timedelta(days=5)
        )
        
        # Refresh from database to get updated total
        invoice.refresh_from_db()
        self.assertGreater(invoice.total_amount, 0)
    
    def test_purchases_count_property(self):
        """Test purchases_count property."""
        invoice = CreditCardInvoiceFactory()
        # Create some variable payments linked to this invoice's credit card
        VariablePaymentFactory.create_batch(
            5,
            credit_card=invoice.credit_card,
            date=invoice.start_date + timedelta(days=5)
        )
        
        # Refresh from database to get updated count
        invoice.refresh_from_db()
        self.assertEqual(invoice.purchases_count, 5)
    
    def test_total_with_fees_property(self):
        """Test total_with_fees property."""
        invoice = CreditCardInvoiceFactory()
        # Create payments with fees
        VariablePaymentFactory.create_batch(
            2,
            credit_card=invoice.credit_card,
            date=invoice.start_date + timedelta(days=5),
            fx_fee_amount=Decimal('5.00'),
            iof_amount=Decimal('2.00')
        )
        
        # Refresh from database
        invoice.refresh_from_db()
        self.assertGreater(invoice.total_with_fees, invoice.total_amount)
    
    def test_billing_period_days_property(self):
        """Test billing_period_days property."""
        start_date = date.today().replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        invoice = CreditCardInvoiceFactory(
            start_date=start_date,
            end_date=end_date
        )
        
        expected_days = (end_date - start_date).days + 1
        self.assertEqual(invoice.billing_period_days, expected_days)
    
    def test_close_invoice_method(self):
        """Test close_invoice method."""
        invoice = CreditCardInvoiceFactory(is_closed=False)
        self.assertFalse(invoice.is_closed)
        
        invoice.close_invoice()
        self.assertTrue(invoice.is_closed)
    
    def test_get_open_invoice_for_card(self):
        """Test get_open_invoice_for_card class method."""
        credit_card = CreditCardFactory()
        
        # Create closed invoice
        ClosedCreditCardInvoiceFactory(credit_card=credit_card)
        
        # Create open invoice
        open_invoice = OpenCreditCardInvoiceFactory(credit_card=credit_card)
        
        # Should return the open invoice
        result = CreditCardInvoice.get_open_invoice_for_card(credit_card)
        self.assertEqual(result, open_invoice)
    
    def test_get_or_create_open_invoice(self):
        """Test get_or_create_open_invoice class method."""
        credit_card = CreditCardFactory()
        
        # First call should create a new invoice
        invoice1 = CreditCardInvoice.get_or_create_open_invoice(credit_card)
        self.assertIsNotNone(invoice1)
        self.assertFalse(invoice1.is_closed)
        
        # Second call should return the same invoice
        invoice2 = CreditCardInvoice.get_or_create_open_invoice(credit_card)
        self.assertEqual(invoice1, invoice2)
    
    def test_unique_together_constraint(self):
        """Test unique together constraint."""
        credit_card = CreditCardFactory()
        start_date = date.today().replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Create first invoice
        CreditCardInvoiceFactory(
            credit_card=credit_card,
            start_date=start_date,
            end_date=end_date
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with self.assertRaises(IntegrityError):
            CreditCardInvoiceFactory(
                credit_card=credit_card,
                start_date=start_date,
                end_date=end_date
            )
    
    def test_string_representation(self):
        """Test string representation of the model."""
        invoice = CreditCardInvoiceFactory()
        expected = f"{invoice.credit_card.cardholder_name} - {invoice.start_date} to {invoice.end_date}"
        self.assertEqual(str(invoice), expected) 