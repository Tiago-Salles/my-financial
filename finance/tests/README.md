# Finance App Test Suite

This directory contains comprehensive unit tests for the finance app. The test suite is designed to provide heavy coverage of all components including models, serializers, views, and integration scenarios.

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── test_models.py           # Model tests (553 lines)
├── test_serializers.py      # Serializer tests (592 lines)
├── test_views.py            # View tests (740 lines)
├── test_factories.py        # Factory tests (471 lines)
├── test_integration.py      # Integration tests (497 lines)
├── test_config.py           # Test configuration and utilities
├── run_tests.py            # Test runner script
└── README.md               # This file
```

## Test Coverage

### Models (test_models.py)
- **UserFinancialProfileModelTest**: Tests user financial profiles, income calculations, and currency handling
- **CreditCardModelTest**: Tests credit card creation, validation, and specialized factories (Brazilian/Portuguese)
- **ExchangeRateModelTest**: Tests exchange rate creation, unique constraints, and realistic rate generation
- **FixedPaymentModelTest**: Tests fixed payments, active status, and specialized payment types
- **VariablePaymentModelTest**: Tests variable payments, fee calculations, and category-specific factories
- **PaymentStatusModelTest**: Tests payment status tracking, overdue detection, and unique constraints
- **CreditCardInvoiceModelTest**: Tests invoice creation, total calculations, and billing period management

### Serializers (test_serializers.py)
- **UserFinancialProfileSerializerTest**: Tests serialization/deserialization of user profiles
- **CreditCardSerializerTest**: Tests credit card data serialization with validation
- **CreditCardDetailSerializerTest**: Tests detailed credit card serialization with related payments
- **ExchangeRateSerializerTest**: Tests exchange rate serialization
- **FixedPaymentSerializerTest**: Tests fixed payment serialization
- **VariablePaymentSerializerTest**: Tests variable payment serialization with credit card relationships
- **PaymentStatusSerializerTest**: Tests payment status serialization
- **CreditCardInvoiceSerializerTest**: Tests invoice serialization
- **FinancialSummarySerializerTest**: Tests financial summary data serialization
- **DashboardSerializerTest**: Tests dashboard data serialization
- **FilterSerializerTest**: Tests filter serializers for search functionality
- **APIResponseSerializerTest**: Tests API response serialization

### Views (test_views.py)
- **UserFinancialProfileViewSetTest**: Tests CRUD operations and current profile action
- **CreditCardViewSetTest**: Tests credit card management, payments, and active cards
- **ExchangeRateViewSetTest**: Tests exchange rate management and latest rates
- **FixedPaymentViewSetTest**: Tests fixed payment management and filtering
- **VariablePaymentViewSetTest**: Tests variable payment management, filtering, and statistics
- **PaymentStatusViewSetTest**: Tests payment status tracking and filtering
- **CreditCardInvoiceViewSetTest**: Tests invoice management and closing
- **DashboardViewSetTest**: Tests dashboard summary and monthly reports
- **APIRootViewSetTest**: Tests API root endpoint
- **AuthenticationTest**: Tests authentication and authorization

### Factories (test_factories.py)
- **UserFinancialProfileFactoryTest**: Tests user profile factory creation
- **CreditCardFactoryTest**: Tests credit card factory with specialized variants
- **ExchangeRateFactoryTest**: Tests exchange rate factory with realistic rates
- **FixedPaymentFactoryTest**: Tests fixed payment factory with specialized types
- **VariablePaymentFactoryTest**: Tests variable payment factory with category-specific variants
- **CreditCardInvoiceFactoryTest**: Tests invoice factory with open/closed variants
- **PaymentStatusFactoryTest**: Tests payment status factory with different payment types
- **FactoryIntegrationTest**: Tests factory relationships and data consistency

### Integration (test_integration.py)
- **FinancialSystemIntegrationTest**: Tests complete financial workflows
- **PerformanceIntegrationTest**: Tests performance with large datasets
- **ErrorHandlingIntegrationTest**: Tests error handling and edge cases
- **DataIntegrityIntegrationTest**: Tests data integrity and constraints

## Running Tests

### Using Django's test runner
```bash
# Run all tests
python manage.py test finance

# Run specific test file
python manage.py test finance.tests.test_models

# Run specific test class
python manage.py test finance.tests.test_models.UserFinancialProfileModelTest

# Run specific test method
python manage.py test finance.tests.test_models.UserFinancialProfileModelTest.test_create_user_financial_profile
```

### Using the test runner script
```bash
# Run all tests with coverage
python finance/tests/run_tests.py

# Run specific test suite
python finance/tests/run_tests.py --suite models
python finance/tests/run_tests.py --suite views
python finance/tests/run_tests.py --suite integration

# Run performance tests
python finance/tests/run_tests.py --performance

# Run unit tests only
python finance/tests/run_tests.py --unit

# Run without coverage
python finance/tests/run_tests.py --no-coverage

# Verbose output
python finance/tests/run_tests.py --verbose
```

### Using pytest (if installed)
```bash
# Install pytest
pip install pytest pytest-django

# Run all tests
pytest finance/tests/

# Run with coverage
pytest --cov=finance finance/tests/
```

## Test Configuration

The test suite uses the `test_config.py` file for:
- **TestConfig**: Constants and configuration values
- **BaseTestCase**: Common setup and utility methods
- **TestDataGenerator**: Utilities for creating test scenarios
- **TestAssertions**: Custom assertions for financial data validation

## Factory Usage

The test suite heavily uses the factories from `factories.py`:

```python
# Create a single instance
profile = UserFinancialProfileFactory()

# Create multiple instances
cards = CreditCardFactory.create_batch(5)

# Create specialized instances
brazilian_card = BrazilianCreditCardFactory()
portuguese_card = PortugueseCreditCardFactory()
food_expense = FoodExpenseFactory()
transport_expense = TransportExpenseFactory()
```

## Test Data

The test suite creates realistic financial data including:
- User financial profiles with different currencies
- Credit cards from Brazil and Portugal with appropriate fees
- Exchange rates with realistic values
- Fixed payments (university fees, rent, etc.)
- Variable payments across different categories
- Credit card invoices with billing periods
- Payment status tracking with various states

## Coverage Areas

### Model Coverage
- ✅ All model fields and properties
- ✅ Model methods and calculated fields
- ✅ Unique constraints and validation
- ✅ String representations
- ✅ Model relationships

### Serializer Coverage
- ✅ Serialization and deserialization
- ✅ Field validation
- ✅ Nested serialization
- ✅ Read-only fields
- ✅ Custom methods

### View Coverage
- ✅ CRUD operations
- ✅ Custom actions
- ✅ Filtering and search
- ✅ Authentication and permissions
- ✅ Error handling

### Integration Coverage
- ✅ Complete workflows
- ✅ Cross-model relationships
- ✅ API endpoint integration
- ✅ Performance testing
- ✅ Error scenarios

## Performance Considerations

The test suite includes performance tests that:
- Test with large datasets (100+ records)
- Measure query performance
- Test complex aggregations
- Validate response times

## Error Handling

The test suite validates:
- Invalid data handling
- Missing required fields
- Duplicate data constraints
- Nonexistent resource handling
- Unauthorized access

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Fast execution (under 30 seconds for full suite)
- Isolated tests with proper cleanup
- Clear error messages
- Coverage reporting

## Contributing

When adding new tests:
1. Use the existing factory patterns
2. Follow the naming conventions
3. Add appropriate assertions
4. Include both positive and negative test cases
5. Update this README if adding new test categories 