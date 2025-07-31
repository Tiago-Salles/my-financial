from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment,
    PaymentStatus,
    CreditCardInvoice
)
from ..serializers import (
    UserFinancialProfileSerializer,
    CreditCardSerializer,
    CreditCardDetailSerializer,
    ExchangeRateSerializer,
    FixedPaymentSerializer,
    VariablePaymentSerializer,
    VariablePaymentDetailSerializer,
    PaymentStatusSerializer,
    PaymentStatusDetailSerializer,
    CreditCardInvoiceSerializer,
    CreditCardInvoiceDetailSerializer,
    FinancialSummarySerializer,
    DashboardSerializer,
    ExpenseStatisticsSerializer,
    MonthlyReportSerializer,
    VariablePaymentFilterSerializer,
    FixedPaymentFilterSerializer,
    APIResponseSerializer
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


class UserFinancialProfileSerializerTest(TestCase):
    """Test cases for UserFinancialProfileSerializer."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_serialize_user_financial_profile(self):
        """Test serializing a user financial profile."""
        profile = UserFinancialProfileFactory(user=self.user)
        serializer = UserFinancialProfileSerializer(profile)
        data = serializer.data
        
        self.assertEqual(data['id'], profile.id)
        self.assertEqual(data['name'], profile.name)
        self.assertEqual(data['base_currency'], profile.base_currency)
        self.assertEqual(Decimal(data['monthly_income_brl']), profile.monthly_income_brl)
        self.assertEqual(Decimal(data['monthly_income_eur']), profile.monthly_income_eur)
        self.assertEqual(Decimal(data['total_monthly_income_base_currency']), profile.total_monthly_income_base_currency)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_user_financial_profile(self):
        """Test deserializing user financial profile data."""
        data = {
            'name': 'John Doe',
            'base_currency': 'EUR',
            'monthly_income_brl': '5000.00',
            'monthly_income_eur': '2000.00'
        }
        serializer = UserFinancialProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        profile = serializer.save(user=self.user)
        self.assertEqual(profile.name, 'John Doe')
        self.assertEqual(profile.base_currency, 'EUR')
        self.assertEqual(profile.monthly_income_brl, Decimal('5000.00'))
        self.assertEqual(profile.monthly_income_eur, Decimal('2000.00'))
    
    def test_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid base currency
        data = {
            'name': 'John Doe',
            'base_currency': 'INVALID',
            'monthly_income_brl': '5000.00',
            'monthly_income_eur': '2000.00'
        }
        serializer = UserFinancialProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('base_currency', serializer.errors)


class CreditCardSerializerTest(TestCase):
    """Test cases for CreditCardSerializer."""
    
    def test_serialize_credit_card(self):
        """Test serializing a credit card."""
        card = CreditCardFactory()
        serializer = CreditCardSerializer(card)
        data = serializer.data
        
        self.assertEqual(data['id'], card.id)
        self.assertEqual(data['issuer_country'], card.issuer_country)
        self.assertEqual(data['currency'], card.currency)
        self.assertEqual(Decimal(data['fx_fee_percent']), card.fx_fee_percent)
        self.assertEqual(Decimal(data['iof_percent']), card.iof_percent)
        self.assertEqual(data['cardholder_name'], card.cardholder_name)
        self.assertEqual(data['final_digits'], card.final_digits)
        self.assertEqual(data['is_active'], card.is_active)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_credit_card(self):
        """Test deserializing credit card data."""
        data = {
            'issuer_country': 'Brazil',
            'currency': 'BRL',
            'fx_fee_percent': '2.5',
            'iof_percent': '6.38',
            'cardholder_name': 'John Doe',
            'final_digits': '1234',
            'is_active': True
        }
        serializer = CreditCardSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        card = serializer.save()
        self.assertEqual(card.issuer_country, 'Brazil')
        self.assertEqual(card.currency, 'BRL')
        self.assertEqual(card.fx_fee_percent, Decimal('2.5'))
        self.assertEqual(card.iof_percent, Decimal('6.38'))
        self.assertEqual(card.cardholder_name, 'John Doe')
        self.assertEqual(card.final_digits, '1234')
        self.assertTrue(card.is_active)
    
    def test_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid issuer country
        data = {
            'issuer_country': 'Invalid',
            'currency': 'BRL',
            'fx_fee_percent': '2.5',
            'iof_percent': '6.38',
            'cardholder_name': 'John Doe',
            'final_digits': '1234',
            'is_active': True
        }
        serializer = CreditCardSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('issuer_country', serializer.errors)


class CreditCardDetailSerializerTest(TestCase):
    """Test cases for CreditCardDetailSerializer."""
    
    def test_serialize_credit_card_with_payments(self):
        """Test serializing a credit card with related payments."""
        card = CreditCardFactory()
        # Create some variable payments for this card
        VariablePaymentFactory.create_batch(3, credit_card=card)
        
        serializer = CreditCardDetailSerializer(card)
        data = serializer.data
        
        self.assertEqual(data['id'], card.id)
        self.assertEqual(data['cardholder_name'], card.cardholder_name)
        self.assertIn('variable_payments', data)
        self.assertEqual(len(data['variable_payments']), 3)
    
    def test_get_variable_payments_method(self):
        """Test get_variable_payments method."""
        card = CreditCardFactory()
        payments = VariablePaymentFactory.create_batch(2, credit_card=card)
        
        serializer = CreditCardDetailSerializer()
        result = serializer.get_variable_payments(card)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], payments[0].id)
        self.assertEqual(result[1]['id'], payments[1].id)


class ExchangeRateSerializerTest(TestCase):
    """Test cases for ExchangeRateSerializer."""
    
    def test_serialize_exchange_rate(self):
        """Test serializing an exchange rate."""
        rate = ExchangeRateFactory()
        serializer = ExchangeRateSerializer(rate)
        data = serializer.data
        
        self.assertEqual(data['id'], rate.id)
        self.assertEqual(data['from_currency'], rate.from_currency)
        self.assertEqual(data['to_currency'], rate.to_currency)
        self.assertEqual(Decimal(data['rate']), rate.rate)
        self.assertEqual(data['date'], rate.date.isoformat())
        self.assertIn('created_at', data)
    
    def test_deserialize_exchange_rate(self):
        """Test deserializing exchange rate data."""
        data = {
            'from_currency': 'BRL',
            'to_currency': 'EUR',
            'rate': '5.50',
            'date': '2024-01-15'
        }
        serializer = ExchangeRateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        rate = serializer.save()
        self.assertEqual(rate.from_currency, 'BRL')
        self.assertEqual(rate.to_currency, 'EUR')
        self.assertEqual(rate.rate, Decimal('5.50'))
        self.assertEqual(rate.date, date(2024, 1, 15))


class FixedPaymentSerializerTest(TestCase):
    """Test cases for FixedPaymentSerializer."""
    
    def test_serialize_fixed_payment(self):
        """Test serializing a fixed payment."""
        payment = FixedPaymentFactory()
        serializer = FixedPaymentSerializer(payment)
        data = serializer.data
        
        self.assertEqual(data['id'], payment.id)
        self.assertEqual(data['country'], payment.country)
        self.assertEqual(data['description'], payment.description)
        self.assertEqual(Decimal(data['amount']), payment.amount)
        self.assertEqual(data['currency'], payment.currency)
        self.assertEqual(data['frequency'], payment.frequency)
        self.assertEqual(data['start_date'], payment.start_date.isoformat())
        if payment.end_date:
            self.assertEqual(data['end_date'], payment.end_date.isoformat())
        self.assertEqual(data['is_active'], payment.is_active)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_fixed_payment(self):
        """Test deserializing fixed payment data."""
        data = {
            'country': 'Brazil',
            'description': 'University Fees',
            'amount': '1500.00',
            'currency': 'BRL',
            'frequency': 'monthly',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'is_active': True
        }
        serializer = FixedPaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        payment = serializer.save()
        self.assertEqual(payment.country, 'Brazil')
        self.assertEqual(payment.description, 'University Fees')
        self.assertEqual(payment.amount, Decimal('1500.00'))
        self.assertEqual(payment.currency, 'BRL')
        self.assertEqual(payment.frequency, 'monthly')
        self.assertEqual(payment.start_date, date(2024, 1, 1))
        self.assertEqual(payment.end_date, date(2024, 12, 31))
        self.assertTrue(payment.is_active)


class VariablePaymentSerializerTest(TestCase):
    """Test cases for VariablePaymentSerializer."""
    
    def test_serialize_variable_payment(self):
        """Test serializing a variable payment."""
        payment = VariablePaymentFactory()
        serializer = VariablePaymentSerializer(payment)
        data = serializer.data
        
        self.assertEqual(data['id'], payment.id)
        self.assertEqual(data['date'], payment.date.isoformat())
        self.assertEqual(data['country'], payment.country)
        self.assertEqual(data['description'], payment.description)
        self.assertEqual(Decimal(data['amount']), payment.amount)
        self.assertEqual(data['currency'], payment.currency)
        self.assertEqual(data['category'], payment.category)
        self.assertEqual(data['linked_credit_card'], payment.linked_credit_card)
        self.assertIn('credit_card', data)
        self.assertEqual(Decimal(data['total_amount_with_fees']), payment.total_amount_with_fees)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_variable_payment(self):
        """Test deserializing variable payment data."""
        credit_card = CreditCardFactory()
        data = {
            'date': '2024-01-15',
            'country': 'Brazil',
            'description': 'Groceries',
            'amount': '150.00',
            'currency': 'BRL',
            'category': 'food',
            'linked_credit_card': True,
            'credit_card_id': credit_card.id
        }
        serializer = VariablePaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        payment = serializer.save()
        self.assertEqual(payment.date, date(2024, 1, 15))
        self.assertEqual(payment.country, 'Brazil')
        self.assertEqual(payment.description, 'Groceries')
        self.assertEqual(payment.amount, Decimal('150.00'))
        self.assertEqual(payment.currency, 'BRL')
        self.assertEqual(payment.category, 'food')
        self.assertTrue(payment.linked_credit_card)
        self.assertEqual(payment.credit_card, credit_card)


class PaymentStatusSerializerTest(TestCase):
    """Test cases for PaymentStatusSerializer."""
    
    def test_serialize_payment_status(self):
        """Test serializing a payment status."""
        status_obj = PaymentStatusFactory()
        serializer = PaymentStatusSerializer(status_obj)
        data = serializer.data
        
        self.assertEqual(data['id'], status_obj.id)
        self.assertEqual(data['payment_type'], status_obj.payment_type)
        self.assertEqual(data['month_year'], status_obj.month_year.isoformat())
        self.assertEqual(data['due_date'], status_obj.due_date.isoformat())
        self.assertEqual(data['status'], status_obj.status)
        self.assertEqual(data['is_paid'], status_obj.is_paid)
        self.assertEqual(Decimal(data['expected_amount']), status_obj.expected_amount)
        self.assertEqual(data['currency'], status_obj.currency)
        self.assertIn('payment_description', data)
        self.assertIn('payment_country', data)
        self.assertIn('is_overdue', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_payment_status(self):
        """Test deserializing payment status data."""
        fixed_payment = FixedPaymentFactory()
        data = {
            'fixed_payment': fixed_payment.id,
            'payment_type': 'fixed',
            'month_year': '2024-01-01',
            'due_date': '2024-01-15',
            'status': 'pending',
            'is_paid': False,
            'expected_amount': '500.00',
            'currency': 'BRL',
            'notes': 'Test payment'
        }
        serializer = PaymentStatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        status_obj = serializer.save()
        self.assertEqual(status_obj.fixed_payment, fixed_payment)
        self.assertEqual(status_obj.payment_type, 'fixed')
        self.assertEqual(status_obj.month_year, date(2024, 1, 1))
        self.assertEqual(status_obj.due_date, date(2024, 1, 15))
        self.assertEqual(status_obj.status, 'pending')
        self.assertFalse(status_obj.is_paid)
        self.assertEqual(status_obj.expected_amount, Decimal('500.00'))
        self.assertEqual(status_obj.currency, 'BRL')
        self.assertEqual(status_obj.notes, 'Test payment')


class CreditCardInvoiceSerializerTest(TestCase):
    """Test cases for CreditCardInvoiceSerializer."""
    
    def test_serialize_credit_card_invoice(self):
        """Test serializing a credit card invoice."""
        invoice = CreditCardInvoiceFactory()
        serializer = CreditCardInvoiceSerializer(invoice)
        data = serializer.data
        
        self.assertEqual(data['id'], invoice.id)
        self.assertIn('credit_card', data)
        self.assertEqual(data['start_date'], invoice.start_date.isoformat())
        self.assertEqual(data['end_date'], invoice.end_date.isoformat())
        self.assertEqual(data['is_closed'], invoice.is_closed)
        self.assertIn('total_amount', data)
        self.assertIn('purchases_count', data)
        self.assertIn('total_with_fees', data)
        self.assertIn('billing_period_days', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_credit_card_invoice(self):
        """Test deserializing credit card invoice data."""
        credit_card = CreditCardFactory()
        data = {
            'credit_card_id': credit_card.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'is_closed': False
        }
        serializer = CreditCardInvoiceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        invoice = serializer.save()
        self.assertEqual(invoice.credit_card, credit_card)
        self.assertEqual(invoice.start_date, date(2024, 1, 1))
        self.assertEqual(invoice.end_date, date(2024, 1, 31))
        self.assertFalse(invoice.is_closed)


class FinancialSummarySerializerTest(TestCase):
    """Test cases for FinancialSummarySerializer."""
    
    def test_serialize_financial_summary(self):
        """Test serializing financial summary data."""
        data = {
            'total_monthly_income': Decimal('5000.00'),
            'total_monthly_expenses': Decimal('3000.00'),
            'total_monthly_fees': Decimal('150.00'),
            'monthly_balance': Decimal('1850.00'),
            'expenses_by_country': [
                {'country': 'Brazil', 'amount': '2000.00'},
                {'country': 'Portugal', 'amount': '1000.00'}
            ],
            'expenses_by_category': [
                {'category': 'food', 'amount': '800.00'},
                {'category': 'transport', 'amount': '400.00'}
            ],
            'expenses_by_currency': [
                {'currency': 'BRL', 'amount': '2000.00'},
                {'currency': 'EUR', 'amount': '1000.00'}
            ]
        }
        serializer = FinancialSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.data
        self.assertEqual(Decimal(serialized_data['total_monthly_income']), Decimal('5000.00'))
        self.assertEqual(Decimal(serialized_data['total_monthly_expenses']), Decimal('3000.00'))
        self.assertEqual(Decimal(serialized_data['total_monthly_fees']), Decimal('150.00'))
        self.assertEqual(Decimal(serialized_data['monthly_balance']), Decimal('1850.00'))
        self.assertEqual(len(serialized_data['expenses_by_country']), 2)
        self.assertEqual(len(serialized_data['expenses_by_category']), 2)
        self.assertEqual(len(serialized_data['expenses_by_currency']), 2)


class DashboardSerializerTest(TestCase):
    """Test cases for DashboardSerializer."""
    
    def test_serialize_dashboard_data(self):
        """Test serializing dashboard data."""
        profile = UserFinancialProfileFactory()
        summary_data = {
            'total_monthly_income': Decimal('5000.00'),
            'total_monthly_expenses': Decimal('3000.00'),
            'total_monthly_fees': Decimal('150.00'),
            'monthly_balance': Decimal('1850.00'),
            'expenses_by_country': [],
            'expenses_by_category': [],
            'expenses_by_currency': []
        }
        recent_expenses = VariablePaymentFactory.create_batch(3)
        active_fixed_payments = FixedPaymentFactory.create_batch(2, is_active=True)
        credit_cards = CreditCardFactory.create_batch(2, is_active=True)
        exchange_rates = ExchangeRateFactory.create_batch(2)
        
        data = {
            'profile': profile,
            'summary': summary_data,
            'recent_expenses': recent_expenses,
            'active_fixed_payments': active_fixed_payments,
            'credit_cards': credit_cards,
            'exchange_rates': exchange_rates
        }
        
        serializer = DashboardSerializer(data)
        serialized_data = serializer.data
        
        self.assertIn('profile', serialized_data)
        self.assertIn('summary', serialized_data)
        self.assertIn('recent_expenses', serialized_data)
        self.assertIn('active_fixed_payments', serialized_data)
        self.assertIn('credit_cards', serialized_data)
        self.assertIn('exchange_rates', serialized_data)
        self.assertEqual(len(serialized_data['recent_expenses']), 3)
        self.assertEqual(len(serialized_data['active_fixed_payments']), 2)
        self.assertEqual(len(serialized_data['credit_cards']), 2)
        self.assertEqual(len(serialized_data['exchange_rates']), 2)


class FilterSerializerTest(TestCase):
    """Test cases for filter serializers."""
    
    def test_variable_payment_filter_serializer(self):
        """Test VariablePaymentFilterSerializer."""
        data = {
            'date_from': '2024-01-01',
            'date_to': '2024-01-31',
            'country': 'Brazil',
            'currency': 'BRL',
            'category': 'food',
            'min_amount': '10.00',
            'max_amount': '500.00',
            'linked_credit_card': True,
            'credit_card_id': 1
        }
        serializer = VariablePaymentFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.data
        self.assertEqual(serialized_data['date_from'], '2024-01-01')
        self.assertEqual(serialized_data['date_to'], '2024-01-31')
        self.assertEqual(serialized_data['country'], 'Brazil')
        self.assertEqual(serialized_data['currency'], 'BRL')
        self.assertEqual(serialized_data['category'], 'food')
        self.assertEqual(Decimal(serialized_data['min_amount']), Decimal('10.00'))
        self.assertEqual(Decimal(serialized_data['max_amount']), Decimal('500.00'))
        self.assertTrue(serialized_data['linked_credit_card'])
        self.assertEqual(serialized_data['credit_card_id'], 1)
    
    def test_fixed_payment_filter_serializer(self):
        """Test FixedPaymentFilterSerializer."""
        data = {
            'country': 'Portugal',
            'currency': 'EUR',
            'frequency': 'monthly',
            'is_active': True,
            'min_amount': '100.00',
            'max_amount': '2000.00'
        }
        serializer = FixedPaymentFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.data
        self.assertEqual(serialized_data['country'], 'Portugal')
        self.assertEqual(serialized_data['currency'], 'EUR')
        self.assertEqual(serialized_data['frequency'], 'monthly')
        self.assertTrue(serialized_data['is_active'])
        self.assertEqual(Decimal(serialized_data['min_amount']), Decimal('100.00'))
        self.assertEqual(Decimal(serialized_data['max_amount']), Decimal('2000.00'))


class APIResponseSerializerTest(TestCase):
    """Test cases for APIResponseSerializer."""
    
    def test_serialize_success_response(self):
        """Test serializing a success response."""
        data = {
            'success': True,
            'message': 'Operation completed successfully',
            'data': {'id': 1, 'name': 'Test'}
        }
        serializer = APIResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.data
        self.assertTrue(serialized_data['success'])
        self.assertEqual(serialized_data['message'], 'Operation completed successfully')
        self.assertEqual(serialized_data['data'], {'id': 1, 'name': 'Test'})
    
    def test_serialize_error_response(self):
        """Test serializing an error response."""
        data = {
            'success': False,
            'message': 'Validation failed',
            'errors': ['Field is required', 'Invalid format']
        }
        serializer = APIResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.data
        self.assertFalse(serialized_data['success'])
        self.assertEqual(serialized_data['message'], 'Validation failed')
        self.assertEqual(serialized_data['errors'], ['Field is required', 'Invalid format']) 