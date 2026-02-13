"""
Utility functions for flexible field handling.
"""
from typing import Dict, List, Tuple


def split_levels(fields: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Sépare les champs par niveau pour l'expansion imbriquée.

    Parse dot-notation field paths and split them into current level fields
    and next level mappings for nested expansion.

    Args:
        fields: Liste de champs avec notation par points (e.g., ['country', 'country.states'])

    Returns:
        Tuple de (champs de niveau actuel, dict des champs de niveau suivant)

    Example:
        >>> split_levels(['country', 'country.states', 'friends.hobbies'])
        (['country', 'friends'], {'country': ['states'], 'friends': ['hobbies']})
    """
    if not fields:
        return [], {}

    current_level = []
    next_level = {}

    for field in fields:
        if not field:  # Skip empty strings
            continue

        parts = field.split('.', 1)
        current_level.append(parts[0])

        if len(parts) > 1:
            if parts[0] not in next_level:
                next_level[parts[0]] = []
            next_level[parts[0]].append(parts[1])

    # Remove duplicates while preserving order
    seen = set()
    current_level_unique = []
    for item in current_level:
        if item not in seen:
            seen.add(item)
            current_level_unique.append(item)

    return current_level_unique, next_level



def is_expanded(request, field: str) -> bool:
    """
    Vérifie si un champ a été étendu via les paramètres de requête.

    Check if a field has been expanded via the request's query parameters.
    Handles None request gracefully and supports both comma-separated and array formats.

    Args:
        request: The request object (can be None)
        field: The name of the field to check

    Returns:
        True if the field is in the expand parameter, False otherwise

    Example:
        >>> is_expanded(request, 'country')  # ?expand=country
        True
        >>> is_expanded(request, 'friends')  # ?expand=country
        False
        >>> is_expanded(None, 'country')
        False
    """
    from adrf_flex_fields import EXPAND_PARAM

    # Handle None request gracefully
    if not request or not hasattr(request, 'query_params'):
        return False

    # Try to get expand values from query params
    expand_values = request.query_params.getlist(EXPAND_PARAM)

    # Support array format (e.g., ?expand[]=country&expand[]=friends)
    if not expand_values:
        expand_values = request.query_params.getlist(f"{EXPAND_PARAM}[]")

    # Handle comma-separated format (e.g., ?expand=country,friends)
    if expand_values and len(expand_values) == 1:
        expand_values = expand_values[0].split(",")

    # Check if field is in the expand list
    return field in expand_values



def is_included(request, field: str) -> bool:
    """
    Vérifie si un champ n'a pas été exclu via omit ou fields.

    Check if a field has NOT been excluded via either the omit parameter
    or the fields parameter. Handles None request gracefully.

    Args:
        request: The request object (can be None)
        field: The name of the field to check

    Returns:
        True if the field is included (not omitted and in fields if specified),
        False otherwise

    Example:
        >>> is_included(request, 'name')  # ?fields=id,name
        True
        >>> is_included(request, 'password')  # ?omit=password
        False
        >>> is_included(None, 'name')
        True
    """
    from adrf_flex_fields import FIELDS_PARAM, OMIT_PARAM

    # Handle None request gracefully - default to included
    if not request or not hasattr(request, 'query_params'):
        return True

    # Check omit parameter
    omit_values = request.query_params.getlist(OMIT_PARAM)
    if not omit_values:
        omit_values = request.query_params.getlist(f"{OMIT_PARAM}[]")

    if omit_values and len(omit_values) == 1:
        omit_values = omit_values[0].split(",")

    # If field is in omit list, it's not included
    if field in omit_values:
        return False

    # Check fields parameter (sparse fields)
    fields_values = request.query_params.getlist(FIELDS_PARAM)
    if not fields_values:
        fields_values = request.query_params.getlist(f"{FIELDS_PARAM}[]")

    if fields_values and len(fields_values) == 1:
        fields_values = fields_values[0].split(",")

    # If fields parameter is specified and field is not in it, it's not included
    if fields_values and field not in fields_values:
        return False

    # Field is included
    return True
