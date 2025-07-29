#!/usr/bin/env python
"""
Test script for the new CreditCardInvoice factory and updated PaymentStatus factory.

This script demonstrates:
1. Creating credit card invoices with factories
2. Creating payment statuses linked to invoices
3. Testing the different factory types
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_financial.settings')
django.setup()

from finance.factories import (
    CreditCardInvoiceFactory,
    OpenCreditCardInvoiceFactory,
    ClosedCreditCardInvoiceFactory,
    PaymentStatusFactory,
    FixedPaymentStatusFactory,
    VariablePaymentStatusFactory,
    CreditCardInvoicePaymentStatusFactory,
    CreditCardFactory,
    FixedPaymentFactory,
    VariablePaymentFactory
)


def test_credit_card_invoice_factories():
    """Test the different credit card invoice factories."""
    
    print("Testing Credit Card Invoice Factories")
    print("=" * 40)
    
    # Test basic invoice factory
    print("\n1. Basic CreditCardInvoiceFactory:")
    invoice = CreditCardInvoiceFactory()
    print(f"   Invoice: {invoice}")
    print(f"   Credit Card: {invoice.credit_card}")
    print(f"   Period: {invoice.start_date} to {invoice.end_date}")
    print(f"   Is Closed: {invoice.is_closed}")
    print(f"   Total Amount: {invoice.total_amount}")
    print(f"   Payment Count: {invoice.purchases_count}")
    
    # Test open invoice factory
    print("\n2. OpenCreditCardInvoiceFactory:")
    open_invoice = OpenCreditCardInvoiceFactory()
    print(f"   Invoice: {open_invoice}")
    print(f"   Is Closed: {open_invoice.is_closed}")
    
    # Test closed invoice factory
    print("\n3. ClosedCreditCardInvoiceFactory:")
    closed_invoice = ClosedCreditCardInvoiceFactory()
    print(f"   Invoice: {closed_invoice}")
    print(f"   Is Closed: {closed_invoice.is_closed}")
    
    return invoice, open_invoice, closed_invoice


def test_payment_status_factories():
    """Test the different payment status factories."""
    
    print("\n\nTesting Payment Status Factories")
    print("=" * 40)
    
    # Test basic payment status factory (random type)
    print("\n1. Basic PaymentStatusFactory (random type):")
    payment_status = PaymentStatusFactory()
    print(f"   Payment Status: {payment_status}")
    print(f"   Payment Type: {payment_status.payment_type}")
    print(f"   Expected Amount: {payment_status.expected_amount}")
    print(f"   Currency: {payment_status.currency}")
    
    # Test fixed payment status factory
    print("\n2. FixedPaymentStatusFactory:")
    fixed_status = FixedPaymentStatusFactory()
    print(f"   Payment Status: {fixed_status}")
    print(f"   Payment Type: {fixed_status.payment_type}")
    print(f"   Fixed Payment: {fixed_status.fixed_payment}")
    print(f"   Expected Amount: {fixed_status.expected_amount}")
    
    # Test variable payment status factory
    print("\n3. VariablePaymentStatusFactory:")
    variable_status = VariablePaymentStatusFactory()
    print(f"   Payment Status: {variable_status}")
    print(f"   Payment Type: {variable_status.payment_type}")
    print(f"   Variable Payment: {variable_status.variable_payment}")
    print(f"   Expected Amount: {variable_status.expected_amount}")
    
    # Test credit card invoice payment status factory
    print("\n4. CreditCardInvoicePaymentStatusFactory:")
    invoice_status = CreditCardInvoicePaymentStatusFactory()
    print(f"   Payment Status: {invoice_status}")
    print(f"   Payment Type: {invoice_status.payment_type}")
    print(f"   Credit Card Invoice: {invoice_status.credit_card_invoice}")
    print(f"   Expected Amount: {invoice_status.expected_amount}")
    
    return payment_status, fixed_status, variable_status, invoice_status


def test_invoice_with_payment_statuses():
    """Test creating an invoice with multiple payment statuses."""
    
    print("\n\nTesting Invoice with Payment Statuses")
    print("=" * 40)
    
    # Create a credit card
    credit_card = CreditCardFactory()
    print(f"Created Credit Card: {credit_card}")
    
    # Create an invoice for this credit card
    invoice = CreditCardInvoiceFactory(credit_card=credit_card)
    print(f"Created Invoice: {invoice}")
    print(f"  Period: {invoice.start_date} to {invoice.end_date}")
    print(f"  Is Closed: {invoice.is_closed}")
    
    # Create multiple payment statuses for this invoice
    print("\nCreating payment statuses for this invoice:")
    
    # Fixed payment status
    fixed_payment = FixedPaymentFactory()
    fixed_status = PaymentStatusFactory(
        fixed_payment=fixed_payment,
        credit_card_invoice=invoice,
        payment_type='fixed',
        expected_amount=fixed_payment.amount,
        currency=fixed_payment.currency
    )
    print(f"  Fixed Payment Status: {fixed_status}")
    
    # Variable payment status
    variable_payment = VariablePaymentFactory(credit_card=credit_card)
    variable_status = PaymentStatusFactory(
        variable_payment=variable_payment,
        credit_card_invoice=invoice,
        payment_type='variable',
        expected_amount=variable_payment.total_amount_with_fees,
        currency=variable_payment.currency
    )
    print(f"  Variable Payment Status: {variable_status}")
    
    # Credit card invoice payment status
    invoice_status = PaymentStatusFactory(
        credit_card_invoice=invoice,
        payment_type='credit_card',
        expected_amount=invoice.total_amount,
        currency=credit_card.currency
    )
    print(f"  Credit Card Invoice Status: {invoice_status}")
    
    # Refresh invoice to get updated totals
    invoice.refresh_from_db()
    
    print(f"\nUpdated Invoice Totals:")
    print(f"  Total Amount: {invoice.total_amount}")
    print(f"  Payment Count: {invoice.purchases_count}")
    
    return invoice


def test_bulk_creation():
    """Test creating multiple invoices and payment statuses."""
    
    print("\n\nTesting Bulk Creation")
    print("=" * 40)
    
    # Create multiple credit cards
    credit_cards = CreditCardFactory.create_batch(3)
    print(f"Created {len(credit_cards)} credit cards")
    
    # Create invoices for each credit card
    invoices = []
    for credit_card in credit_cards:
        invoice = CreditCardInvoiceFactory(credit_card=credit_card)
        invoices.append(invoice)
        print(f"  Created invoice for {credit_card}: {invoice}")
    
    # Create payment statuses for each invoice
    for invoice in invoices:
        # Create 2-4 payment statuses per invoice
        num_payments = 2 + (hash(str(invoice.id)) % 3)  # Deterministic but varied
        
        for i in range(num_payments):
            if i % 3 == 0:
                # Fixed payment
                fixed_payment = FixedPaymentFactory()
                PaymentStatusFactory(
                    fixed_payment=fixed_payment,
                    credit_card_invoice=invoice,
                    payment_type='fixed'
                )
            elif i % 3 == 1:
                # Variable payment
                variable_payment = VariablePaymentFactory(credit_card=invoice.credit_card)
                PaymentStatusFactory(
                    variable_payment=variable_payment,
                    credit_card_invoice=invoice,
                    payment_type='variable'
                )
            else:
                # Credit card invoice payment
                PaymentStatusFactory(
                    credit_card_invoice=invoice,
                    payment_type='credit_card'
                )
        
        # Refresh invoice to get updated totals
        invoice.refresh_from_db()
        print(f"  Invoice {invoice.id}: {invoice.purchases_count} payments, {invoice.total_amount} total")
    
    return invoices


def main():
    """Main function to run all tests."""
    
    print("Credit Card Invoice Factory Tests")
    print("=" * 50)
    
    try:
        # Test credit card invoice factories
        test_credit_card_invoice_factories()
        
        # Test payment status factories
        test_payment_status_factories()
        
        # Test invoice with payment statuses
        test_invoice_with_payment_statuses()
        
        # Test bulk creation
        test_bulk_creation()
        
        print(f"\n{'='*50}")
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print(f"{'='*50}")
        
        # Show summary
        from finance.models import CreditCardInvoice, PaymentStatus
        print(f"\nSummary:")
        print(f"  Credit Card Invoices: {CreditCardInvoice.objects.count()}")
        print(f"  Payment Statuses: {PaymentStatus.objects.count()}")
        print(f"  Open Invoices: {CreditCardInvoice.objects.filter(is_closed=False).count()}")
        print(f"  Closed Invoices: {CreditCardInvoice.objects.filter(is_closed=True).count()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 