"""
Async serializer mixins and classes for flexible field handling.
"""
from typing import Optional

from adrf_flex_fields import (
    EXPAND_PARAM,
    FIELDS_PARAM,
    OMIT_PARAM,
)


class FlexFieldsSerializerMixin:
    """
    A mixin that adds flexible field handling to ADRF serializers.

    Provides support for:
    - Dynamic field expansion via 'expand' parameter
    - Sparse fields via 'fields' and 'omit' parameters
    - Deep nested expansion with dot notation
    - Lazy serializer references
    - Configurable expansion depth and recursion control
    """

    expandable_fields = {}
    maximum_expansion_depth: Optional[int] = None
    recursive_expansion_permitted: Optional[bool] = None

    def __init__(self, *args, **kwargs):
        """
        Initialize the mixin and extract flex field options.

        Extracts expand, fields, and omit parameters from kwargs and stores them
        for later application. Also maintains parent reference for nested serializers.
        """
        # Extract flex field options from kwargs
        expand = list(kwargs.pop(EXPAND_PARAM, []))
        fields = list(kwargs.pop(FIELDS_PARAM, []))
        omit = list(kwargs.pop(OMIT_PARAM, []))
        parent = kwargs.pop("parent", None)

        # Call parent __init__
        super().__init__(*args, **kwargs)

        # Store parent reference and initialize state
        self.parent = parent
        self.expanded_fields = []
        self._flex_fields_rep_applied = False

        # Store flex options for different application phases
        # _flex_options_base: options passed directly to serializer constructor
        self._flex_options_base = {
            "expand": expand,
            "fields": fields,
            "omit": omit,
        }

        # _flex_options_rep_only: options from query params (applied in to_representation)
        self._flex_options_rep_only = {
            "expand": (
                self._get_permitted_expands_from_query_param(EXPAND_PARAM)
                if not expand
                else []
            ),
            "fields": (
                self._get_query_param_value(FIELDS_PARAM) if not fields else []
            ),
            "omit": (
                self._get_query_param_value(OMIT_PARAM) if not omit else []
            ),
        }

        # _flex_options_all: combined options from both sources
        self._flex_options_all = {
            "expand": self._flex_options_base["expand"]
            + self._flex_options_rep_only["expand"],
            "fields": self._flex_options_base["fields"]
            + self._flex_options_rep_only["fields"],
            "omit": self._flex_options_base["omit"]
            + self._flex_options_rep_only["omit"],
        }

    def _get_query_param_value(self, field: str):
        """
        Get query parameter values from request.

        Only allowed to examine query params if it's the root serializer.
        Returns empty list if not root or no request in context.
        """
        # Placeholder - will be implemented in task 10
        return []

    def _get_permitted_expands_from_query_param(self, expand_param: str):
        """
        Get permitted expand values from query params.

        Filters expand values by permitted_expands from context if present.
        """
        # Placeholder - will be implemented in task 10
        return []


    def get_fields(self):
        """
        Override to apply flex fields during field construction.

        Called by DRF/ADRF during serializer initialization to get the fields dict.
        We apply flex field transformations here for options passed directly to
        the serializer constructor.
        """
        fields = super().get_fields()
        self.apply_flex_fields(fields, self._flex_options_base)
        return fields

    def apply_flex_fields(self, fields, flex_options):
        """
        Apply flex field transformations (expand, fields, omit).

        This is the core method that modifies the fields dict based on the
        flex options. It handles field removal (omit/sparse) and field expansion.

        Args:
            fields: The fields dict to modify
            flex_options: Dict with 'expand', 'fields', and 'omit' keys

        Returns:
            The modified fields dict
        """
        from adrf_flex_fields.utils import split_levels

        # Split field paths by level for nested handling
        expand_fields, next_expand_fields = split_levels(flex_options["expand"])
        sparse_fields, next_sparse_fields = split_levels(flex_options["fields"])
        omit_fields, next_omit_fields = split_levels(flex_options["omit"])

        # Remove fields based on omit and sparse fields rules
        for field_name in self._get_fields_names_to_remove(
            fields, omit_fields, sparse_fields, next_omit_fields
        ):
            fields.pop(field_name)

        # Expand fields
        for name in self._get_expanded_field_names(
            expand_fields, omit_fields, sparse_fields, next_omit_fields
        ):
            self.expanded_fields.append(name)

            fields[name] = self._make_expanded_field_serializer(
                name, next_expand_fields, next_sparse_fields, next_omit_fields
            )

        return fields


    async def ato_representation(self, instance):
        """
        Override ADRF's async to_representation to apply flex fields.

        This is called during serialization to convert the instance to a dict.
        We apply flex field transformations here for options from query parameters,
        which allows us to support expand/fields/omit on non-GET requests.

        Args:
            instance: The model instance or data to serialize

        Returns:
            The serialized representation as a dict
        """
        # Apply flex fields from query params if not already applied
        if not self._flex_fields_rep_applied:
            self.apply_flex_fields(self.fields, self._flex_options_rep_only)
            self._flex_fields_rep_applied = True

        # Call parent's async to_representation
        return await super().ato_representation(instance)


    def _get_fields_names_to_remove(
        self,
        current_fields,
        omit_fields,
        sparse_fields,
        next_level_omits,
    ):
        """
        Determine which fields should be removed based on omit and fields parameters.

        Args:
            current_fields: Dict of current fields
            omit_fields: List of fields to omit
            sparse_fields: List of fields to include (if specified, all others excluded)
            next_level_omits: Dict mapping field names to nested omits

        Returns:
            List of field names to remove
        """
        sparse = len(sparse_fields) > 0
        to_remove = []

        if not sparse and len(omit_fields) == 0:
            return to_remove

        for field_name in current_fields:
            should_exist = self._should_field_exist(
                field_name, omit_fields, sparse_fields, next_level_omits
            )

            if not should_exist:
                to_remove.append(field_name)

        return to_remove

    def _should_field_exist(
        self,
        field_name,
        omit_fields,
        sparse_fields,
        next_level_omits,
    ):
        """
        Determine if a field should exist based on omit and fields parameters.

        Next level omits take form of:
        {
            'this_level_field': [field_to_omit_at_next_level]
        }
        We don't want to prematurely omit a field, eg "omit=house.rooms.kitchen"
        should not omit the entire house or all the rooms, just the kitchen.

        Args:
            field_name: Name of the field to check
            omit_fields: List of fields to omit at this level
            sparse_fields: List of fields to include at this level
            next_level_omits: Dict of nested omits

        Returns:
            True if field should exist, False otherwise
        """
        # If field is in omit list and not needed for nested omits, remove it
        if field_name in omit_fields and field_name not in next_level_omits:
            return False
        # If wildcard in sparse fields, include all
        elif self._contains_wildcard_value(sparse_fields):
            return True
        # If sparse fields specified and field not in list, remove it
        elif len(sparse_fields) > 0 and field_name not in sparse_fields:
            return False
        else:
            return True

    def _contains_wildcard_value(self, values):
        """
        Check if any wildcard values are present in the list.

        Args:
            values: List of field names to check

        Returns:
            True if wildcard value found, False otherwise
        """
        from adrf_flex_fields import WILDCARD_VALUES

        if WILDCARD_VALUES is None:
            return False

        intersecting_values = list(set(values) & set(WILDCARD_VALUES))
        return len(intersecting_values) > 0


    def _get_expanded_field_names(
        self,
        expand_fields,
        omit_fields,
        sparse_fields,
        next_level_omits,
    ):
        """
        Get list of field names that should be expanded.

        Args:
            expand_fields: List of fields to expand
            omit_fields: List of fields to omit
            sparse_fields: List of fields to include
            next_level_omits: Dict of nested omits

        Returns:
            List of field names to expand
        """
        if len(expand_fields) == 0:
            return []

        # Handle wildcard expansion
        if self._contains_wildcard_value(expand_fields):
            expand_fields = list(self._expandable_fields.keys())

        accum = []

        for name in expand_fields:
            # Skip if not in expandable_fields
            if name not in self._expandable_fields:
                continue

            # Skip if field should not exist based on omit/sparse rules
            if not self._should_field_exist(
                name, omit_fields, sparse_fields, next_level_omits
            ):
                continue

            accum.append(name)

        return accum

    @property
    def _expandable_fields(self):
        """
        Get expandable fields from Meta class or class attribute.

        It's more consistent with DRF to declare the expandable fields
        on the Meta class, however we need to support both places
        for legacy reasons.
        """
        if hasattr(self, "Meta") and hasattr(self.Meta, "expandable_fields"):
            return self.Meta.expandable_fields

        return self.expandable_fields

    def _make_expanded_field_serializer(
        self, name, nested_expand, nested_fields, nested_omit
    ):
        """
        Create an instance of the expanded field serializer.

        Args:
            name: Name of the field to expand
            nested_expand: Dict of nested expand options
            nested_fields: Dict of nested fields options
            nested_omit: Dict of nested omit options

        Returns:
            Instance of the expanded serializer
        """
        import copy
        from rest_framework import serializers

        field_options = self._expandable_fields[name]

        # Parse field options (can be class, tuple, or string)
        if isinstance(field_options, tuple):
            serializer_class = field_options[0]
            settings = copy.deepcopy(field_options[1]) if len(field_options) > 1 else {}
        else:
            serializer_class = field_options
            settings = {}

        # Handle lazy string references
        if isinstance(serializer_class, str):
            serializer_class = self._get_serializer_class_from_lazy_string(
                serializer_class
            )

        # Pass context to all serializers
        if issubclass(serializer_class, serializers.Serializer):
            settings["context"] = self.context

        # Pass flex options to FlexFields serializers
        if issubclass(serializer_class, FlexFieldsSerializerMixin):
            settings["parent"] = self

            if name in nested_expand:
                settings[EXPAND_PARAM] = nested_expand[name]

            if name in nested_fields:
                settings[FIELDS_PARAM] = nested_fields[name]

            if name in nested_omit:
                settings[OMIT_PARAM] = nested_omit[name]

        return serializer_class(**settings)

    def _get_serializer_class_from_lazy_string(self, full_lazy_path: str):
        """
        Import serializer class from lazy string reference.

        Supports both full import paths and shortcut paths.
        Example: 'myapp.serializers.UserSerializer' or 'myapp.UserSerializer'

        Args:
            full_lazy_path: String path to serializer class

        Returns:
            The serializer class

        Raises:
            Exception: If serializer cannot be imported
        """
        path_parts = full_lazy_path.split(".")
        class_name = path_parts.pop()
        path = ".".join(path_parts)

        # Try full path first
        serializer_class, error = self._import_serializer_class(path, class_name)

        # If failed and path doesn't end with .serializers, try adding it
        if error and not path.endswith(".serializers"):
            serializer_class, error = self._import_serializer_class(
                path + ".serializers", class_name
            )

        if serializer_class:
            return serializer_class

        raise Exception(error)

    def _import_serializer_class(self, path: str, class_name: str):
        """
        Helper to import a serializer class from a module path.

        Args:
            path: Module path (e.g., 'myapp.serializers')
            class_name: Name of the class to import

        Returns:
            Tuple of (class, error_message) - one will be None
        """
        import importlib

        try:
            module = importlib.import_module(path)
        except ImportError:
            return (
                None,
                f"No module found at path: {path} when trying to import {class_name}",
            )

        try:
            return getattr(module, class_name), None
        except AttributeError:
            return None, f"No class {class_name} found in module {path}"



    def get_maximum_expansion_depth(self) -> Optional[int]:
        """
        Get maximum expansion depth from serializer or settings.

        Returns:
            Maximum expansion depth or None for unlimited
        """
        from adrf_flex_fields import MAXIMUM_EXPANSION_DEPTH
        return self.maximum_expansion_depth or MAXIMUM_EXPANSION_DEPTH

    def get_recursive_expansion_permitted(self) -> bool:
        """
        Get whether recursive expansion is permitted from serializer or settings.

        Returns:
            True if recursive expansion is permitted, False otherwise
        """
        from adrf_flex_fields import RECURSIVE_EXPANSION_PERMITTED

        if self.recursive_expansion_permitted is not None:
            return self.recursive_expansion_permitted
        else:
            return RECURSIVE_EXPANSION_PERMITTED

    def _split_expand_field(self, expand_path: str):
        """Split expand path by dots."""
        return expand_path.split(".")

    def recursive_expansion_not_permitted(self):
        """
        Raise exception when recursive expansion is found.

        Can be overridden for custom exception handling.
        """
        from rest_framework import serializers
        raise serializers.ValidationError(
            detail="Recursive expansion not permitted"
        )

    def expansion_depth_exceeded(self):
        """
        Raise exception when expansion depth is exceeded.

        Can be overridden for custom exception handling.
        """
        from rest_framework import serializers
        raise serializers.ValidationError(detail="Expansion depth exceeded")

    def _validate_recursive_expansion(self, expand_path: str) -> None:
        """
        Validate that expansion path doesn't contain recursive references.

        Args:
            expand_path: Dot-separated expansion path

        Raises:
            ValidationError: If recursive expansion detected
        """
        if not self.get_recursive_expansion_permitted():
            expansion_path = self._split_expand_field(expand_path)
            expansion_length = len(expansion_path)
            expansion_length_unique = len(set(expansion_path))

            if expansion_length != expansion_length_unique:
                self.recursive_expansion_not_permitted()

    def _validate_expansion_depth(self, expand_path: str) -> None:
        """
        Validate that expansion path doesn't exceed maximum depth.

        Args:
            expand_path: Dot-separated expansion path

        Raises:
            ValidationError: If depth exceeded
        """
        maximum_expansion_depth = self.get_maximum_expansion_depth()
        if maximum_expansion_depth is None:
            return

        expansion_path = self._split_expand_field(expand_path)
        if len(expansion_path) > maximum_expansion_depth:
            self.expansion_depth_exceeded()

    def _get_query_param_value(self, field: str):
        """
        Get query parameter values from request.

        Only allowed to examine query params if it's the root serializer.
        Returns empty list if not root or no request in context.

        Args:
            field: Name of the query parameter

        Returns:
            List of values from query parameter
        """
        # Only root serializer can access query params
        if self.parent:
            return []

        if not hasattr(self, "context") or not self.context.get("request"):
            return []

        # Try to get values from query params
        values = self.context["request"].query_params.getlist(field)

        # Support array format (e.g., ?expand[]=country)
        if not values:
            values = self.context["request"].query_params.getlist(f"{field}[]")

        # Handle comma-separated format (e.g., ?expand=country,friends)
        if values and len(values) == 1:
            values = values[0].split(",")

        # Validate expand paths
        for expand_path in values:
            self._validate_recursive_expansion(expand_path)
            self._validate_expansion_depth(expand_path)

        return values or []

    def _get_permitted_expands_from_query_param(self, expand_param: str):
        """
        Get permitted expand values from query params.

        Filters expand values by permitted_expands from context if present.
        This is used by ViewSets to restrict expansions on list views.

        Args:
            expand_param: Name of the expand parameter

        Returns:
            List of permitted expand values
        """
        expand = self._get_query_param_value(expand_param)

        if "permitted_expands" in self.context:
            permitted_expands = self.context["permitted_expands"]

            if self._contains_wildcard_value(expand):
                return permitted_expands
            else:
                return list(set(expand) & set(permitted_expands))

        return expand


# FlexFieldsModelSerializer combining mixin with ADRF ModelSerializer
from adrf.serializers import ModelSerializer


class FlexFieldsModelSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    """
    ADRF ModelSerializer with flexible field handling.

    Combines FlexFieldsSerializerMixin with ADRF's async ModelSerializer
    to provide full async support with dynamic field expansion and sparse fields.
    """
    pass
