from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
import json

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


class BaseViewTest(APITestCase):
    """Base test class for view tests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)


class UserFinancialProfileViewSetTest(BaseViewTest):
    """Test cases for UserFinancialProfileViewSet."""
    
    def test_list_user_financial_profiles(self):
        """Test listing user financial profiles."""
        profiles = UserFinancialProfileFactory.create_batch(3)
        
        url = reverse('userfinancialprofile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_user_financial_profile(self):
        """Test creating a user financial profile."""
        data = {
            'name': 'John Doe',
            'base_currency': 'EUR',
            'monthly_income_brl': '5000.00',
            'monthly_income_eur': '2000.00'
        }
        
        url = reverse('userfinancialprofile-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['base_currency'], 'EUR')
    
    def test_retrieve_user_financial_profile(self):
        """Test retrieving a specific user financial profile."""
        profile = UserFinancialProfileFactory()
        
        url = reverse('userfinancialprofile-detail', args=[profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], profile.id)
        self.assertEqual(response.data['name'], profile.name)
    
    def test_update_user_financial_profile(self):
        """Test updating a user financial profile."""
        profile = UserFinancialProfileFactory()
        data = {
            'name': 'Updated Name',
            'base_currency': 'BRL',
            'monthly_income_brl': '6000.00',
            'monthly_income_eur': '2500.00'
        }
        
        url = reverse('userfinancialprofile-detail', args=[profile.id])
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['base_currency'], 'BRL')
    
    def test_delete_user_financial_profile(self):
        """Test deleting a user financial profile."""
        profile = UserFinancialProfileFactory()
        
        url = reverse('userfinancialprofile-detail', args=[profile.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserFinancialProfile.objects.filter(id=profile.id).exists())
    
    def test_current_action(self):
        """Test current action to get current user's profile."""
        profile = UserFinancialProfileFactory(user=self.user)
        
        url = reverse('userfinancialprofile-current')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], profile.id)
    
    def test_current_action_no_profile(self):
        """Test current action when no profile exists."""
        url = reverse('userfinancialprofile-current')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class CreditCardViewSetTest(BaseViewTest):
    """Test cases for CreditCardViewSet."""
    
    def test_list_credit_cards(self):
        """Test listing credit cards."""
        cards = CreditCardFactory.create_batch(3)
        
        url = reverse('creditcard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_credit_card(self):
        """Test creating a credit card."""
        data = {
            'issuer_country': 'Brazil',
            'currency': 'BRL',
            'fx_fee_percent': '2.5',
            'iof_percent': '6.38',
            'cardholder_name': 'John Doe',
            'final_digits': '1234',
            'is_active': True
        }
        
        url = reverse('creditcard-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cardholder_name'], 'John Doe')
        self.assertEqual(response.data['issuer_country'], 'Brazil')
    
    def test_retrieve_credit_card(self):
        """Test retrieving a specific credit card."""
        card = CreditCardFactory()
        
        url = reverse('creditcard-detail', args=[card.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], card.id)
        self.assertEqual(response.data['cardholder_name'], card.cardholder_name)
    
    def test_update_credit_card(self):
        """Test updating a credit card."""
        card = CreditCardFactory()
        data = {
            'issuer_country': 'Portugal',
            'currency': 'EUR',
            'fx_fee_percent': '1.5',
            'iof_percent': '0.00',
            'cardholder_name': 'Updated Name',
            'final_digits': '5678',
            'is_active': False
        }
        
        url = reverse('creditcard-detail', args=[card.id])
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cardholder_name'], 'Updated Name')
        self.assertEqual(response.data['issuer_country'], 'Portugal')
    
    def test_delete_credit_card(self):
        """Test deleting a credit card."""
        card = CreditCardFactory()
        
        url = reverse('creditcard-detail', args=[card.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CreditCard.objects.filter(id=card.id).exists())
    
    def test_payments_action(self):
        """Test payments action to get payments for a credit card."""
        card = CreditCardFactory()
        payments = VariablePaymentFactory.create_batch(3, credit_card=card)
        
        url = reverse('creditcard-payments', args=[card.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_active_action(self):
        """Test active action to get only active credit cards."""
        active_cards = CreditCardFactory.create_batch(2, is_active=True)
        CreditCardFactory.create_batch(2, is_active=False)
        
        url = reverse('creditcard-active')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for card_data in response.data:
            self.assertTrue(card_data['is_active'])


class ExchangeRateViewSetTest(BaseViewTest):
    """Test cases for ExchangeRateViewSet."""
    
    def test_list_exchange_rates(self):
        """Test listing exchange rates."""
        rates = ExchangeRateFactory.create_batch(3)
        
        url = reverse('exchangerate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_exchange_rate(self):
        """Test creating an exchange rate."""
        data = {
            'from_currency': 'BRL',
            'to_currency': 'EUR',
            'rate': '5.50',
            'date': '2024-01-15'
        }
        
        url = reverse('exchangerate-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['from_currency'], 'BRL')
        self.assertEqual(response.data['to_currency'], 'EUR')
        self.assertEqual(Decimal(response.data['rate']), Decimal('5.50'))
    
    def test_latest_action(self):
        """Test latest action to get latest exchange rates."""
        # Create rates with different dates
        old_rate = ExchangeRateFactory(date=date.today() - timedelta(days=10))
        new_rate = ExchangeRateFactory(date=date.today())
        
        url = reverse('exchangerate-latest')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return the most recent rate
        self.assertEqual(response.data['id'], new_rate.id)
    
    def test_currency_pair_action(self):
        """Test currency_pair action to get rates for specific currency pair."""
        rate = ExchangeRateFactory(
            from_currency='BRL',
            to_currency='EUR',
            rate=Decimal('5.50')
        )
        
        url = reverse('exchangerate-currency-pair')
        response = self.client.get(url, {
            'from_currency': 'BRL',
            'to_currency': 'EUR'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], rate.id)


class FixedPaymentViewSetTest(BaseViewTest):
    """Test cases for FixedPaymentViewSet."""
    
    def test_list_fixed_payments(self):
        """Test listing fixed payments."""
        payments = FixedPaymentFactory.create_batch(3)
        
        url = reverse('fixedpayment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_fixed_payment(self):
        """Test creating a fixed payment."""
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
        
        url = reverse('fixedpayment-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'University Fees')
        self.assertEqual(response.data['country'], 'Brazil')
    
    def test_active_action(self):
        """Test active action to get only active fixed payments."""
        active_payments = FixedPaymentFactory.create_batch(2, is_active=True)
        FixedPaymentFactory.create_batch(2, is_active=False)
        
        url = reverse('fixedpayment-active')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for payment_data in response.data:
            self.assertTrue(payment_data['is_active'])
    
    def test_by_country_action(self):
        """Test by_country action to get payments by country."""
        brazil_payments = FixedPaymentFactory.create_batch(2, country='Brazil')
        portugal_payments = FixedPaymentFactory.create_batch(3, country='Portugal')
        
        url = reverse('fixedpayment-by-country')
        response = self.client.get(url, {'country': 'Brazil'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for payment_data in response.data:
            self.assertEqual(payment_data['country'], 'Brazil')


class VariablePaymentViewSetTest(BaseViewTest):
    """Test cases for VariablePaymentViewSet."""
    
    def test_list_variable_payments(self):
        """Test listing variable payments."""
        payments = VariablePaymentFactory.create_batch(3)
        
        url = reverse('variablepayment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_variable_payment(self):
        """Test creating a variable payment."""
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
        
        url = reverse('variablepayment-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Groceries')
        self.assertEqual(response.data['category'], 'food')
    
    def test_recent_action(self):
        """Test recent action to get recent variable payments."""
        recent_payments = VariablePaymentFactory.create_batch(3, date=date.today())
        old_payments = VariablePaymentFactory.create_batch(2, date=date.today() - timedelta(days=30))
        
        url = reverse('variablepayment-recent')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return recent payments (within last 7 days by default)
        self.assertGreater(len(response.data), 0)
    
    def test_by_category_action(self):
        """Test by_category action to get payments by category."""
        food_payments = FoodExpenseFactory.create_batch(3)
        transport_payments = TransportExpenseFactory.create_batch(2)
        
        url = reverse('variablepayment-by-category')
        response = self.client.get(url, {'category': 'food'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for payment_data in response.data:
            self.assertEqual(payment_data['category'], 'food')
    
    def test_by_country_action(self):
        """Test by_country action to get payments by country."""
        brazil_payments = VariablePaymentFactory.create_batch(2, country='Brazil')
        portugal_payments = VariablePaymentFactory.create_batch(3, country='Portugal')
        
        url = reverse('variablepayment-by-country')
        response = self.client.get(url, {'country': 'Brazil'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for payment_data in response.data:
            self.assertEqual(payment_data['country'], 'Brazil')
    
    def test_statistics_action(self):
        """Test statistics action to get payment statistics."""
        # Create payments with different categories and amounts
        FoodExpenseFactory.create_batch(3, amount=Decimal('50.00'))
        TransportExpenseFactory.create_batch(2, amount=Decimal('25.00'))
        
        url = reverse('variablepayment-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_expenses', response.data)
        self.assertIn('expenses_by_category', response.data)
        self.assertIn('expenses_by_country', response.data)


class PaymentStatusViewSetTest(BaseViewTest):
    """Test cases for PaymentStatusViewSet."""
    
    def test_list_payment_statuses(self):
        """Test listing payment statuses."""
        statuses = PaymentStatusFactory.create_batch(3)
        
        url = reverse('paymentstatus-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_payment_status(self):
        """Test creating a payment status."""
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
        
        url = reverse('paymentstatus-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['payment_type'], 'fixed')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_pending_action(self):
        """Test pending action to get pending payment statuses."""
        pending_statuses = PaymentStatusFactory.create_batch(3, status='pending')
        PaymentStatusFactory.create_batch(2, status='paid')
        
        url = reverse('paymentstatus-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for status_data in response.data:
            self.assertEqual(status_data['status'], 'pending')
    
    def test_overdue_action(self):
        """Test overdue action to get overdue payment statuses."""
        overdue_statuses = PaymentStatusFactory.create_batch(2, 
            status='pending', 
            due_date=date.today() - timedelta(days=5)
        )
        PaymentStatusFactory.create_batch(2, status='paid')
        
        url = reverse('paymentstatus-overdue')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for status_data in response.data:
            self.assertEqual(status_data['status'], 'pending')
            self.assertTrue(status_data['is_overdue'])
    
    def test_paid_action(self):
        """Test paid action to get paid payment statuses."""
        paid_statuses = PaymentStatusFactory.create_batch(3, status='paid')
        PaymentStatusFactory.create_batch(2, status='pending')
        
        url = reverse('paymentstatus-paid')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for status_data in response.data:
            self.assertEqual(status_data['status'], 'paid')
    
    def test_by_month_action(self):
        """Test by_month action to get payment statuses by month."""
        month_year = date.today().replace(day=1)
        month_statuses = PaymentStatusFactory.create_batch(3, month_year=month_year)
        PaymentStatusFactory.create_batch(2, month_year=month_year - timedelta(days=30))
        
        url = reverse('paymentstatus-by-month')
        response = self.client.get(url, {
            'year': month_year.year,
            'month': month_year.month
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_summary_action(self):
        """Test summary action to get payment status summary."""
        PaymentStatusFactory.create_batch(3, status='pending')
        PaymentStatusFactory.create_batch(2, status='paid')
        PaymentStatusFactory.create_batch(1, status='overdue')
        
        url = reverse('paymentstatus-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_payments', response.data)
        self.assertIn('pending_count', response.data)
        self.assertIn('paid_count', response.data)
        self.assertIn('overdue_count', response.data)


class CreditCardInvoiceViewSetTest(BaseViewTest):
    """Test cases for CreditCardInvoiceViewSet."""
    
    def test_list_credit_card_invoices(self):
        """Test listing credit card invoices."""
        invoices = CreditCardInvoiceFactory.create_batch(3)
        
        url = reverse('creditcardinvoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_credit_card_invoice(self):
        """Test creating a credit card invoice."""
        credit_card = CreditCardFactory()
        data = {
            'credit_card_id': credit_card.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'is_closed': False
        }
        
        url = reverse('creditcardinvoice-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['credit_card']['id'], credit_card.id)
        self.assertFalse(response.data['is_closed'])
    
    def test_close_invoice_action(self):
        """Test close_invoice action."""
        invoice = OpenCreditCardInvoiceFactory()
        
        url = reverse('creditcardinvoice-close-invoice', args=[invoice.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_closed'])
    
    def test_open_action(self):
        """Test open action to get open invoices."""
        open_invoices = OpenCreditCardInvoiceFactory.create_batch(2)
        ClosedCreditCardInvoiceFactory.create_batch(3)
        
        url = reverse('creditcardinvoice-open')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for invoice_data in response.data:
            self.assertFalse(invoice_data['is_closed'])
    
    def test_closed_action(self):
        """Test closed action to get closed invoices."""
        ClosedCreditCardInvoiceFactory.create_batch(3)
        OpenCreditCardInvoiceFactory.create_batch(2)
        
        url = reverse('creditcardinvoice-closed')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for invoice_data in response.data:
            self.assertTrue(invoice_data['is_closed'])
    
    def test_by_credit_card_action(self):
        """Test by_credit_card action to get invoices by credit card."""
        credit_card = CreditCardFactory()
        card_invoices = CreditCardInvoiceFactory.create_batch(3, credit_card=credit_card)
        CreditCardInvoiceFactory.create_batch(2)  # Other invoices
        
        url = reverse('creditcardinvoice-by-credit-card')
        response = self.client.get(url, {'credit_card_id': credit_card.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for invoice_data in response.data:
            self.assertEqual(invoice_data['credit_card']['id'], credit_card.id)
    
    def test_summary_action(self):
        """Test summary action to get invoice summary."""
        CreditCardInvoiceFactory.create_batch(3, is_closed=False)
        CreditCardInvoiceFactory.create_batch(2, is_closed=True)
        
        url = reverse('creditcardinvoice-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_invoices', response.data)
        self.assertIn('open_invoices', response.data)
        self.assertIn('closed_invoices', response.data)


class DashboardViewSetTest(BaseViewTest):
    """Test cases for DashboardViewSet."""
    
    def test_summary_action(self):
        """Test summary action to get dashboard summary."""
        # Create test data
        profile = UserFinancialProfileFactory(user=self.user)
        VariablePaymentFactory.create_batch(3)
        FixedPaymentFactory.create_batch(2, is_active=True)
        CreditCardFactory.create_batch(2, is_active=True)
        ExchangeRateFactory.create_batch(2)
        
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)
        self.assertIn('summary', response.data)
        self.assertIn('recent_expenses', response.data)
        self.assertIn('active_fixed_payments', response.data)
        self.assertIn('credit_cards', response.data)
        self.assertIn('exchange_rates', response.data)
    
    def test_monthly_report_action(self):
        """Test monthly_report action to get monthly financial report."""
        # Create test data for current month
        VariablePaymentFactory.create_batch(5, date=date.today())
        FixedPaymentFactory.create_batch(3, is_active=True)
        
        url = reverse('dashboard-monthly-report')
        response = self.client.get(url, {
            'year': date.today().year,
            'month': date.today().month
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('month', response.data)
        self.assertIn('year', response.data)
        self.assertIn('income', response.data)
        self.assertIn('expenses', response.data)
        self.assertIn('balance', response.data)
        self.assertIn('transactions_count', response.data)


class APIRootViewSetTest(BaseViewTest):
    """Test cases for APIRootViewSet."""
    
    def test_root_action(self):
        """Test root action to get API endpoints."""
        url = reverse('apiroot-root')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', response.data)
        self.assertIn('version', response.data)
        self.assertIn('description', response.data)


class AuthenticationTest(APITestCase):
    """Test cases for authentication."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('userfinancialprofile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access(self):
        """Test that authenticated users can access protected endpoints."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('userfinancialprofile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_root_public_access(self):
        """Test that API root is publicly accessible."""
        url = reverse('apiroot-root')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 