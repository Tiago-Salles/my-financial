#!/usr/bin/env python
"""
Example script demonstrating the credit card invoice system.

This script shows how to:
1. Create a credit card
2. Create invoices for the credit card
3. Create payment statuses linked to invoices
4. Close an invoice and automatically create the next one
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_financial.settings')
django.setup()

from finance.models import CreditCard, CreditCardInvoice, PaymentStatus, FixedPayment, VariablePayment


def create_example_data():
    """Create example data to demonstrate the invoice system."""
    
    print("Creating example credit card...")
    
    # Create a credit card
    credit_card = CreditCard.objects.create(
        issuer_country='Brazil',
        currency='BRL',
        fx_fee_percent=Decimal('2.5'),
        iof_percent=Decimal('0.38'),
        cardholder_name='João Silva',
        final_digits='1234',
        is_active=True
    )
    
    print(f"Created credit card: {credit_card}")
    
    # Create an invoice for the current month
    current_date = datetime.now().date()
    start_date = current_date.replace(day=1)
    
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
    
    invoice = CreditCardInvoice.objects.create(
        credit_card=credit_card,
        start_date=start_date,
        end_date=end_date,
        is_closed=False
    )
    
    print(f"Created invoice: {invoice}")
    print(f"  Period: {start_date} to {end_date}")
    print(f"  Total amount: {invoice.total_amount}")
    print(f"  Payment count: {invoice.purchases_count}")
    
    # Create some example payments
    print("\nCreating example payments...")
    
    # Create a fixed payment
    fixed_payment = FixedPayment.objects.create(
        description='Netflix Subscription',
        amount=Decimal('29.90'),
        currency='BRL',
        country='Brazil',
        frequency='monthly',
        start_date=current_date,
        is_active=True
    )
    
    # Create a variable payment
    variable_payment = VariablePayment.objects.create(
        date=current_date,
        description='Grocery Shopping',
        amount=Decimal('150.00'),
        currency='BRL',
        country='Brazil',
        category='food',
        linked_credit_card=True,
        credit_card=credit_card
    )
    
    # Create payment statuses linked to the invoice
    print("Creating payment statuses...")
    
    # Fixed payment status
    fixed_payment_status = PaymentStatus.objects.create(
        fixed_payment=fixed_payment,
        payment_type='fixed',
        month_year=current_date.replace(day=1),
        due_date=current_date + timedelta(days=15),
        status='pending',
        expected_amount=fixed_payment.amount,
        currency=fixed_payment.currency
    )
    
    # Variable payment status
    variable_payment_status = PaymentStatus.objects.create(
        variable_payment=variable_payment,
        payment_type='variable',
        month_year=current_date.replace(day=1),
        due_date=current_date + timedelta(days=5),
        status='pending',
        expected_amount=variable_payment.total_amount_with_fees,
        currency=variable_payment.currency
    )
    
    # Credit card invoice payment status
    invoice_payment_status = PaymentStatus.objects.create(
        credit_card_invoice=invoice,
        payment_type='credit_card',
        month_year=current_date.replace(day=1),
        due_date=end_date + timedelta(days=10),  # Due 10 days after invoice end
        status='pending',
        expected_amount=invoice.total_amount,
        currency=credit_card.currency
    )
    
    print(f"Created payment statuses:")
    print(f"  Fixed payment: {fixed_payment_status}")
    print(f"  Variable payment: {variable_payment_status}")
    print(f"  Credit card invoice: {invoice_payment_status}")
    
    # Update invoice totals
    invoice.recalculate_totals()
    
    print(f"\nUpdated invoice totals:")
    print(f"  Total amount: {invoice.total_amount}")
    print(f"  Payment count: {invoice.purchases_count}")
    
    return credit_card, invoice


def demonstrate_invoice_closing(credit_card, invoice):
    """Demonstrate closing an invoice and creating the next one."""
    
    print(f"\n{'='*50}")
    print("DEMONSTRATING INVOICE CLOSING")
    print(f"{'='*50}")
    
    print(f"Current invoice: {invoice}")
    print(f"  Is closed: {invoice.is_closed}")
    print(f"  Total amount: {invoice.total_amount}")
    print(f"  Payment count: {invoice.purchases_count}")
    
    # Close the invoice
    print("\nClosing invoice...")
    invoice.close_invoice()
    
    print(f"After closing:")
    print(f"  Is closed: {invoice.is_closed}")
    
    # Check if a new invoice was created
    new_invoice = CreditCardInvoice.objects.filter(
        credit_card=credit_card,
        is_closed=False
    ).exclude(id=invoice.id).first()
    
    if new_invoice:
        print(f"New invoice created: {new_invoice}")
        print(f"  Period: {new_invoice.start_date} to {new_invoice.end_date}")
        print(f"  Is closed: {new_invoice.is_closed}")
    else:
        print("No new invoice was created.")


def main():
    """Main function to run the example."""
    
    print("Credit Card Invoice System Example")
    print("=" * 40)
    
    try:
        # Create example data
        credit_card, invoice = create_example_data()
        
        # Demonstrate invoice closing
        demonstrate_invoice_closing(credit_card, invoice)
        
        print(f"\n{'='*50}")
        print("EXAMPLE COMPLETED SUCCESSFULLY")
        print(f"{'='*50}")
        
        # Show summary
        print(f"\nSummary:")
        print(f"  Credit cards: {CreditCard.objects.count()}")
        print(f"  Invoices: {CreditCardInvoice.objects.count()}")
        print(f"  Payment statuses: {PaymentStatus.objects.count()}")
        print(f"  Fixed payments: {FixedPayment.objects.count()}")
        print(f"  Variable payments: {VariablePayment.objects.count()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 