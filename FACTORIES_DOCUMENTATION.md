# Factory Documentation

This document describes all the factories available in the finance app for creating test data.

## Overview

The factories use the `factory_boy` library to create realistic test data for all models in the finance app. They include specialized factories for different scenarios and use cases.

## Core Factories

### UserFinancialProfileFactory

Creates user financial profiles with realistic data.

```python
from finance.factories import UserFinancialProfileFactory

# Create a basic profile
profile = UserFinancialProfileFactory()

# Create with specific currency
profile = UserFinancialProfileFactory(base_currency='BRL')
```

**Fields:**
- `name`: Random name using Faker
- `base_currency`: Randomly 'BRL' or 'EUR'
- `monthly_income_brl`: Random amount between 2000-15000 BRL
- `monthly_income_eur`: Random amount between 1000-8000 EUR

### CreditCardFactory

Creates credit cards with realistic settings.

```python
from finance.factories import CreditCardFactory

# Create a basic credit card
card = CreditCardFactory()

# Create an active card
card = CreditCardFactory(is_active=True)
```

**Fields:**
- `issuer_country`: Randomly 'Brazil' or 'Portugal'
- `currency`: Randomly 'BRL', 'EUR', or 'USD'
- `fx_fee_percent`: Random percentage 0-5%
- `iof_percent`: Random percentage 0-6.38%
- `cardholder_name`: Random name
- `final_digits`: Random 4-digit string
- `is_active`: 75% chance of being True

### CreditCardInvoiceFactory

Creates credit card invoices with realistic billing periods.

```python
from finance.factories import CreditCardInvoiceFactory

# Create a basic invoice
invoice = CreditCardInvoiceFactory()

# Create for specific credit card
card = CreditCardFactory()
invoice = CreditCardInvoiceFactory(credit_card=card)
```

**Fields:**
- `credit_card`: SubFactory of CreditCardFactory
- `start_date`: First day of current month
- `end_date`: Last day of current month
- `is_closed`: 75% chance of being False (open)

**Specialized Factories:**
- `OpenCreditCardInvoiceFactory`: Always creates open invoices
- `ClosedCreditCardInvoiceFactory`: Always creates closed invoices

### ExchangeRateFactory

Creates exchange rates with realistic values.

```python
from finance.factories import ExchangeRateFactory

# Create a basic exchange rate
rate = ExchangeRateFactory()

# Create for specific currency pair
rate = ExchangeRateFactory(from_currency='BRL', to_currency='EUR')
```

**Fields:**
- `from_currency`: Random currency
- `to_currency`: Random currency
- `rate`: Random rate between 0.1-10.0
- `date`: Random date within last 30 days

**Post-generation:**
- Ensures `from_currency` and `to_currency` are different
- Sets rate to 1.0 if currencies are the same

### FixedPaymentFactory

Creates fixed payments with realistic descriptions and amounts.

```python
from finance.factories import FixedPaymentFactory

# Create a basic fixed payment
payment = FixedPaymentFactory()

# Create for specific country
payment = FixedPaymentFactory(country='Brazil')
```

**Fields:**
- `country`: Randomly 'Brazil' or 'Portugal'
- `description`: Random from predefined list
- `amount`: Random amount between 50-2000
- `currency`: Random currency
- `frequency`: Randomly 'monthly' or 'yearly'
- `start_date`: Random date within last year
- `end_date`: Random future date or None
- `is_active`: 75% chance of being True

### VariablePaymentFactory

Creates variable payments with realistic categories and amounts.

```python
from finance.factories import VariablePaymentFactory

# Create a basic variable payment
payment = VariablePaymentFactory()

# Create linked to credit card
payment = VariablePaymentFactory(linked_credit_card=True)
```

**Fields:**
- `date`: Random date within last 30 days
- `country`: Randomly 'Brazil' or 'Portugal'
- `description`: Random from predefined list
- `amount`: Random amount between 5-500
- `currency`: Random currency
- `category`: Random category
- `linked_credit_card`: 66% chance of being True
- `credit_card`: SubFactory of CreditCardFactory
- `fx_fee_amount`: Calculated based on credit card
- `iof_amount`: Calculated based on credit card and country

**Post-generation:**
- Calculates FX fees if linked to credit card
- Calculates IOF for Brazilian cards on foreign transactions

## Payment Status Factories

### PaymentStatusFactory

Creates payment status records with random types and realistic data.

```python
from finance.factories import PaymentStatusFactory

# Create a basic payment status
status = PaymentStatusFactory()

# Create for specific type
status = PaymentStatusFactory(payment_type='fixed')
```

**Fields:**
- `payment_type`: Randomly 'fixed', 'variable', or 'credit_card'
- `month_year`: Random month within last year
- `due_date`: Random future date
- `status`: Randomly 'pending', 'paid', or 'overdue'
- `is_paid`: True if status is 'paid'
- `paid_date`: Today's date if paid, None otherwise
- `expected_amount`: Random amount between 50-2000
- `actual_amount`: Random amount between 50-2000
- `currency`: Random currency
- `notes`: Random note or None

**Post-generation:**
- Links to appropriate payment based on type
- Sets expected amount and currency from linked payment

### FixedPaymentStatusFactory

Creates payment statuses specifically for fixed payments.

```python
from finance.factories import FixedPaymentStatusFactory

# Create payment status for fixed payment
status = FixedPaymentStatusFactory()
```

**Fields:**
- `payment_type`: Always 'fixed'
- `fixed_payment`: SubFactory of FixedPaymentFactory

### VariablePaymentStatusFactory

Creates payment statuses specifically for variable payments.

```python
from finance.factories import VariablePaymentStatusFactory

# Create payment status for variable payment
status = VariablePaymentStatusFactory()
```

**Fields:**
- `payment_type`: Always 'variable'
- `variable_payment`: SubFactory of VariablePaymentFactory

### CreditCardInvoicePaymentStatusFactory

Creates payment statuses specifically for credit card invoices.

```python
from finance.factories import CreditCardInvoicePaymentStatusFactory

# Create payment status for credit card invoice
status = CreditCardInvoicePaymentStatusFactory()
```

**Fields:**
- `payment_type`: Always 'credit_card'
- `credit_card_invoice`: SubFactory of CreditCardInvoiceFactory

## Specialized Factories

### BrazilianCreditCardFactory

Creates Brazilian credit cards with typical IOF rates.

```python
from finance.factories import BrazilianCreditCardFactory

# Create Brazilian credit card
card = BrazilianCreditCardFactory()
```

**Fields:**
- `issuer_country`: Always 'Brazil'
- `currency`: Randomly 'BRL' or 'USD'
- `iof_percent`: Random percentage 6.0-6.38%

### PortugueseCreditCardFactory

Creates Portuguese credit cards.

```python
from finance.factories import PortugueseCreditCardFactory

# Create Portuguese credit card
card = PortugueseCreditCardFactory()
```

**Fields:**
- `issuer_country`: Always 'Portugal'
- `currency`: Always 'EUR'
- `iof_percent`: Always 0.00

### UniversityPaymentFactory

Creates university-related fixed payments.

```python
from finance.factories import UniversityPaymentFactory

# Create university payment
payment = UniversityPaymentFactory()
```

**Fields:**
- `country`: Always 'Brazil'
- `description`: Random university-related description
- `currency`: Always 'BRL'
- `frequency`: Always 'monthly'
- `amount`: Random amount between 500-2000

### RentPaymentFactory

Creates rent payments (typically Portuguese).

```python
from finance.factories import RentPaymentFactory

# Create rent payment
payment = RentPaymentFactory()
```

**Fields:**
- `country`: Always 'Portugal'
- `description`: Always 'Rent'
- `currency`: Always 'EUR'
- `frequency`: Always 'monthly'
- `amount`: Random amount between 400-1200

### FoodExpenseFactory

Creates food-related variable payments.

```python
from finance.factories import FoodExpenseFactory

# Create food expense
payment = FoodExpenseFactory()
```

**Fields:**
- `description`: Random food-related description
- `category`: Always 'food'
- `amount`: Random amount between 5-100

### TransportExpenseFactory

Creates transport-related variable payments.

```python
from finance.factories import TransportExpenseFactory

# Create transport expense
payment = TransportExpenseFactory()
```

**Fields:**
- `description`: Random transport-related description
- `category`: Always 'transport'
- `amount`: Random amount between 2-50

### RealisticExchangeRateFactory

Creates exchange rates with realistic values based on currency pairs.

```python
from finance.factories import RealisticExchangeRateFactory

# Create realistic exchange rate
rate = RealisticExchangeRateFactory()
```

**Post-generation:**
- Sets realistic rates for common currency pairs
- BRL/EUR: 0.15-0.20
- EUR/BRL: 5.0-6.5
- BRL/USD: 0.18-0.22
- USD/BRL: 4.5-5.5
- EUR/USD: 1.05-1.15
- USD/EUR: 0.85-0.95

## Usage Examples

### Creating Test Data

```python
from finance.factories import *

# Create a complete financial profile
profile = UserFinancialProfileFactory()
card = CreditCardFactory()
invoice = CreditCardInvoiceFactory(credit_card=card)

# Create payments for the invoice
fixed_payment = FixedPaymentFactory()
variable_payment = VariablePaymentFactory(credit_card=card)

# Create payment statuses
fixed_status = FixedPaymentStatusFactory(
    fixed_payment=fixed_payment,
    credit_card_invoice=invoice
)
variable_status = VariablePaymentStatusFactory(
    variable_payment=variable_payment,
    credit_card_invoice=invoice
)
invoice_status = CreditCardInvoicePaymentStatusFactory(
    credit_card_invoice=invoice
)
```

### Bulk Creation

```python
# Create multiple records
cards = CreditCardFactory.create_batch(5)
invoices = CreditCardInvoiceFactory.create_batch(10)
payments = VariablePaymentFactory.create_batch(20)
```

### Creating Related Data

```python
# Create invoice with specific credit card
card = CreditCardFactory()
invoice = CreditCardInvoiceFactory(credit_card=card)

# Create payment statuses for the invoice
PaymentStatusFactory.create_batch(
    3, 
    credit_card_invoice=invoice,
    payment_type='fixed'
)
```

### Testing Different Scenarios

```python
# Test Brazilian scenario
brazilian_card = BrazilianCreditCardFactory()
brazilian_invoice = CreditCardInvoiceFactory(credit_card=brazilian_card)

# Test Portuguese scenario
portuguese_card = PortugueseCreditCardFactory()
portuguese_invoice = CreditCardInvoiceFactory(credit_card=portuguese_card)

# Test food expenses
food_payments = FoodExpenseFactory.create_batch(5)

# Test transport expenses
transport_payments = TransportExpenseFactory.create_batch(3)
```

## Best Practices

1. **Use Specific Factories**: Use specialized factories when you need specific data patterns
2. **Override Fields**: Pass specific values when needed
3. **Create Related Data**: Use SubFactory for automatic related object creation
4. **Bulk Creation**: Use create_batch for multiple records
5. **Post-generation**: Leverage post-generation hooks for complex logic

## Testing

Run the test script to see all factories in action:

```bash
python test_factories.py
```

This will demonstrate:
- Creating different types of invoices
- Creating payment statuses with various types
- Linking payments to invoices
- Bulk creation scenarios 