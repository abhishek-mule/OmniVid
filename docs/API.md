# API Documentation

## Authentication

### Login

```http
POST /api/auth/login
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**

```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "accessToken": "jwt.token.here",
    "expiresIn": 3600
  }
}
```

### Logout

```http
POST /api/auth/logout
```

**Response**

```json
{
  "success": true
}
```

## User

### Get Current User

```http
GET /api/user/me
```

**Headers**
```
Authorization: Bearer <access_token>
```

**Response**

```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "https://example.com/avatar.jpg"
}
```

## Projects

### List Projects

```http
GET /api/projects
```

**Query Parameters**
- `limit`: Number of projects to return (default: 10)
- `offset`: Number of projects to skip (default: 0)
- `status`: Filter by status (e.g., `active`, `archived`)

**Response**

```json
{
  "projects": [
    {
      "id": "proj_123",
      "name": "My Project",
      "description": "Project description",
      "status": "active",
      "createdAt": "2023-01-01T00:00:00Z",
      "updatedAt": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### Create Project

```http
POST /api/projects
```

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "New Project",
  "description": "Project description"
}
```

**Response**

```json
{
  "id": "proj_123",
  "name": "New Project",
  "description": "Project description",
  "status": "active",
  "createdAt": "2023-01-01T00:00:00Z",
  "updatedAt": "2023-01-01T00:00:00Z"
}
```

## Error Handling

All API errors follow the same format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | The request is missing required parameters |
| `unauthorized` | 401 | Authentication failed or user not logged in |
| `forbidden` | 403 | User doesn't have permission to access the resource |
| `not_found` | 404 | The requested resource doesn't exist |
| `conflict` | 409 | Resource already exists |
| `too_many_requests` | 429 | Too many requests, try again later |
| `internal_server_error` | 500 | Internal server error |

## Rate Limiting

- **Unauthenticated**: 100 requests per hour
- **Authenticated**: 1,000 requests per hour

## Pagination

All list endpoints support pagination using `limit` and `offset` parameters.

**Example**
```
GET /api/projects?limit=10&offset=20
```

## Sorting

Most list endpoints support sorting using the `sort` parameter.

**Example**
```
GET /api/projects?sort=-createdAt,name
```

## Filtering

Most list endpoints support filtering using query parameters.

**Example**
```
GET /api/projects?status=active&createdAfter=2023-01-01
```
