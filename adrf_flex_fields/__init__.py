"""
ADRF-Flex-Fields - Flexible, dynamic fields for ADRF serializers.

Async adaptation of drf-flex-fields for Async Django REST Framework (ADRF).
"""

__version__ = "0.1.0"

# Configuration constants with defaults
EXPAND_PARAM = "expand"
FIELDS_PARAM = "fields"
OMIT_PARAM = "omit"
WILDCARD_VALUES = ["*", "~all"]
MAXIMUM_EXPANSION_DEPTH = None
RECURSIVE_EXPANSION_PERMITTED = True


def _load_settings():
    """Load configuration from Django settings if available."""
    global EXPAND_PARAM, FIELDS_PARAM, OMIT_PARAM, WILDCARD_VALUES
    global MAXIMUM_EXPANSION_DEPTH, RECURSIVE_EXPANSION_PERMITTED

    try:
        from django.conf import settings
        _user_settings = getattr(settings, "REST_FLEX_FIELDS", {})

        EXPAND_PARAM = _user_settings.get("EXPAND_PARAM", EXPAND_PARAM)
        FIELDS_PARAM = _user_settings.get("FIELDS_PARAM", FIELDS_PARAM)
        OMIT_PARAM = _user_settings.get("OMIT_PARAM", OMIT_PARAM)
        WILDCARD_VALUES = _user_settings.get("WILDCARD_VALUES", WILDCARD_VALUES)
        MAXIMUM_EXPANSION_DEPTH = _user_settings.get(
            "MAXIMUM_EXPANSION_DEPTH", MAXIMUM_EXPANSION_DEPTH
        )
        RECURSIVE_EXPANSION_PERMITTED = _user_settings.get(
            "RECURSIVE_EXPANSION_PERMITTED", RECURSIVE_EXPANSION_PERMITTED
        )
    except (ImportError, RuntimeError):
        # Django not available or not configured yet
        pass


# Load settings on import
_load_settings()

# Public API exports
from adrf_flex_fields.serializers import (
    FlexFieldsSerializerMixin,
    FlexFieldsModelSerializer,
)
from adrf_flex_fields.views import (
    FlexFieldsMixin,
    SerializerMethodMixin,
    FlexFieldsModelViewSet,
)
from adrf_flex_fields.filter_backends import (
    FlexFieldsFilterBackend,
    FlexFieldsDocsFilterBackend,
)
from adrf_flex_fields.utils import (
    is_expanded,
    is_included,
    split_levels,
)

__all__ = [
    # Version
    "__version__",
    # Configuration
    "EXPAND_PARAM",
    "FIELDS_PARAM",
    "OMIT_PARAM",
    "WILDCARD_VALUES",
    "MAXIMUM_EXPANSION_DEPTH",
    "RECURSIVE_EXPANSION_PERMITTED",
    # Serializers
    "FlexFieldsSerializerMixin",
    "FlexFieldsModelSerializer",
    # Views
    "FlexFieldsMixin",
    "SerializerMethodMixin",
    "FlexFieldsModelViewSet",
    # Filter Backends
    "FlexFieldsFilterBackend",
    "FlexFieldsDocsFilterBackend",
    # Utils
    "is_expanded",
    "is_included",
    "split_levels",
]
