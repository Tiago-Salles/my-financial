#!/usr/bin/env python
"""
Script to create PaymentStatus records for existing payments.
This creates a monthly checklist of payments to be made.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_financial.settings')
django.setup()

from finance.models import FixedPayment, VariablePayment, PaymentStatus
from finance.factories import PaymentStatusFactory, FixedPaymentStatusFactory, VariablePaymentStatusFactory
from django.utils import timezone


def create_payment_status_records():
    """Create PaymentStatus records for existing payments."""
    
    print("🎯 Creating PaymentStatus records...")
    
    # Get existing payments
    fixed_payments = FixedPayment.objects.filter(is_active=True)
    variable_payments = VariablePayment.objects.all()
    
    print(f"📋 Found {fixed_payments.count()} active fixed payments")
    print(f"📋 Found {variable_payments.count()} variable payments")
    
    # Create PaymentStatus for fixed payments (last 3 months)
    for payment in fixed_payments:
        for i in range(3):  # Last 3 months
            month_date = date.today().replace(day=1) - timedelta(days=30*i)
            
            # Skip if payment status already exists
            if PaymentStatus.objects.filter(
                fixed_payment=payment,
                month_year=month_date
            ).exists():
                continue
            
            # Create payment status
            status = FixedPaymentStatusFactory(
                fixed_payment=payment,
                month_year=month_date,
                due_date=month_date + timedelta(days=random.randint(1, 15)),
                status=random.choice(['pending', 'paid', 'overdue']),
                is_paid=random.choice([True, False]),
                notes=random.choice([
                    'Payment scheduled',
                    'Payment completed',
                    'Pending confirmation',
                    'Late payment',
                    None
                ])
            )
            print(f"✅ Created status for {payment.description} - {month_date.strftime('%B %Y')}")
    
    # Create PaymentStatus for variable payments (last month)
    for payment in variable_payments[:20]:  # Limit to 20 recent payments
        month_date = payment.date.replace(day=1)
        
        # Skip if payment status already exists
        if PaymentStatus.objects.filter(
            variable_payment=payment,
            month_year=month_date
        ).exists():
            continue
        
        # Create payment status
        status = VariablePaymentStatusFactory(
            variable_payment=payment,
            month_year=month_date,
            due_date=payment.date,
            status='paid',  # Variable payments are usually already paid
            is_paid=True,
            paid_date=payment.date,
            notes='Payment completed'
        )
        print(f"✅ Created status for {payment.description} - {month_date.strftime('%B %Y')}")
    
    # Summary
    total_status = PaymentStatus.objects.count()
    pending_status = PaymentStatus.objects.filter(status='pending').count()
    paid_status = PaymentStatus.objects.filter(status='paid').count()
    overdue_status = PaymentStatus.objects.filter(status='overdue').count()
    
    print(f"\n📊 PaymentStatus Summary:")
    print(f"   Total Records: {total_status}")
    print(f"   Pending: {pending_status}")
    print(f"   Paid: {paid_status}")
    print(f"   Overdue: {overdue_status}")
    
    print("\n✅ PaymentStatus records created successfully!")
    print("🌐 Access the admin at: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin")


if __name__ == '__main__':
    import random
    create_payment_status_records() 