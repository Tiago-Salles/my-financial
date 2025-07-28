#!/usr/bin/env python
"""
Data population script for the Personal Financial Tracker.
This script creates realistic sample data for testing and development.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_financial.settings')
django.setup()

from finance.models import (
    UserFinancialProfile,
    CreditCard,
    ExchangeRate,
    FixedPayment,
    VariablePayment
)
from finance.factories import (
    UserFinancialProfileFactory,
    CreditCardFactory,
    ExchangeRateFactory,
    FixedPaymentFactory,
    VariablePaymentFactory,
    BrazilianCreditCardFactory,
    PortugueseCreditCardFactory,
    UniversityPaymentFactory,
    RentPaymentFactory,
    FoodExpenseFactory,
    TransportExpenseFactory,
    RealisticExchangeRateFactory
)


def clear_data():
    """Clear all existing data."""
    print("🗑️  Clearing existing data...")
    VariablePayment.objects.all().delete()
    FixedPayment.objects.all().delete()
    ExchangeRate.objects.all().delete()
    CreditCard.objects.all().delete()
    UserFinancialProfile.objects.all().delete()
    print("✅ Data cleared successfully")


def create_user_profile():
    """Create a user financial profile."""
    print("👤 Creating user profile...")
    profile = UserFinancialProfileFactory(
        name="Tiago Silva",
        base_currency="EUR",
        monthly_income_brl=Decimal("8000.00"),
        monthly_income_eur=Decimal("2500.00")
    )
    print(f"✅ Created profile: {profile}")
    return profile


def create_credit_cards():
    """Create realistic credit cards."""
    print("💳 Creating credit cards...")
    
    # Brazilian credit cards
    brazilian_cards = [
        BrazilianCreditCardFactory(
            cardholder_name="Tiago Silva",
            final_digits="1234",
            fx_fee_percent=Decimal("4.5"),
            iof_percent=Decimal("6.38")
        ),
        BrazilianCreditCardFactory(
            cardholder_name="Tiago Silva",
            final_digits="5678",
            fx_fee_percent=Decimal("3.2"),
            iof_percent=Decimal("6.38")
        )
    ]
    
    # Portuguese credit card
    portuguese_card = PortugueseCreditCardFactory(
        cardholder_name="Tiago Silva",
        final_digits="9012",
        fx_fee_percent=Decimal("2.1")
    )
    
    cards = brazilian_cards + [portuguese_card]
    print(f"✅ Created {len(cards)} credit cards")
    return cards


def create_exchange_rates():
    """Create realistic exchange rates."""
    print("💱 Creating exchange rates...")
    
    # Create realistic rates for the last 30 days
    rates = []
    for i in range(30):
        rate_date = date.today() - timedelta(days=i)
        
        # BRL to EUR
        rates.append(RealisticExchangeRateFactory(
            from_currency="BRL",
            to_currency="EUR",
            date=rate_date
        ))
        
        # EUR to BRL
        rates.append(RealisticExchangeRateFactory(
            from_currency="EUR",
            to_currency="BRL",
            date=rate_date
        ))
        
        # BRL to USD
        rates.append(RealisticExchangeRateFactory(
            from_currency="BRL",
            to_currency="USD",
            date=rate_date
        ))
        
        # USD to BRL
        rates.append(RealisticExchangeRateFactory(
            from_currency="USD",
            to_currency="BRL",
            date=rate_date
        ))
        
        # EUR to USD
        rates.append(RealisticExchangeRateFactory(
            from_currency="EUR",
            to_currency="USD",
            date=rate_date
        ))
        
        # USD to EUR
        rates.append(RealisticExchangeRateFactory(
            from_currency="USD",
            to_currency="EUR",
            date=rate_date
        ))
    
    print(f"✅ Created {len(rates)} exchange rates")
    return rates


def create_fixed_payments():
    """Create realistic fixed payments."""
    print("💰 Creating fixed payments...")
    
    payments = []
    
    # Brazilian payments
    brazilian_payments = [
        UniversityPaymentFactory(
            description="University Tuition",
            amount=Decimal("1200.00"),
            start_date=date.today() - timedelta(days=90)
        ),
        FixedPaymentFactory(
            country="Brazil",
            description="Netflix Subscription",
            amount=Decimal("39.90"),
            currency="BRL",
            frequency="monthly",
            start_date=date.today() - timedelta(days=180)
        ),
        FixedPaymentFactory(
            country="Brazil",
            description="Spotify Premium",
            amount=Decimal("19.90"),
            currency="BRL",
            frequency="monthly",
            start_date=date.today() - timedelta(days=120)
        )
    ]
    
    # Portuguese payments
    portuguese_payments = [
        RentPaymentFactory(
            description="Rent",
            amount=Decimal("800.00"),
            start_date=date.today() - timedelta(days=60)
        ),
        FixedPaymentFactory(
            country="Portugal",
            description="Internet",
            amount=Decimal("45.00"),
            currency="EUR",
            frequency="monthly",
            start_date=date.today() - timedelta(days=90)
        ),
        FixedPaymentFactory(
            country="Portugal",
            description="Phone Bill",
            amount=Decimal("25.00"),
            currency="EUR",
            frequency="monthly",
            start_date=date.today() - timedelta(days=60)
        ),
        FixedPaymentFactory(
            country="Portugal",
            description="Gym Membership",
            amount=Decimal("35.00"),
            currency="EUR",
            frequency="monthly",
            start_date=date.today() - timedelta(days=45)
        )
    ]
    
    payments = brazilian_payments + portuguese_payments
    print(f"✅ Created {len(payments)} fixed payments")
    return payments


def create_variable_payments(cards):
    """Create realistic variable payments."""
    print("🛒 Creating variable payments...")
    
    payments = []
    
    # Create payments for the last 30 days
    for i in range(30):
        payment_date = date.today() - timedelta(days=i)
        
        # Create 2-5 payments per day
        daily_payments = random.randint(2, 5)
        
        for _ in range(daily_payments):
            # 70% chance to use a credit card
            use_credit_card = random.random() < 0.7
            credit_card = random.choice(cards) if use_credit_card else None
            
            # Create different types of expenses
            expense_type = random.choice(['food', 'transport', 'entertainment', 'shopping'])
            
            if expense_type == 'food':
                payment = FoodExpenseFactory(
                    date=payment_date,
                    linked_credit_card=use_credit_card,
                    credit_card=credit_card
                )
            elif expense_type == 'transport':
                payment = TransportExpenseFactory(
                    date=payment_date,
                    linked_credit_card=use_credit_card,
                    credit_card=credit_card
                )
            else:
                payment = VariablePaymentFactory(
                    date=payment_date,
                    linked_credit_card=use_credit_card,
                    credit_card=credit_card
                )
            
            payments.append(payment)
    
    print(f"✅ Created {len(payments)} variable payments")
    return payments


def create_realistic_scenario():
    """Create a realistic financial scenario."""
    print("🎯 Creating realistic financial scenario...")
    
    # Clear existing data
    clear_data()
    
    # Create user profile
    profile = create_user_profile()
    
    # Create credit cards
    cards = create_credit_cards()
    
    # Create exchange rates
    rates = create_exchange_rates()
    
    # Create fixed payments
    fixed_payments = create_fixed_payments()
    
    # Create variable payments
    variable_payments = create_variable_payments(cards)
    
    # Print summary
    print("\n📊 Data Population Summary:")
    print(f"   👤 User Profiles: {UserFinancialProfile.objects.count()}")
    print(f"   💳 Credit Cards: {CreditCard.objects.count()}")
    print(f"   💱 Exchange Rates: {ExchangeRate.objects.count()}")
    print(f"   💰 Fixed Payments: {FixedPayment.objects.count()}")
    print(f"   🛒 Variable Payments: {VariablePayment.objects.count()}")
    
    # Calculate some statistics
    total_expenses = sum(p.amount for p in variable_payments)
    total_fees = sum(p.fx_fee_amount + p.iof_amount for p in variable_payments)
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total Expenses: {total_expenses:.2f}")
    print(f"   Total Fees: {total_fees:.2f}")
    print(f"   Average Daily Expense: {total_expenses/30:.2f}")
    
    print("\n✅ Data population completed successfully!")
    print("🌐 Access the admin at: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin")


def create_minimal_data():
    """Create minimal data for testing."""
    print("🔧 Creating minimal test data...")
    
    # Clear existing data
    clear_data()
    
    # Create basic data
    profile = UserFinancialProfileFactory()
    card = CreditCardFactory()
    rate = ExchangeRateFactory()
    fixed_payment = FixedPaymentFactory()
    variable_payment = VariablePaymentFactory()
    
    print("✅ Minimal data created successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--minimal":
        create_minimal_data()
    else:
        create_realistic_scenario() 