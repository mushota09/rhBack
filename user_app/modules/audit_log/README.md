# Audit Log API Documentation

## Overview

The AuditLogViewSet provides comprehensive querying capabilities for audit logs with advanced filtering and search functionality. This implementation satisfies Requirements 7.3 and 7.5 for audit history display and querying.

## Features

- **Permission-based Access Control**: Only superusers can access audit logs
- **Advanced Filtering**: Filter by user, action, resource type, date ranges, and IP addresses
- **Text Search**: Search across user details, actions, and resource information
- **Flexible Ordering**: Order by timestamp, action, resource type, and user details
- **Field Selection**: Use ADRF flex_fields for selective field inclusion/expansion

## API Endpoints

### List Audit Logs
```
GET /api/user_app/audit_log/
```

### Retrieve Specific Audit Log
```
GET /api/user_app/audit_log/{id}/
```

## Filtering Options

### Basic Filters
- `user_id`: Filter by exact user ID
- `action`: Filter by exact action (CREATE, UPDATE, DELETE, etc.)
- `type_ressource`: Filter by resource type (exact match)
- `adresse_ip`: Filter by exact IP address

### Advanced Filters
- `timestamp_after`: Filter logs after specific timestamp (ISO format)
- `timestamp_before`: Filter logs before specific timestamp (ISO format)
- `date_after`: Filter logs after specific date (YYYY-MM-DD)
- `date_before`: Filter logs before specific date (YYYY-MM-DD)
- `type_ressource__icontains`: Case-insensitive partial match for resource type
- `user_email`: Case-insensitive partial match for user email
- `user_name`: Search across user's nom and prenom fields

### Multiple Action Filtering
```
GET /api/user_app/audit_log/?action=CREATE&action=UPDATE
```

## Search Functionality

Use the `search` parameter to search across multiple fields:
```
GET /api/user_app/audit_log/?search=john
```

Search fields include:
- User email, nom, prenom
- Action
- Resource type
- Resource ID
- IP address
- User agent

## Ordering

Use the `ordering` parameter:
```
GET /api/user_app/audit_log/?ordering=-timestamp
GET /api/user_app/audit_log/?ordering=action,type_ressource
```

Available ordering fields:
- `timestamp`
- `action`
- `type_ressource`
- `user_id__email`
- `user_id__nom`

## Field Selection and Expansion

### Select Specific Fields
```
GET /api/user_app/audit_log/?fields=id,action,timestamp,user_id
```

### Expand Related Fields
```
GET /api/user_app/audit_log/?expand=user_id
```

## Example Queries

### Filter by Date Range
```
GET /api/user_app/audit_log/?date_after=2024-01-01&date_before=2024-01-31
```

### Filter by User and Action
```
GET /api/user_app/audit_log/?user_id=123&action=CREATE
```

### Search for Specific User
```
GET /api/user_app/audit_log/?search=john.doe@example.com
```

### Complex Query with Multiple Filters
```
GET /api/user_app/audit_log/?action=UPDATE&action=DELETE&type_ressource__icontains=group&date_after=2024-01-01&ordering=-timestamp&expand=user_id
```

## Response Format

```json
{
  "count": 150,
  "next": "http://api/user_app/audit_log/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_id": 123,
      "action": "CREATE",
      "action_display": "Créer",
      "type_ressource": "user_group",
      "id_ressource": "456",
      "anciennes_valeurs": null,
      "nouvelles_valeurs": {"status": "active"},
      "adresse_ip": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Permissions

- **CanViewAuditLogs**: Only superusers can access audit log endpoints
- All other users receive HTTP 403 Forbidden
- Unauthenticated users receive HTTP 401 Unauthorized

## Implementation Details

- Uses Django Filter for advanced filtering capabilities
- Implements custom filter methods for complex queries
- Optimizes database queries with `select_related('user_id')`
- Follows ADRF patterns for async compatibility
- Maintains backward compatibility with existing URL configuration
