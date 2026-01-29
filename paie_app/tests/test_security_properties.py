"""
Property-based tests for security and authentication in the payroll system.
Feature: paie-system, Property 38: API Security with JWT
Validates: Requirements 9.4
"""
import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from utilities.jwt_utils import create_access_token

User = get_user_model()


class SecurityPropertiesTest(TestCase):
    """Property-based tests for security and JWT authentication."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create(
            email="admin@test.com",
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.admin_user.set_password("testpass123")
        self.admin_user.save()

        self.regular_user = User.objects.create(
            email="user@test.com",
            is_active=True
        )
        self.regular_user.set_password("testpass123")
        self.regular_user.save()

    @given(endpoint_path=st.sampled_from(['/api/paie/periode-paie/']))
    @settings(max_examples=5, deadline=3000)
    def test_api_requires_authentication(self, endpoint_path):
        """
        Property 38: API Security with JWT
        For any API endpoint, the system should require valid JWT authentication.
        Validates: Requirements 9.4
        """
        response = self.client.get(endpoint_path)
        print(f"Response status: {response.status_code}, Content: {response.content}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @given(user_type=st.sampled_from(['admin', 'regular']))
    @settings(max_examples=5, deadline=3000)
    def test_valid_jwt_grants_access(self, user_type):
        """
        Property 38: API Security with JWT
        For any valid JWT token, the system should grant appropriate access.
        Validates: Requirements 9.4
        """
        user = self.admin_user if user_type == 'admin' else self.regular_user
        token = create_access_token(user.id)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/paie/periode-paie/')

        # Should not return 401 (authentication should succeed)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        self.client.credentials()

    def test_invalid_jwt_denies_access(self):
        """Test that invalid JWT tokens are rejected."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get('/api/paie/periode-paie/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        self.client.credentials()
