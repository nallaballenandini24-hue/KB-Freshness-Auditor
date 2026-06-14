# API Response Examples

## Dashboard Statistics
```json
{
  "total_articles": 1250,
  "fresh_articles": 420,
  "warning_articles": 580,
  "stale_articles": 250,
  "recent_audits_count": 5
}
```

## Audit Result
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "article_id": "550e8400-e29b-41d4-a716-446655440001",
  "freshness_score": 75.5,
  "status": "stale",
  "article_age_days": 180,
  "ticket_count": 45,
  "days_since_last_update": 120,
  "audit_date": "2024-01-15T10:30:00Z"
}
```

## AI Recommendation
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "article_id": "550e8400-e29b-41d4-a716-446655440001",
  "recommendation_type": "missing_info",
  "original_content": "Original article text...",
  "recommended_content": "Updated article with new information...",
  "confidence_score": 0.87,
  "accepted": false,
  "rejected": false,
  "created_at": "2024-01-15T10:35:00Z"
}
```

## Article Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "How to Reset Your Password",
  "description": "Step-by-step guide for password reset",
  "file_path": "articles/550e8400-e29b-41d4-a716-446655440001/guide.md",
  "file_name": "guide.md",
  "tags": "password, authentication, account",
  "created_at": "2023-07-15T10:00:00Z",
  "updated_at": "2023-12-10T14:25:00Z",
  "last_reviewed_at": "2024-01-10T09:00:00Z",
  "is_active": true
}
```

## Ticket Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "ticket_id": "TICK-12345",
  "article_id": "550e8400-e29b-41d4-a716-446655440001",
  "subject": "Cannot reset password",
  "description": "User unable to complete password reset",
  "category": "account-access",
  "resolved": true,
  "created_at": "2024-01-10T15:30:00Z",
  "resolved_at": "2024-01-12T10:00:00Z",
  "imported_at": "2024-01-13T09:00:00Z"
}
```

## Audit Job Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "workflow_id": "abc123def456",
  "status": "running",
  "total_articles": 1250,
  "processed_articles": 342,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```
