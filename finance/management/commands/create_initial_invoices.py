from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from finance.models import CreditCard, CreditCardInvoice


class Command(BaseCommand):
    help = 'Create initial invoices for existing credit cards'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=3,
            help='Number of months to create invoices for (default: 3)'
        )
        parser.add_argument(
            '--credit-card-id',
            type=int,
            help='Create invoices for a specific credit card ID'
        )

    def handle(self, *args, **options):
        months = options['months']
        credit_card_id = options.get('credit_card_id')
        
        # Get credit cards to process
        if credit_card_id:
            credit_cards = CreditCard.objects.filter(id=credit_card_id, is_active=True)
        else:
            credit_cards = CreditCard.objects.filter(is_active=True)
        
        if not credit_cards.exists():
            self.stdout.write(
                self.style.WARNING('No active credit cards found.')
            )
            return
        
        created_count = 0
        
        for credit_card in credit_cards:
            self.stdout.write(f'Processing credit card: {credit_card}')
            
            # Check if invoices already exist for this card
            existing_invoices = CreditCardInvoice.objects.filter(credit_card=credit_card)
            if existing_invoices.exists():
                self.stdout.write(
                    self.style.WARNING(f'Invoices already exist for {credit_card}. Skipping.')
                )
                continue
            
            # Create invoices for the specified number of months
            current_date = timezone.now().date()
            
            for i in range(months):
                # Calculate start and end dates for this month
                if i == 0:
                    # First invoice starts from the beginning of current month
                    start_date = current_date.replace(day=1)
                else:
                    # Subsequent invoices start from the next month
                    if start_date.month == 12:
                        start_date = start_date.replace(year=start_date.year + 1, month=1)
                    else:
                        start_date = start_date.replace(month=start_date.month + 1)
                
                # Calculate end date (last day of the month)
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
                
                # Create the invoice
                invoice = CreditCardInvoice.objects.create(
                    credit_card=credit_card,
                    start_date=start_date,
                    end_date=end_date,
                    is_closed=False
                )
                
                created_count += 1
                self.stdout.write(
                    f'  Created invoice: {start_date} to {end_date}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} invoices.')
        ) 