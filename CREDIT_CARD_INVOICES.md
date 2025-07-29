# Credit Card Invoice System

This document describes the credit card invoice tracking system implemented in the Django finance app.

## Overview

The credit card invoice system allows you to track monthly billing periods for credit cards, manage payment statuses, and automatically create new invoices when the current one is closed.

## Models

### CreditCardInvoice

Represents a billing period for a specific credit card.

**Fields:**
- `credit_card`: ForeignKey to CreditCard
- `start_date`: Start date of the billing period
- `end_date`: End date of the billing period
- `is_closed`: Boolean indicating if the invoice is closed
- `created_at`, `updated_at`: Timestamps

**Properties:**
- `total_amount`: Calculated total of all payment statuses (read-only)
- `purchases_count`: Number of payment statuses (read-only)
- `total_with_fees`: Same as total_amount for invoices
- `billing_period_days`: Number of days in the billing period

**Methods:**
- `close_invoice()`: Closes the invoice and creates the next one
- `create_next_invoice()`: Creates the next billing period
- `recalculate_totals()`: Recalculates totals (kept for compatibility)

### PaymentStatus (Updated)

The PaymentStatus model has been extended to support credit card invoices.

**New Fields:**
- `credit_card_invoice`: ForeignKey to CreditCardInvoice (optional)
- `payment_type`: Now includes 'credit_card' option

**Payment Types:**
- `fixed`: Fixed payments
- `variable`: Variable payments  
- `credit_card`: Credit card invoice payments

## Business Rules

1. **Invoice Creation**: Invoices are created for specific billing periods (typically monthly)
2. **Payment Association**: PaymentStatus records can be linked to invoices
3. **Automatic Next Invoice**: When an invoice is closed, a new one is automatically created
4. **Calculated Totals**: Invoice totals are calculated from associated PaymentStatus records
5. **Flexible Billing Periods**: Billing periods can vary in length (handles month-end edge cases)

## API Endpoints

### Credit Card Invoices

- `GET /api/credit-card-invoices/` - List all invoices
- `POST /api/credit-card-invoices/` - Create new invoice
- `GET /api/credit-card-invoices/{id}/` - Get invoice details
- `PUT /api/credit-card-invoices/{id}/` - Update invoice
- `DELETE /api/credit-card-invoices/{id}/` - Delete invoice
- `POST /api/credit-card-invoices/{id}/close_invoice/` - Close invoice
- `GET /api/credit-card-invoices/open/` - Get open invoices only
- `GET /api/credit-card-invoices/closed/` - Get closed invoices only
- `GET /api/credit-card-invoices/by_credit_card/?credit_card_id=X` - Get invoices for specific card
- `GET /api/credit-card-invoices/summary/` - Get invoice statistics

### Payment Statuses

- `GET /api/payment-statuses/` - List all payment statuses
- `POST /api/payment-statuses/` - Create new payment status
- `GET /api/payment-statuses/{id}/` - Get payment status details
- `PUT /api/payment-statuses/{id}/` - Update payment status
- `DELETE /api/payment-statuses/{id}/` - Delete payment status

## Admin Interface

### CreditCardInvoiceAdmin

The admin interface provides:
- List view with credit card, dates, status, and calculated totals
- Filtering by credit card, closed status, and dates
- Search by cardholder name and final digits
- Editable closed status
- Actions to close multiple invoices and recalculate totals

### PaymentStatusAdmin

Updated to include:
- Credit card invoice relationship
- Payment type filtering
- Enhanced display fields

## Management Commands

### create_initial_invoices

Creates initial invoices for existing credit cards.

```bash
# Create invoices for all active credit cards (3 months default)
python manage.py create_initial_invoices

# Create invoices for specific number of months
python manage.py create_initial_invoices --months 6

# Create invoices for specific credit card
python manage.py create_initial_invoices --credit-card-id 1
```

## Usage Examples

### Creating an Invoice

```python
from finance.models import CreditCard, CreditCardInvoice
from datetime import datetime, timedelta

# Get a credit card
credit_card = CreditCard.objects.get(id=1)

# Create invoice for current month
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
```

### Linking Payments to Invoices

```python
from finance.models import PaymentStatus, FixedPayment, VariablePayment

# Create payment status for fixed payment
fixed_payment = FixedPayment.objects.get(id=1)
payment_status = PaymentStatus.objects.create(
    fixed_payment=fixed_payment,
    payment_type='fixed',
    month_year=invoice.start_date,
    due_date=invoice.end_date + timedelta(days=10),
    expected_amount=fixed_payment.amount,
    currency=fixed_payment.currency
)

# Create payment status for variable payment
variable_payment = VariablePayment.objects.get(id=1)
payment_status = PaymentStatus.objects.create(
    variable_payment=variable_payment,
    payment_type='variable',
    month_year=invoice.start_date,
    due_date=invoice.end_date + timedelta(days=5),
    expected_amount=variable_payment.total_amount_with_fees,
    currency=variable_payment.currency
)

# Create payment status for credit card invoice
payment_status = PaymentStatus.objects.create(
    credit_card_invoice=invoice,
    payment_type='credit_card',
    month_year=invoice.start_date,
    due_date=invoice.end_date + timedelta(days=10),
    expected_amount=invoice.total_amount,
    currency=invoice.credit_card.currency
)
```

### Closing an Invoice

```python
# Close the invoice (automatically creates next one)
invoice.close_invoice()

# Check if new invoice was created
new_invoice = CreditCardInvoice.objects.filter(
    credit_card=invoice.credit_card,
    is_closed=False
).exclude(id=invoice.id).first()
```

### Getting Invoice Totals

```python
# Get calculated totals
total_amount = invoice.total_amount
payment_count = invoice.purchases_count
billing_days = invoice.billing_period_days
```

## Database Schema

### CreditCardInvoice Table

```sql
CREATE TABLE finance_creditcardinvoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (credit_card_id) REFERENCES finance_creditcard (id)
);
```

### Updated PaymentStatus Table

```sql
ALTER TABLE finance_paymentstatus ADD COLUMN credit_card_invoice_id INTEGER;
ALTER TABLE finance_paymentstatus ADD FOREIGN KEY (credit_card_invoice_id) REFERENCES finance_creditcardinvoice (id);
```

## Testing

Run the example script to test the system:

```bash
python create_invoice_example.py
```

This will:
1. Create a sample credit card
2. Create an invoice for the current month
3. Create sample payments and payment statuses
4. Demonstrate closing an invoice and creating the next one

## Migration Notes

The system includes a migration that:
1. Adds the CreditCardInvoice model
2. Updates PaymentStatus to include credit_card_invoice field
3. Updates payment_type choices to include 'credit_card'
4. Updates unique constraints for PaymentStatus

## Future Enhancements

Potential improvements:
1. **Recurring Invoice Creation**: Automatically create invoices for future periods
2. **Invoice Templates**: Predefined invoice structures
3. **Payment Scheduling**: Automatic payment status creation
4. **Invoice Notifications**: Email/SMS reminders for due payments
5. **Multi-Currency Support**: Handle invoices in different currencies
6. **Invoice Export**: PDF/Excel export functionality
7. **Payment Integration**: Connect with actual payment processors 