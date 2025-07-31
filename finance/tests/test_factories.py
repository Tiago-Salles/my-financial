from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
import random

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


class UserFinancialProfileFactoryTest(TestCase):
    """Test cases for UserFinancialProfileFactory."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_financial_profile(self):
        """Test creating a user financial profile with factory."""
        profile = UserFinancialProfileFactory()
        
        self.assertIsInstance(profile, UserFinancialProfile)
        self.assertIsNotNone(profile.id)
        self.assertIsNotNone(profile.name)
        self.assertIn(profile.base_currency, ['BRL', 'EUR'])
        self.assertGreaterEqual(profile.monthly_income_brl, 0)
        self.assertGreaterEqual(profile.monthly_income_eur, 0)
    
    def test_create_user_financial_profile_with_user(self):
        """Test creating a user financial profile with specific user."""
        profile = UserFinancialProfileFactory(user=self.user)
        
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.name)
    
    def test_create_multiple_profiles(self):
        """Test creating multiple profiles with different data."""
        profiles = UserFinancialProfileFactory.create_batch(5)
        
        self.assertEqual(len(profiles), 5)
        # Check that profiles have different names
        names = [p.name for p in profiles]
        self.assertEqual(len(set(names)), 5)
        
        # Check that currencies are distributed
        currencies = [p.base_currency for p in profiles]
        self.assertTrue('BRL' in currencies or 'EUR' in currencies)


class CreditCardFactoryTest(TestCase):
    """Test cases for CreditCardFactory."""
    
    def test_create_credit_card(self):
        """Test creating a credit card with factory."""
        card = CreditCardFactory()
        
        self.assertIsInstance(card, CreditCard)
        self.assertIsNotNone(card.id)
        self.assertIn(card.issuer_country, ['Brazil', 'Portugal'])
        self.assertIn(card.currency, ['BRL', 'EUR', 'USD'])
        self.assertGreaterEqual(card.fx_fee_percent, 0)
        self.assertGreaterEqual(card.iof_percent, 0)
        self.assertIsNotNone(card.cardholder_name)
        self.assertIsNotNone(card.final_digits)
        self.assertIsInstance(card.is_active, bool)
    
    def test_create_multiple_cards(self):
        """Test creating multiple credit cards."""
        cards = CreditCardFactory.create_batch(10)
        
        self.assertEqual(len(cards), 10)
        # Check that cards have different names
        names = [c.cardholder_name for c in cards]
        self.assertEqual(len(set(names)), 10)
        
        # Check that final digits are different
        digits = [c.final_digits for c in cards]
        self.assertEqual(len(set(digits)), 10)
    
    def test_brazilian_credit_card_factory(self):
        """Test Brazilian credit card factory."""
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


class ExchangeRateFactoryTest(TestCase):
    """Test cases for ExchangeRateFactory."""
    
    def test_create_exchange_rate(self):
        """Test creating an exchange rate with factory."""
        rate = ExchangeRateFactory()
        
        self.assertIsInstance(rate, ExchangeRate)
        self.assertIsNotNone(rate.id)
        self.assertIn(rate.from_currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(rate.to_currency, ['BRL', 'EUR', 'USD'])
        self.assertGreater(rate.rate, 0)
        self.assertIsInstance(rate.date, date)
    
    def test_create_multiple_rates(self):
        """Test creating multiple exchange rates."""
        rates = ExchangeRateFactory.create_batch(10)
        
        self.assertEqual(len(rates), 10)
        # Check that rates have different dates
        dates = [r.date for r in rates]
        self.assertEqual(len(set(dates)), 10)
    
    def test_realistic_exchange_rate_factory(self):
        """Test realistic exchange rate factory."""
        rate = RealisticExchangeRateFactory()
        
        self.assertIsInstance(rate, ExchangeRate)
        # If same currency, rate should be 1.0
        if rate.from_currency == rate.to_currency:
            self.assertEqual(rate.rate, Decimal('1.000000'))
        else:
            # Check realistic rate ranges
            self.assertGreater(rate.rate, 0)
            self.assertLess(rate.rate, 10)


class FixedPaymentFactoryTest(TestCase):
    """Test cases for FixedPaymentFactory."""
    
    def test_create_fixed_payment(self):
        """Test creating a fixed payment with factory."""
        payment = FixedPaymentFactory()
        
        self.assertIsInstance(payment, FixedPayment)
        self.assertIsNotNone(payment.id)
        self.assertIn(payment.country, ['Brazil', 'Portugal'])
        self.assertIsNotNone(payment.description)
        self.assertGreater(payment.amount, 0)
        self.assertIn(payment.currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(payment.frequency, ['monthly', 'yearly'])
        self.assertIsInstance(payment.is_active, bool)
    
    def test_create_multiple_payments(self):
        """Test creating multiple fixed payments."""
        payments = FixedPaymentFactory.create_batch(10)
        
        self.assertEqual(len(payments), 10)
        # Check that payments have different descriptions
        descriptions = [p.description for p in payments]
        self.assertEqual(len(set(descriptions)), 10)
    
    def test_university_payment_factory(self):
        """Test university payment factory."""
        payment = UniversityPaymentFactory()
        
        self.assertEqual(payment.country, 'Brazil')
        self.assertEqual(payment.currency, 'BRL')
        self.assertEqual(payment.frequency, 'monthly')
        self.assertGreaterEqual(payment.amount, 500)
        self.assertLessEqual(payment.amount, 2000)
        self.assertIn(payment.description, [
            'University Tuition', 'Course Materials', 'Student Services',
            'Library Fee', 'Laboratory Fee'
        ])
    
    def test_rent_payment_factory(self):
        """Test rent payment factory."""
        payment = RentPaymentFactory()
        
        self.assertEqual(payment.country, 'Portugal')
        self.assertEqual(payment.description, 'Rent')
        self.assertEqual(payment.currency, 'EUR')
        self.assertEqual(payment.frequency, 'monthly')
        self.assertGreaterEqual(payment.amount, 400)
        self.assertLessEqual(payment.amount, 1200)


class VariablePaymentFactoryTest(TestCase):
    """Test cases for VariablePaymentFactory."""
    
    def test_create_variable_payment(self):
        """Test creating a variable payment with factory."""
        payment = VariablePaymentFactory()
        
        self.assertIsInstance(payment, CreditCard)
        self.assertIsNotNone(payment.id)
        self.assertIsInstance(payment.date, date)
        self.assertIn(payment.country, ['Brazil', 'Portugal'])
        self.assertIsNotNone(payment.description)
        self.assertGreater(payment.amount, 0)
        self.assertIn(payment.currency, ['BRL', 'EUR', 'USD'])
        self.assertIn(payment.category, [
            'food', 'transport', 'entertainment', 'shopping', 
            'health', 'education', 'utilities', 'other'
        ])
        self.assertIsInstance(payment.linked_credit_card, bool)
    
    def test_create_multiple_payments(self):
        """Test creating multiple variable payments."""
        payments = VariablePaymentFactory.create_batch(10)
        
        self.assertEqual(len(payments), 10)
        # Check that payments have different dates
        dates = [p.date for p in payments]
        self.assertEqual(len(set(dates)), 10)
    
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


class CreditCardInvoiceFactoryTest(TestCase):
    """Test cases for CreditCardInvoiceFactory."""
    
    def test_create_credit_card_invoice(self):
        """Test creating a credit card invoice with factory."""
        invoice = CreditCardInvoiceFactory()
        
        self.assertIsInstance(invoice, CreditCardInvoice)
        self.assertIsNotNone(invoice.id)
        self.assertIsInstance(invoice.credit_card, CreditCard)
        self.assertIsInstance(invoice.start_date, date)
        self.assertIsInstance(invoice.end_date, date)
        self.assertIsInstance(invoice.is_closed, bool)
    
    def test_create_multiple_invoices(self):
        """Test creating multiple credit card invoices."""
        invoices = CreditCardInvoiceFactory.create_batch(5)
        
        self.assertEqual(len(invoices), 5)
        # Check that invoices have different dates
        start_dates = [i.start_date for i in invoices]
        self.assertEqual(len(set(start_dates)), 5)
    
    def test_open_credit_card_invoice_factory(self):
        """Test open credit card invoice factory."""
        invoice = OpenCreditCardInvoiceFactory()
        
        self.assertFalse(invoice.is_closed)
        self.assertIsInstance(invoice.credit_card, CreditCard)
    
    def test_closed_credit_card_invoice_factory(self):
        """Test closed credit card invoice factory."""
        invoice = ClosedCreditCardInvoiceFactory()
        
        self.assertTrue(invoice.is_closed)
        self.assertIsInstance(invoice.credit_card, CreditCard)


class PaymentStatusFactoryTest(TestCase):
    """Test cases for PaymentStatusFactory."""
    
    def test_create_payment_status(self):
        """Test creating a payment status with factory."""
        status_obj = PaymentStatusFactory()
        
        self.assertIsInstance(status_obj, PaymentStatus)
        self.assertIsNotNone(status_obj.id)
        self.assertIn(status_obj.payment_type, ['fixed', 'variable', 'credit_card'])
        self.assertIsInstance(status_obj.month_year, date)
        self.assertIsInstance(status_obj.due_date, date)
        self.assertIn(status_obj.status, ['pending', 'paid', 'overdue', 'cancelled'])
        self.assertIsInstance(status_obj.is_paid, bool)
        self.assertGreater(status_obj.expected_amount, 0)
        self.assertIn(status_obj.currency, ['BRL', 'EUR', 'USD'])
    
    def test_create_multiple_statuses(self):
        """Test creating multiple payment statuses."""
        statuses = PaymentStatusFactory.create_batch(10)
        
        self.assertEqual(len(statuses), 10)
        # Check that statuses have different months
        months = [s.month_year for s in statuses]
        self.assertEqual(len(set(months)), 10)
    
    def test_fixed_payment_status_factory(self):
        """Test fixed payment status factory."""
        status_obj = FixedPaymentStatusFactory()
        
        self.assertEqual(status_obj.payment_type, 'fixed')
        self.assertIsInstance(status_obj.fixed_payment, FixedPayment)
        self.assertIsNone(status_obj.variable_payment)
        self.assertIsNone(status_obj.credit_card_invoice)
    
    def test_variable_payment_status_factory(self):
        """Test variable payment status factory."""
        status_obj = VariablePaymentStatusFactory()
        
        self.assertEqual(status_obj.payment_type, 'variable')
        self.assertIsInstance(status_obj.variable_payment, VariablePayment)
        self.assertIsNone(status_obj.fixed_payment)
        self.assertIsNone(status_obj.credit_card_invoice)
    
    def test_credit_card_invoice_payment_status_factory(self):
        """Test credit card invoice payment status factory."""
        status_obj = CreditCardInvoicePaymentStatusFactory()
        
        self.assertEqual(status_obj.payment_type, 'credit_card')
        self.assertIsInstance(status_obj.credit_card_invoice, CreditCardInvoice)
        self.assertIsNone(status_obj.fixed_payment)
        self.assertIsNone(status_obj.variable_payment)


class FactoryIntegrationTest(TestCase):
    """Integration tests for factories working together."""
    
    def test_create_complete_financial_scenario(self):
        """Test creating a complete financial scenario with all models."""
        # Create user and profile
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = UserFinancialProfileFactory(user=user)
        
        # Create credit cards
        brazilian_card = BrazilianCreditCardFactory()
        portuguese_card = PortugueseCreditCardFactory()
        
        # Create exchange rates
        exchange_rates = RealisticExchangeRateFactory.create_batch(3)
        
        # Create fixed payments
        university_payment = UniversityPaymentFactory()
        rent_payment = RentPaymentFactory()
        
        # Create variable payments
        food_expenses = FoodExpenseFactory.create_batch(5)
        transport_expenses = TransportExpenseFactory.create_batch(3)
        
        # Create credit card invoices
        open_invoice = OpenCreditCardInvoiceFactory(credit_card=brazilian_card)
        closed_invoice = ClosedCreditCardInvoiceFactory(credit_card=portuguese_card)
        
        # Create payment statuses
        fixed_status = FixedPaymentStatusFactory(fixed_payment=university_payment)
        variable_status = VariablePaymentStatusFactory(variable_payment=food_expenses[0])
        invoice_status = CreditCardInvoicePaymentStatusFactory(credit_card_invoice=open_invoice)
        
        # Verify all objects were created correctly
        self.assertIsInstance(profile, UserFinancialProfile)
        self.assertEqual(profile.user, user)
        
        self.assertEqual(brazilian_card.issuer_country, 'Brazil')
        self.assertEqual(portuguese_card.issuer_country, 'Portugal')
        
        self.assertEqual(len(exchange_rates), 3)
        
        self.assertEqual(university_payment.country, 'Brazil')
        self.assertEqual(rent_payment.country, 'Portugal')
        
        self.assertEqual(len(food_expenses), 5)
        self.assertEqual(len(transport_expenses), 3)
        
        self.assertFalse(open_invoice.is_closed)
        self.assertTrue(closed_invoice.is_closed)
        
        self.assertEqual(fixed_status.payment_type, 'fixed')
        self.assertEqual(variable_status.payment_type, 'variable')
        self.assertEqual(invoice_status.payment_type, 'credit_card')
    
    def test_factory_relationships(self):
        """Test that factory relationships work correctly."""
        # Create a credit card
        card = CreditCardFactory()
        
        # Create variable payments linked to the card
        payments = VariablePaymentFactory.create_batch(3, credit_card=card)
        
        # Create an invoice for the card
        invoice = CreditCardInvoiceFactory(credit_card=card)
        
        # Create payment status for the invoice
        status_obj = CreditCardInvoicePaymentStatusFactory(credit_card_invoice=invoice)
        
        # Verify relationships
        for payment in payments:
            self.assertEqual(payment.credit_card, card)
        
        self.assertEqual(invoice.credit_card, card)
        self.assertEqual(status_obj.credit_card_invoice, invoice)
        self.assertEqual(status_obj.payment_type, 'credit_card')
    
    def test_factory_data_consistency(self):
        """Test that factory data is consistent and realistic."""
        # Test Brazilian card has appropriate IOF
        brazilian_card = BrazilianCreditCardFactory()
        self.assertGreaterEqual(brazilian_card.iof_percent, 6.0)
        self.assertLessEqual(brazilian_card.iof_percent, 6.38)
        
        # Test Portuguese card has no IOF
        portuguese_card = PortugueseCreditCardFactory()
        self.assertEqual(portuguese_card.iof_percent, Decimal('0.00'))
        
        # Test university payment is Brazilian
        university_payment = UniversityPaymentFactory()
        self.assertEqual(university_payment.country, 'Brazil')
        self.assertEqual(university_payment.currency, 'BRL')
        
        # Test rent payment is Portuguese
        rent_payment = RentPaymentFactory()
        self.assertEqual(rent_payment.country, 'Portugal')
        self.assertEqual(rent_payment.currency, 'EUR')
        
        # Test food expenses are in food category
        food_expense = FoodExpenseFactory()
        self.assertEqual(food_expense.category, 'food')
        
        # Test transport expenses are in transport category
        transport_expense = TransportExpenseFactory()
        self.assertEqual(transport_expense.category, 'transport') 