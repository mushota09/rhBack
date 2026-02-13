"""
ViewSet mixins for flexible field handling.
"""


class FlexFieldsMixin:
    """
    Mixin for ViewSets to control field expansions.

    Provides control over which fields can be expanded in list views
    via the permit_list_expands attribute.
    """

    permit_list_expands = []

    def get_serializer_context(self):
        """
        Add permitted expansions to context for list views.

        When the action is "list", adds permitted_expands to the serializer
        context to restrict which fields can be expanded.
        """
        context = super().get_serializer_context()

        if hasattr(self, "action") and self.action == "list":
            context["permitted_expands"] = self.permit_list_expands

        return context


class SerializerMethodMixin:
    """
    Mixin to support different serializers for read and write operations.

    Allows using:
    - serializer_class_read for GET/HEAD operations
    - serializer_class_write for POST/PUT/PATCH/DELETE operations
    """

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on request method.

        Returns:
            Serializer class for read operations (GET/HEAD) or write operations
        """
        if (hasattr(self, 'serializer_class_read') and
            hasattr(self, 'serializer_class_write')):

            if self.request.method in ['GET', 'HEAD']:
                return self.serializer_class_read
            return self.serializer_class_write

        return super().get_serializer_class()


# Import ModelViewSet only when needed to avoid circular imports
try:
    from adrf.viewsets import ModelViewSet
    class FlexFieldsModelViewSet(
        ModelViewSet,
        FlexFieldsMixin,
        SerializerMethodMixin
    ):
        """
        ADRF ModelViewSet with flexible field handling and serializer management.

        Combines:
        - ViewSetMixin: for DRF router compatibility (get_extra_actions)
        - ADRF ModelViewSet: for full async support
        - FlexFieldsMixin: for controlled field expansion
        - SerializerMethodMixin: for read/write serializer separation

        Usage:
            class MyAPIView(FlexFieldsModelViewSet):
                queryset = MyModel.objects.all()
                serializer_class_read = MyReadSerializer
                serializer_class_write = MyWriteSerializer
                permit_list_expands = ["field1", "field2.nested"]
        """
        pass

except ImportError:
    # Fallback if adrf is not available
    class FlexFieldsModelViewSet(FlexFieldsMixin, SerializerMethodMixin):
        """
        Fallback FlexFieldsModelViewSet when ADRF is not available.
        """
        pass
