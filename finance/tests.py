"""
Finance app tests package.
This file is kept for backward compatibility.
All tests are now organized in the tests/ package.
"""

# Import all test modules for easy discovery
from .tests.test_models import *
from .tests.test_serializers import *
from .tests.test_views import *
from .tests.test_factories import *
from .tests.test_integration import *

# This allows running tests with: python manage.py test finance
# while maintaining the new organized structure
