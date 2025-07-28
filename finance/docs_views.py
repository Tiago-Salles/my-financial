from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .api_docs import get_api_documentation, get_endpoint_documentation, get_model_documentation


@api_view(['GET'])
@permission_classes([AllowAny])
def api_docs_view(request):
    """Return complete API documentation."""
    return Response(get_api_documentation())


@api_view(['GET'])
@permission_classes([AllowAny])
def endpoint_docs_view(request, endpoint_name):
    """Return documentation for a specific endpoint."""
    docs = get_endpoint_documentation(endpoint_name)
    if docs:
        return Response(docs)
    return Response(
        {'error': f'Endpoint {endpoint_name} not found'},
        status=404
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def model_docs_view(request, model_name):
    """Return documentation for a specific model."""
    docs = get_model_documentation(model_name)
    if docs:
        return Response(docs)
    return Response(
        {'error': f'Model {model_name} not found'},
        status=404
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def api_overview_view(request):
    """Return a simplified API overview."""
    docs = get_api_documentation()
    overview = {
        'title': docs['title'],
        'version': docs['version'],
        'description': docs['description'],
        'base_url': docs['base_url'],
        'authentication': docs['authentication'],
        'available_endpoints': list(docs['endpoints'].keys()),
        'available_models': list(docs['models'].keys()),
        'quick_start': {
            '1': 'Register a user: POST /api/auth/register/',
            '2': 'Login to get token: POST /api/auth/login/',
            '3': 'Create a profile: POST /api/profiles/',
            '4': 'Add credit cards: POST /api/credit-cards/',
            '5': 'Add payments: POST /api/variable-payments/',
            '6': 'View dashboard: GET /api/dashboard/summary/'
        }
    }
    return Response(overview) 