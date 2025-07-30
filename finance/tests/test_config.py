"""
Test configuration and utilities for the finance app test suite.
"""
import os
import sys
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

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
    CreditCardInvoiceFactory
)


class TestConfig:
    """Configuration class for test settings."""
    
    # Test data constants
    TEST_USER_USERNAME = 'testuser'
    TEST_USER_EMAIL = 'test@example.com'
    TEST_USER_PASSWORD = 'testpass123'
    
    # Test amounts
    TEST_AMOUNTS = {
        'small': Decimal('10.00'),
        'medium': Decimal('100.00'),
        'large': Decimal('1000.00'),
        'university_fee': Decimal('1500.00'),
        'rent': Decimal('800.00'),
        'food': Decimal('50.00'),
        'transport': Decimal('25.00')
    }
    
    # Test dates
    TEST_DATES = {
        'today': date.today(),
        'yesterday': date.today() - timedelta(days=1),
        'tomorrow': date.today() + timedelta(days=1),
        'last_month': date.today() - timedelta(days=30),
        'next_month': date.today() + timedelta(days=30)
    }
    
    # Test currencies
    TEST_CURRENCIES = ['BRL', 'EUR', 'USD']
    
    # Test countries
    TEST_COUNTRIES = ['Brazil', 'Portugal']
    
    # Test categories
    TEST_CATEGORIES = [
        'food', 'transport', 'entertainment', 'health', 
        'education', 'shopping', 'bills', 'other'
    ]
    
    # Test payment types
    TEST_PAYMENT_TYPES = ['fixed', 'variable', 'credit_card']
    
    # Test statuses
    TEST_STATUSES = ['pending', 'paid', 'overdue', 'cancelled']


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TestConfig.TEST_USER_USERNAME,
            email=TestConfig.TEST_USER_EMAIL,
            password=TestConfig.TEST_USER_PASSWORD
        )
        self.profile = UserFinancialProfileFactory(user=self.user)
    
    def create_test_credit_cards(self, count=2):
        """Create test credit cards."""
        return CreditCardFactory.create_batch(count)
    
    def create_test_exchange_rates(self, count=3):
        """Create test exchange rates."""
        return ExchangeRateFactory.create_batch(count)
    
    def create_test_fixed_payments(self, count=3):
        """Create test fixed payments."""
        return FixedPaymentFactory.create_batch(count)
    
    def create_test_variable_payments(self, count=5):
        """Create test variable payments."""
        return VariablePaymentFactory.create_batch(count)
    
    def create_test_invoices(self, count=2):
        """Create test credit card invoices."""
        return CreditCardInvoiceFactory.create_batch(count)
    
    def create_test_payment_statuses(self, count=4):
        """Create test payment statuses."""
        return PaymentStatusFactory.create_batch(count)
    
    def assert_decimal_equal(self, actual, expected, places=2):
        """Assert that two decimal values are equal within specified places."""
        actual_rounded = actual.quantize(Decimal(f'0.{"0" * places}'))
        expected_rounded = expected.quantize(Decimal(f'0.{"0" * places}'))
        self.assertEqual(actual_rounded, expected_rounded)
    
    def assert_date_equal(self, actual, expected):
        """Assert that two dates are equal."""
        if isinstance(actual, str):
            actual = date.fromisoformat(actual)
        if isinstance(expected, str):
            expected = date.fromisoformat(expected)
        self.assertEqual(actual, expected)
    
    def assert_currency_valid(self, currency):
        """Assert that a currency is valid."""
        self.assertIn(currency, TestConfig.TEST_CURRENCIES)
    
    def assert_country_valid(self, country):
        """Assert that a country is valid."""
        self.assertIn(country, TestConfig.TEST_COUNTRIES)
    
    def assert_category_valid(self, category):
        """Assert that a category is valid."""
        self.assertIn(category, TestConfig.TEST_CATEGORIES)
    
    def assert_payment_type_valid(self, payment_type):
        """Assert that a payment type is valid."""
        self.assertIn(payment_type, TestConfig.TEST_PAYMENT_TYPES)
    
    def assert_status_valid(self, status):
        """Assert that a status is valid."""
        self.assertIn(status, TestConfig.TEST_STATUSES)


class TestDataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def create_complete_financial_scenario():
        """Create a complete financial scenario with all models."""
        # Create user and profile
        user = User.objects.create_user(
            username='scenario_user',
            email='scenario@example.com',
            password='scenario123'
        )
        profile = UserFinancialProfileFactory(user=user)
        
        # Create credit cards
        brazilian_card = CreditCardFactory(issuer_country='Brazil', currency='BRL')
        portuguese_card = CreditCardFactory(issuer_country='Portugal', currency='EUR')
        
        # Create exchange rates
        exchange_rates = ExchangeRateFactory.create_batch(3)
        
        # Create fixed payments
        fixed_payments = FixedPaymentFactory.create_batch(3)
        
        # Create variable payments
        variable_payments = VariablePaymentFactory.create_batch(5)
        
        # Create invoices
        invoices = CreditCardInvoiceFactory.create_batch(2)
        
        # Create payment statuses
        payment_statuses = PaymentStatusFactory.create_batch(4)
        
        return {
            'user': user,
            'profile': profile,
            'credit_cards': [brazilian_card, portuguese_card],
            'exchange_rates': exchange_rates,
            'fixed_payments': fixed_payments,
            'variable_payments': variable_payments,
            'invoices': invoices,
            'payment_statuses': payment_statuses
        }
    
    @staticmethod
    def create_brazilian_financial_data():
        """Create Brazilian financial data."""
        user = User.objects.create_user(
            username='brazilian_user',
            email='brazilian@example.com',
            password='brazilian123'
        )
        profile = UserFinancialProfileFactory(
            user=user,
            base_currency='BRL',
            monthly_income_brl=Decimal('5000.00'),
            monthly_income_eur=Decimal('1000.00')
        )
        
        # Brazilian credit card
        card = CreditCardFactory(
            issuer_country='Brazil',
            currency='BRL',
            iof_percent=Decimal('6.38')
        )
        
        # Brazilian payments
        fixed_payments = FixedPaymentFactory.create_batch(2, country='Brazil', currency='BRL')
        variable_payments = VariablePaymentFactory.create_batch(3, country='Brazil', currency='BRL')
        
        return {
            'user': user,
            'profile': profile,
            'credit_card': card,
            'fixed_payments': fixed_payments,
            'variable_payments': variable_payments
        }
    
    @staticmethod
    def create_portuguese_financial_data():
        """Create Portuguese financial data."""
        user = User.objects.create_user(
            username='portuguese_user',
            email='portuguese@example.com',
            password='portuguese123'
        )
        profile = UserFinancialProfileFactory(
            user=user,
            base_currency='EUR',
            monthly_income_brl=Decimal('2000.00'),
            monthly_income_eur=Decimal('3000.00')
        )
        
        # Portuguese credit card
        card = CreditCardFactory(
            issuer_country='Portugal',
            currency='EUR',
            iof_percent=Decimal('0.00')
        )
        
        # Portuguese payments
        fixed_payments = FixedPaymentFactory.create_batch(2, country='Portugal', currency='EUR')
        variable_payments = VariablePaymentFactory.create_batch(3, country='Portugal', currency='EUR')
        
        return {
            'user': user,
            'profile': profile,
            'credit_card': card,
            'fixed_payments': fixed_payments,
            'variable_payments': variable_payments
        }


class TestAssertions:
    """Custom assertions for financial data validation."""
    
    @staticmethod
    def assert_financial_profile_valid(test_case, profile):
        """Assert that a financial profile is valid."""
        test_case.assertIsNotNone(profile.id)
        test_case.assertIsNotNone(profile.name)
        test_case.assertIn(profile.base_currency, TestConfig.TEST_CURRENCIES)
        test_case.assertGreaterEqual(profile.monthly_income_brl, 0)
        test_case.assertGreaterEqual(profile.monthly_income_eur, 0)
    
    @staticmethod
    def assert_credit_card_valid(test_case, card):
        """Assert that a credit card is valid."""
        test_case.assertIsNotNone(card.id)
        test_case.assertIn(card.issuer_country, TestConfig.TEST_COUNTRIES)
        test_case.assertIn(card.currency, TestConfig.TEST_CURRENCIES)
        test_case.assertGreaterEqual(card.fx_fee_percent, 0)
        test_case.assertGreaterEqual(card.iof_percent, 0)
        test_case.assertIsNotNone(card.cardholder_name)
        test_case.assertIsNotNone(card.final_digits)
        test_case.assertIsInstance(card.is_active, bool)
    
    @staticmethod
    def assert_exchange_rate_valid(test_case, rate):
        """Assert that an exchange rate is valid."""
        test_case.assertIsNotNone(rate.id)
        test_case.assertIn(rate.from_currency, TestConfig.TEST_CURRENCIES)
        test_case.assertIn(rate.to_currency, TestConfig.TEST_CURRENCIES)
        test_case.assertGreater(rate.rate, 0)
        test_case.assertIsInstance(rate.date, date)
    
    @staticmethod
    def assert_fixed_payment_valid(test_case, payment):
        """Assert that a fixed payment is valid."""
        test_case.assertIsNotNone(payment.id)
        test_case.assertIn(payment.country, TestConfig.TEST_COUNTRIES)
        test_case.assertIsNotNone(payment.description)
        test_case.assertGreater(payment.amount, 0)
        test_case.assertIn(payment.currency, TestConfig.TEST_CURRENCIES)
        test_case.assertIn(payment.frequency, ['monthly', 'yearly'])
        test_case.assertIsInstance(payment.is_active, bool)
    
    @staticmethod
    def assert_variable_payment_valid(test_case, payment):
        """Assert that a variable payment is valid."""
        test_case.assertIsNotNone(payment.id)
        test_case.assertIsInstance(payment.date, date)
        test_case.assertIn(payment.country, TestConfig.TEST_COUNTRIES)
        test_case.assertIsNotNone(payment.description)
        test_case.assertGreater(payment.amount, 0)
        test_case.assertIn(payment.currency, TestConfig.TEST_CURRENCIES)
        test_case.assertIn(payment.category, TestConfig.TEST_CATEGORIES)
        test_case.assertIsInstance(payment.linked_credit_card, bool)
    
    @staticmethod
    def assert_payment_status_valid(test_case, status_obj):
        """Assert that a payment status is valid."""
        test_case.assertIsNotNone(status_obj.id)
        test_case.assertIn(status_obj.payment_type, TestConfig.TEST_PAYMENT_TYPES)
        test_case.assertIsInstance(status_obj.month_year, date)
        test_case.assertIsInstance(status_obj.due_date, date)
        test_case.assertIn(status_obj.status, TestConfig.TEST_STATUSES)
        test_case.assertIsInstance(status_obj.is_paid, bool)
        test_case.assertGreater(status_obj.expected_amount, 0)
        test_case.assertIn(status_obj.currency, TestConfig.TEST_CURRENCIES)
    
    @staticmethod
    def assert_credit_card_invoice_valid(test_case, invoice):
        """Assert that a credit card invoice is valid."""
        test_case.assertIsNotNone(invoice.id)
        test_case.assertIsInstance(invoice.credit_card, CreditCard)
        test_case.assertIsInstance(invoice.start_date, date)
        test_case.assertIsInstance(invoice.end_date, date)
        test_case.assertIsInstance(invoice.is_closed, bool) 