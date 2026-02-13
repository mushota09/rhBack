"""
Filter backends for query optimization and documentation.
"""
from functools import lru_cache
from typing import Optional

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import QuerySet
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from adrf_flex_fields import (
    FIELDS_PARAM,
    EXPAND_PARAM,
    OMIT_PARAM,
    WILDCARD_VALUES
)
from adrf_flex_fields.serializers import (
    FlexFieldsModelSerializer,
    FlexFieldsSerializerMixin,
)

WILDCARD_VALUES_JOINED = ",".join(WILDCARD_VALUES) if WILDCARD_VALUES else ""


class FlexFieldsDocsFilterBackend(BaseFilterBackend):
    """
    Filter backend for schema/documentation generation.

    Generates OpenAPI and CoreAPI schema parameters for flex fields.
    Does not modify the queryset.
    """

    def filter_queryset(self, request, queryset, view):
        """Pass-through - doesn't modify queryset."""
        return queryset

    @staticmethod
    @lru_cache()
    def _get_field(field_name: str, model: models.Model) -> Optional[models.Field]:
        """Get field from model by name."""
        try:
            return model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return None

    @staticmethod
    def _get_expandable_fields(serializer_class: FlexFieldsModelSerializer) -> list:
        """
        Get list of expandable fields including nested ones.

        Recursively collects expandable fields with dot notation for nested fields.
        """
        if not hasattr(serializer_class, 'Meta'):
            return []

        expandable_fields = list(
            getattr(serializer_class.Meta, 'expandable_fields', {}).items()
        )
        expand_list = []

        while expandable_fields:
            key, cls = expandable_fields.pop()
            cls = cls[0] if hasattr(cls, '__iter__') and not isinstance(cls, str) else cls

            expand_list.append(key)

            if hasattr(cls, "Meta") and issubclass(cls, FlexFieldsSerializerMixin):
                if hasattr(cls.Meta, "expandable_fields"):
                    next_layer = getattr(cls.Meta, 'expandable_fields')
                    expandable_fields.extend([
                        (f"{key}.{k}", v) for k, v in list(next_layer.items())
                    ])

        return expand_list

    @staticmethod
    def _get_fields(serializer_class):
        """Get comma-separated list of fields from serializer."""
        if not hasattr(serializer_class, 'Meta'):
            return ""
        fields = getattr(serializer_class.Meta, "fields", [])
        return ",".join(fields) if fields else ""

    def get_schema_fields(self, view):
        """Generate CoreAPI schema fields."""
        assert coreapi is not None, \
            "coreapi must be installed to use `get_schema_fields()`"
        assert coreschema is not None, \
            "coreschema must be installed to use `get_schema_fields()`"

        serializer_class = view.get_serializer_class()
        if not issubclass(serializer_class, FlexFieldsSerializerMixin):
            return []

        fields = self._get_fields(serializer_class)
        expandable_fields_joined = ",".join(
            self._get_expandable_fields(serializer_class)
        )

        return [
            coreapi.Field(
                name=FIELDS_PARAM,
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Selected fields",
                    description="Specify required fields by comma",
                ),
                example=(fields or "field1,field2,nested.field") +
                        ("," + WILDCARD_VALUES_JOINED if WILDCARD_VALUES_JOINED else ""),
            ),
            coreapi.Field(
                name=OMIT_PARAM,
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Omitted fields",
                    description="Specify omitted fields by comma",
                ),
                example=(fields or "field1,field2,nested.field") +
                        ("," + WILDCARD_VALUES_JOINED if WILDCARD_VALUES_JOINED else ""),
            ),
            coreapi.Field(
                name=EXPAND_PARAM,
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Expanded fields",
                    description="Specify expanded fields by comma",
                ),
                example=(expandable_fields_joined or "field1,field2,nested.field") +
                        ("," + WILDCARD_VALUES_JOINED if WILDCARD_VALUES_JOINED else ""),
            ),
        ]

    def get_schema_operation_parameters(self, view):
        """Generate OpenAPI 3.0 schema parameters."""
        serializer_class = view.get_serializer_class()
        if not issubclass(serializer_class, FlexFieldsSerializerMixin):
            return []

        fields = self._get_fields(serializer_class)
        expandable_fields = self._get_expandable_fields(serializer_class)
        if WILDCARD_VALUES:
            expandable_fields.extend(WILDCARD_VALUES)

        parameters = [
            {
                "name": FIELDS_PARAM,
                "required": False,
                "in": "query",
                "description": "Specify required fields by comma",
                "schema": {
                    "title": "Selected fields",
                    "type": "string",
                },
                "example": (fields or "field1,field2,nested.field") +
                          ("," + WILDCARD_VALUES_JOINED if WILDCARD_VALUES_JOINED else ""),
            },
            {
                "name": OMIT_PARAM,
                "required": False,
                "in": "query",
                "description": "Specify omitted fields by comma",
                "schema": {
                    "title": "Omitted fields",
                    "type": "string",
                },
                "example": (fields or "field1,field2,nested.field") +
                          ("," + WILDCARD_VALUES_JOINED if WILDCARD_VALUES_JOINED else ""),
            },
            {
                "name": EXPAND_PARAM,
                "required": False,
                "in": "query",
                "description": "Select fields to expand",
                "style": "form",
                "explode": False,
                "schema": {
                    "title": "Expanded fields",
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": expandable_fields
                    }
                },
            },
        ]

        return parameters


class FlexFieldsFilterBackend(FlexFieldsDocsFilterBackend):
    """
    Filter backend for automatic query optimization.

    Analyzes requested fields and applies select_related/prefetch_related
    and only() to optimize database queries.
    """

    def filter_queryset(
        self, request: Request, queryset: QuerySet, view
    ):
        """
        Optimize queryset based on requested fields.

        Args:
            request: The request object
            queryset: The queryset to optimize
            view: The view being accessed

        Returns:
            Optimized queryset
        """
        if (
            not issubclass(view.get_serializer_class(), FlexFieldsSerializerMixin)
            or request.method != "GET"
        ):
            return queryset

        auto_remove_fields_from_query = getattr(
            view, "auto_remove_fields_from_query", True
        )
        auto_select_related_on_query = getattr(
            view, "auto_select_related_on_query", True
        )
        required_query_fields = list(getattr(view, "required_query_fields", []))

        # Create serializer and apply flex fields to analyze what's needed
        serializer = view.get_serializer(
            context=view.get_serializer_context()
        )

        serializer.apply_flex_fields(
            serializer.fields, serializer._flex_options_rep_only
        )
        serializer._flex_fields_rep_applied = True

        # Analyze fields to determine model fields and nested fields
        model_fields = []
        nested_model_fields = []

        for field in serializer.fields.values():
            model_field = self._get_field(field.source, queryset.model)
            if model_field:
                model_fields.append(model_field)
                # Check if field is expanded or is a relation
                if (field.field_name in serializer.expanded_fields or
                    (model_field.is_relation and not model_field.many_to_one) or
                    (model_field.is_relation and model_field.many_to_one and
                     not model_field.concrete)):
                    nested_model_fields.append(model_field)

        # Apply only() for sparse fields
        if auto_remove_fields_from_query:
            only_fields = required_query_fields + [
                model_field.name
                for model_field in model_fields
                if (not model_field.is_relation or
                    (model_field.many_to_one and model_field.concrete))
            ]
            queryset = queryset.only(*only_fields)

        # Apply select_related and prefetch_related
        if auto_select_related_on_query and nested_model_fields:
            # select_related for ForeignKey
            select_related_fields = [
                model_field.name
                for model_field in nested_model_fields
                if (model_field.is_relation and
                    model_field.many_to_one and
                    model_field.concrete)
            ]
            if select_related_fields:
                queryset = queryset.select_related(*select_related_fields)

            # prefetch_related for ManyToMany and reverse ForeignKey
            prefetch_fields = [
                model_field.name
                for model_field in nested_model_fields
                if ((model_field.is_relation and not model_field.many_to_one) or
                    (model_field.is_relation and model_field.many_to_one and
                     not model_field.concrete))
            ]
            if prefetch_fields:
                queryset = queryset.prefetch_related(*prefetch_fields)

        return queryset

    @staticmethod
    @lru_cache()
    def _get_field(field_name: str, model: models.Model) -> Optional[models.Field]:
        """Get field from model by name."""
        try:
            return model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return None

