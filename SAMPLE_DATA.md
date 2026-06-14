# Sample CSV Import Format

## tickets.csv

For importing support tickets, use the following CSV format:

```csv
ticket_id,subject,description,category,article_id,created_at,resolved,resolved_at
TICK-001,Password Reset Error,User cannot complete password reset,account-access,550e8400-e29b-41d4-a716-446655440001,2024-01-10T15:30:00Z,true,2024-01-12T10:00:00Z
TICK-002,Login Issues,Cannot log in with correct credentials,authentication,,2024-01-11T09:00:00Z,false,
TICK-003,Email Not Received,Password reset email never arrived,account-access,550e8400-e29b-41d4-a716-446655440001,2024-01-11T16:00:00Z,true,2024-01-13T11:00:00Z
TICK-004,Two-Factor Auth Problem,MFA codes not working,security,,2024-01-12T12:30:00Z,false,
TICK-005,Account Locked,Account locked after failed login attempts,account-access,,2024-01-13T08:00:00Z,true,2024-01-13T14:30:00Z
```

### Fields:
- **ticket_id**: Unique ticket identifier (required)
- **subject**: Ticket subject line (required)
- **description**: Full ticket description
- **category**: Ticket category/type
- **article_id**: UUID of related KB article (leave empty if unknown)
- **created_at**: ISO 8601 timestamp when ticket was created
- **resolved**: Boolean (true/false) indicating if resolved
- **resolved_at**: ISO 8601 timestamp when ticket was resolved (null if not resolved)

## Sample Article Content

### example-article.md

```markdown
# How to Reset Your Password

## Overview
Learn how to reset your account password if you've forgotten it or need to change it for security reasons.

## Prerequisites
- Active account with the platform
- Access to your registered email address
- Internet connection

## Step-by-Step Instructions

### Method 1: Using the Login Page
1. Go to the login page
2. Click on "Forgot Password?" link
3. Enter your email address
4. Check your email for a password reset link
5. Click the link within 24 hours
6. Enter your new password (min 12 characters, must include uppercase, lowercase, numbers, symbols)
7. Confirm your password
8. Click "Reset Password"

### Method 2: From Account Settings
1. Log in to your account
2. Go to Settings → Security
3. Click "Change Password"
4. Enter your current password
5. Enter your new password twice
6. Click "Update"

## Troubleshooting

### I didn't receive the reset email
- Check your spam/junk folder
- Verify the email address is correct
- Try resetting again after 5 minutes
- Contact support if issue persists

### Reset link expired
- Reset links are valid for 24 hours
- Request a new reset link if yours has expired

### Password doesn't meet requirements
Your password must contain:
- At least 12 characters
- One uppercase letter (A-Z)
- One lowercase letter (a-z)
- One number (0-9)
- One special character (!@#$%^&*)

## Related Articles
- Account Security Best Practices
- Enabling Two-Factor Authentication
- Account Recovery Options

## Last Updated
January 15, 2024
```
