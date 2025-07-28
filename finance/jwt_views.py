from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json


@swagger_auto_schema(
    method='post',
    operation_description="Register a new user and return JWT tokens",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ),
    responses={
        201: openapi.Response(
            description='User created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                }
            )
        ),
        400: openapi.Response(description='Bad Request - Invalid data or user already exists'),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_register_view(request):
    """Register user and return JWT tokens."""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response(
            {'error': 'Username, email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'message': 'User created successfully'
    }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_description="Login user and return JWT tokens",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ),
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                }
            )
        ),
        400: openapi.Response(description='Bad Request - Missing credentials'),
        401: openapi.Response(description='Unauthorized - Invalid credentials'),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_login_view(request):
    """Login user and return JWT tokens."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_logout_view(request):
    """Logout user by blacklisting refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        else:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def jwt_user_info_view(request):
    """Get current user information from JWT token."""
    return Response({
        'user_id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'date_joined': request.user.date_joined,
        'is_active': request.user.is_active,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_refresh_view(request):
    """Refresh JWT access token using refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token),
        })
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_verify_view(request):
    """Verify JWT access token."""
    try:
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to decode the token
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        
        return Response({
            'valid': True,
            'user_id': access_token['user_id'],
            'exp': access_token['exp'],
        })
    except Exception as e:
        return Response(
            {'valid': False, 'error': 'Invalid token'},
            status=status.HTTP_401_UNAUTHORIZED
        ) 