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


class FinancialSystemIntegrationTest(APITestCase):
    """Integration tests for the complete financial system."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create base data for integration tests
        self.profile = UserFinancialProfileFactory(user=self.user)
        self.brazilian_card = BrazilianCreditCardFactory()
        self.portuguese_card = PortugueseCreditCardFactory()
        self.exchange_rates = RealisticExchangeRateFactory.create_batch(3)
    
    def test_complete_financial_workflow(self):
        """Test a complete financial workflow from creation to reporting."""
        # 1. Create fixed payments
        university_payment = UniversityPaymentFactory()
        rent_payment = RentPaymentFactory()
        
        # 2. Create variable payments
        food_expenses = FoodExpenseFactory.create_batch(5)
        transport_expenses = TransportExpenseFactory.create_batch(3)
        
        # 3. Create credit card invoices
        open_invoice = OpenCreditCardInvoiceFactory(credit_card=self.brazilian_card)
        closed_invoice = ClosedCreditCardInvoiceFactory(credit_card=self.portuguese_card)
        
        # 4. Create payment statuses
        fixed_status = FixedPaymentStatusFactory(fixed_payment=university_payment)
        variable_status = VariablePaymentStatusFactory(variable_payment=food_expenses[0])
        invoice_status = CreditCardInvoicePaymentStatusFactory(credit_card_invoice=open_invoice)
        
        # 5. Test API endpoints
        # Test dashboard summary
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)
        self.assertIn('summary', response.data)
        
        # Test monthly report
        url = reverse('dashboard-monthly-report')
        response = self.client.get(url, {
            'year': date.today().year,
            'month': date.today().month
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('month', response.data)
        self.assertIn('expenses', response.data)
        
        # Test payment status summary
        url = reverse('paymentstatus-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_payments', response.data)
        
        # Test credit card invoice summary
        url = reverse('creditcardinvoice-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_invoices', response.data)
    
    def test_cross_currency_financial_management(self):
        """Test managing finances across multiple currencies."""
        # Create exchange rates for currency conversion
        brl_to_eur = ExchangeRateFactory(
            from_currency='BRL',
            to_currency='EUR',
            rate=Decimal('5.50')
        )
        eur_to_brl = ExchangeRateFactory(
            from_currency='EUR',
            to_currency='BRL',
            rate=Decimal('0.18')
        )
        
        # Create payments in different currencies
        brazilian_expenses = VariablePaymentFactory.create_batch(3, currency='BRL', country='Brazil')
        portuguese_expenses = VariablePaymentFactory.create_batch(2, currency='EUR', country='Portugal')
        
        # Test filtering by currency
        url = reverse('variablepayment-list')
        response = self.client.get(url, {'currency': 'BRL'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        response = self.client.get(url, {'currency': 'EUR'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_credit_card_integration(self):
        """Test credit card integration with payments and invoices."""
        # Create variable payments linked to credit cards
        card_payments = VariablePaymentFactory.create_batch(5, 
            credit_card=self.brazilian_card,
            linked_credit_card=True
        )
        
        # Create invoice for the card
        invoice = CreditCardInvoiceFactory(credit_card=self.brazilian_card)
        
        # Test credit card payments endpoint
        url = reverse('creditcard-payments', args=[self.brazilian_card.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        
        # Test invoice creation and closing
        url = reverse('creditcardinvoice-close-invoice', args=[invoice.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_closed'])
    
    def test_payment_tracking_system(self):
        """Test the complete payment tracking system."""
        # Create various payment types
        fixed_payment = FixedPaymentFactory()
        variable_payment = VariablePaymentFactory()
        invoice = CreditCardInvoiceFactory()
        
        # Create payment statuses
        fixed_status = FixedPaymentStatusFactory(
            fixed_payment=fixed_payment,
            status='pending',
            due_date=date.today() + timedelta(days=5)
        )
        variable_status = VariablePaymentStatusFactory(
            variable_payment=variable_payment,
            status='paid',
            paid_date=date.today()
        )
        invoice_status = CreditCardInvoicePaymentStatusFactory(
            credit_card_invoice=invoice,
            status='overdue',
            due_date=date.today() - timedelta(days=5)
        )
        
        # Test payment status filtering
        url = reverse('paymentstatus-pending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        url = reverse('paymentstatus-paid')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        url = reverse('paymentstatus-overdue')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_financial_reporting_integration(self):
        """Test comprehensive financial reporting."""
        # Create diverse financial data
        profiles = UserFinancialProfileFactory.create_batch(2)
        cards = CreditCardFactory.create_batch(3)
        fixed_payments = FixedPaymentFactory.create_batch(5)
        variable_payments = VariablePaymentFactory.create_batch(10)
        invoices = CreditCardInvoiceFactory.create_batch(4)
        
        # Test statistics endpoints
        url = reverse('variablepayment-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_expenses', response.data)
        self.assertIn('expenses_by_category', response.data)
        
        # Test by-category filtering
        url = reverse('variablepayment-by-category')
        response = self.client.get(url, {'category': 'food'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test by-country filtering
        url = reverse('variablepayment-by-country')
        response = self.client.get(url, {'country': 'Brazil'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_data_consistency_across_models(self):
        """Test data consistency across different models."""
        # Create a credit card
        card = CreditCardFactory(issuer_country='Brazil', currency='BRL')
        
        # Create payments linked to the card
        payments = VariablePaymentFactory.create_batch(3, credit_card=card)
        
        # Create invoice for the card
        invoice = CreditCardInvoiceFactory(credit_card=card)
        
        # Verify relationships are maintained
        for payment in payments:
            self.assertEqual(payment.credit_card, card)
            self.assertEqual(payment.credit_card.issuer_country, 'Brazil')
        
        self.assertEqual(invoice.credit_card, card)
        self.assertEqual(invoice.credit_card.issuer_country, 'Brazil')
        
        # Test API consistency
        url = reverse('creditcard-detail', args=[card.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['issuer_country'], 'Brazil')
        self.assertEqual(response.data['currency'], 'BRL')


class PerformanceIntegrationTest(APITestCase):
    """Performance tests for the financial system."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        # Create large datasets
        profiles = UserFinancialProfileFactory.create_batch(10)
        cards = CreditCardFactory.create_batch(20)
        fixed_payments = FixedPaymentFactory.create_batch(50)
        variable_payments = VariablePaymentFactory.create_batch(100)
        invoices = CreditCardInvoiceFactory.create_batch(30)
        payment_statuses = PaymentStatusFactory.create_batch(80)
        
        # Test list endpoints performance
        import time
        
        start_time = time.time()
        url = reverse('variablepayment-list')
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(end_time - start_time, 2.0)
        
        # Test filtered queries performance
        start_time = time.time()
        url = reverse('variablepayment-by-category')
        response = self.client.get(url, {'category': 'food'})
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)
    
    def test_complex_queries_performance(self):
        """Test performance of complex queries and aggregations."""
        # Create diverse data
        cards = CreditCardFactory.create_batch(5)
        for card in cards:
            VariablePaymentFactory.create_batch(10, credit_card=card)
            CreditCardInvoiceFactory.create_batch(2, credit_card=card)
        
        # Test dashboard summary performance
        import time
        
        start_time = time.time()
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 3.0)
        
        # Test statistics performance
        start_time = time.time()
        url = reverse('variablepayment-statistics')
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 2.0)


class ErrorHandlingIntegrationTest(APITestCase):
    """Test error handling and edge cases in the system."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        # Test invalid currency
        data = {
            'issuer_country': 'Brazil',
            'currency': 'INVALID',
            'fx_fee_percent': '2.5',
            'iof_percent': '6.38',
            'cardholder_name': 'John Doe',
            'final_digits': '1234',
            'is_active': True
        }
        
        url = reverse('creditcard-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currency', response.data)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        data = {
            'issuer_country': 'Brazil',
            # Missing required fields
        }
        
        url = reverse('creditcard-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_data_handling(self):
        """Test handling of duplicate data."""
        # Create an exchange rate
        rate = ExchangeRateFactory(
            from_currency='BRL',
            to_currency='EUR',
            date=date.today()
        )
        
        # Try to create duplicate
        data = {
            'from_currency': 'BRL',
            'to_currency': 'EUR',
            'rate': '5.60',
            'date': rate.date.isoformat()
        }
        
        url = reverse('exchangerate-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nonexistent_resource_handling(self):
        """Test handling of requests for nonexistent resources."""
        url = reverse('creditcard-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthorized_access_handling(self):
        """Test handling of unauthorized access."""
        # Create a new client without authentication
        unauthenticated_client = APIClient()
        
        url = reverse('creditcard-list')
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DataIntegrityIntegrationTest(TestCase):
    """Test data integrity across the system."""
    
    def test_cascade_deletions(self):
        """Test that cascade deletions work correctly."""
        # Create a credit card
        card = CreditCardFactory()
        
        # Create payments linked to the card
        payments = VariablePaymentFactory.create_batch(3, credit_card=card)
        
        # Create invoice for the card
        invoice = CreditCardInvoiceFactory(credit_card=card)
        
        # Delete the card
        card.delete()
        
        # Verify related objects are handled correctly
        for payment in payments:
            payment.refresh_from_db()
            self.assertIsNone(payment.credit_card)
        
        # Invoice should be deleted
        self.assertFalse(CreditCardInvoice.objects.filter(id=invoice.id).exists())
    
    def test_unique_constraints(self):
        """Test that unique constraints are enforced."""
        # Test exchange rate unique constraint
        rate1 = ExchangeRateFactory(
            from_currency='BRL',
            to_currency='EUR',
            date=date.today()
        )
        
        with self.assertRaises(Exception):
            ExchangeRateFactory(
                from_currency='BRL',
                to_currency='EUR',
                date=date.today()
            )
        
        # Test payment status unique constraint
        fixed_payment = FixedPaymentFactory()
        month_year = date.today().replace(day=1)
        
        PaymentStatusFactory(
            fixed_payment=fixed_payment,
            month_year=month_year
        )
        
        with self.assertRaises(Exception):
            PaymentStatusFactory(
                fixed_payment=fixed_payment,
                month_year=month_year
            )
    
    def test_data_validation(self):
        """Test that data validation works correctly."""
        # Test invalid currency
        with self.assertRaises(Exception):
            CreditCardFactory(currency='INVALID')
        
        # Test invalid country
        with self.assertRaises(Exception):
            FixedPaymentFactory(country='INVALID')
        
        # Test invalid payment type
        with self.assertRaises(Exception):
            PaymentStatusFactory(payment_type='INVALID')
    
    def test_calculated_fields_accuracy(self):
        """Test that calculated fields are accurate."""
        # Test total_amount_with_fees calculation
        payment = VariablePaymentFactory(
            amount=Decimal('100.00'),
            fx_fee_amount=Decimal('5.00'),
            iof_amount=Decimal('2.00')
        )
        
        expected_total = Decimal('107.00')
        self.assertEqual(payment.total_amount_with_fees, expected_total)
        
        # Test total_monthly_income_base_currency calculation
        profile = UserFinancialProfileFactory(
            base_currency='EUR',
            monthly_income_eur=Decimal('2000.00'),
            monthly_income_brl=Decimal('10000.00')
        )
        
        self.assertEqual(profile.total_monthly_income_base_currency, Decimal('2000.00'))
        
        profile.base_currency = 'BRL'
        profile.save()
        self.assertEqual(profile.total_monthly_income_base_currency, Decimal('10000.00')) 