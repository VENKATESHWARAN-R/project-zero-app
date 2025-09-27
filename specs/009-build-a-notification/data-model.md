# Data Model: Notification Service

**Date**: 2025-09-28
**Feature**: Notification Service
**Technology**: Sequelize ORM with SQLite

## Entity Relationships

```
NotificationTemplate (1) ────┐
                             │
                             ▼
Notification (N) ──────► NotificationHistory (1)
     │
     └──────► UserNotificationPreference (N)
```

## Core Entities

### 1. Notification
Represents a communication sent to a user.

**Table**: `notifications`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique notification identifier |
| userId | VARCHAR(255) | NOT NULL, INDEX | Target user identifier from auth service |
| templateId | UUID | FOREIGN KEY | Reference to notification template |
| channel | ENUM | NOT NULL | Delivery channel: 'email', 'sms', 'in_app' |
| recipient | VARCHAR(255) | NOT NULL | Email address or phone number |
| subject | VARCHAR(500) | NULLABLE | Email subject or SMS preview |
| content | TEXT | NOT NULL | Notification body content |
| metadata | JSON | NULLABLE | Additional context data |
| status | ENUM | NOT NULL, DEFAULT 'pending' | 'pending', 'sent', 'delivered', 'failed' |
| scheduledAt | TIMESTAMP | NULLABLE | When to send (NULL for immediate) |
| sentAt | TIMESTAMP | NULLABLE | When actually sent |
| deliveredAt | TIMESTAMP | NULLABLE | When delivery confirmed |
| failureReason | TEXT | NULLABLE | Error details if failed |
| createdAt | TIMESTAMP | NOT NULL | Record creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last modification time |

**Indexes**:
- `idx_notifications_user_id` on `userId`
- `idx_notifications_status` on `status`
- `idx_notifications_scheduled_at` on `scheduledAt`
- `idx_notifications_created_at` on `createdAt`

**Validation Rules**:
- `channel` must be one of: 'email', 'sms', 'in_app'
- `status` must be one of: 'pending', 'sent', 'delivered', 'failed'
- `recipient` must be valid email for email channel, valid phone for SMS
- `content` must not be empty
- `scheduledAt` must be in the future if provided

### 2. NotificationTemplate
Represents reusable templates for notifications.

**Table**: `notification_templates`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique template identifier |
| name | VARCHAR(255) | NOT NULL, UNIQUE | Template identifier name |
| type | ENUM | NOT NULL | Template category: 'welcome', 'order', 'payment', 'system', 'promotional' |
| channel | ENUM | NOT NULL | Target channel: 'email', 'sms', 'in_app' |
| subject | VARCHAR(500) | NULLABLE | Template subject (for email) |
| content | TEXT | NOT NULL | Template body with variable placeholders |
| variables | JSON | NULLABLE | Available template variables and their types |
| isActive | BOOLEAN | NOT NULL, DEFAULT true | Whether template is available for use |
| createdAt | TIMESTAMP | NOT NULL | Record creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last modification time |

**Indexes**:
- `idx_notification_templates_name` on `name`
- `idx_notification_templates_type_channel` on `type, channel`
- `idx_notification_templates_active` on `isActive`

**Validation Rules**:
- `type` must be one of: 'welcome', 'order', 'payment', 'system', 'promotional'
- `channel` must be one of: 'email', 'sms', 'in_app'
- `name` must be unique and follow pattern: `{type}_{channel}_{purpose}`
- `content` must contain valid template variable syntax: `{{variableName}}`

### 3. NotificationHistory
Represents the historical record and audit trail of notifications.

**Table**: `notification_history`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique history record identifier |
| notificationId | UUID | FOREIGN KEY | Reference to original notification |
| userId | VARCHAR(255) | NOT NULL, INDEX | Target user (denormalized for queries) |
| event | ENUM | NOT NULL | Event type: 'created', 'sent', 'delivered', 'failed', 'retried' |
| previousStatus | ENUM | NULLABLE | Status before this event |
| newStatus | ENUM | NULLABLE | Status after this event |
| details | JSON | NULLABLE | Event-specific details and context |
| providerId | VARCHAR(255) | NULLABLE | External provider delivery ID |
| errorCode | VARCHAR(100) | NULLABLE | Error code from delivery provider |
| errorMessage | TEXT | NULLABLE | Human-readable error description |
| timestamp | TIMESTAMP | NOT NULL | When this event occurred |

**Indexes**:
- `idx_notification_history_notification_id` on `notificationId`
- `idx_notification_history_user_id` on `userId`
- `idx_notification_history_event` on `event`
- `idx_notification_history_timestamp` on `timestamp`

**Validation Rules**:
- `event` must be one of: 'created', 'sent', 'delivered', 'failed', 'retried'
- `previousStatus` and `newStatus` must be valid notification statuses when provided
- `timestamp` must not be in the future

### 4. UserNotificationPreference
Represents user preferences for receiving notifications.

**Table**: `user_notification_preferences`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique preference record identifier |
| userId | VARCHAR(255) | NOT NULL, INDEX | User identifier from auth service |
| type | ENUM | NOT NULL | Notification type: 'welcome', 'order', 'payment', 'system', 'promotional' |
| channel | ENUM | NOT NULL | Channel: 'email', 'sms', 'in_app' |
| enabled | BOOLEAN | NOT NULL, DEFAULT true | Whether user wants these notifications |
| frequency | ENUM | NOT NULL, DEFAULT 'immediate' | 'immediate', 'daily', 'weekly', 'disabled' |
| metadata | JSON | NULLABLE | Additional preference settings |
| createdAt | TIMESTAMP | NOT NULL | Record creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last modification time |

**Indexes**:
- `idx_user_notification_preferences_user_id` on `userId`
- `idx_user_notification_preferences_type_channel` on `type, channel`
- `unique_user_type_channel` UNIQUE on `userId, type, channel`

**Validation Rules**:
- `type` must be one of: 'welcome', 'order', 'payment', 'system', 'promotional'
- `channel` must be one of: 'email', 'sms', 'in_app'
- `frequency` must be one of: 'immediate', 'daily', 'weekly', 'disabled'
- One record per user/type/channel combination

### 5. ScheduledNotification
Represents notifications scheduled for future delivery.

**Table**: `scheduled_notifications`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique scheduled notification identifier |
| notificationId | UUID | FOREIGN KEY | Reference to notification to be sent |
| scheduledAt | TIMESTAMP | NOT NULL, INDEX | When to send the notification |
| attempts | INTEGER | NOT NULL, DEFAULT 0 | Number of delivery attempts |
| maxAttempts | INTEGER | NOT NULL, DEFAULT 3 | Maximum retry attempts |
| retryInterval | INTEGER | NOT NULL, DEFAULT 300 | Seconds between retries |
| status | ENUM | NOT NULL, DEFAULT 'scheduled' | 'scheduled', 'processing', 'sent', 'failed' |
| lastAttemptAt | TIMESTAMP | NULLABLE | When last delivery was attempted |
| nextAttemptAt | TIMESTAMP | NULLABLE | When next retry will occur |
| createdAt | TIMESTAMP | NOT NULL | Record creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last modification time |

**Indexes**:
- `idx_scheduled_notifications_scheduled_at` on `scheduledAt`
- `idx_scheduled_notifications_status` on `status`
- `idx_scheduled_notifications_next_attempt` on `nextAttemptAt`

**Validation Rules**:
- `status` must be one of: 'scheduled', 'processing', 'sent', 'failed'
- `scheduledAt` must be in the future when created
- `maxAttempts` must be positive
- `retryInterval` must be positive

## Sequelize Model Relationships

```javascript
// Notification belongs to NotificationTemplate
Notification.belongsTo(NotificationTemplate, {
  foreignKey: 'templateId',
  as: 'template'
});

// Notification has many NotificationHistory records
Notification.hasMany(NotificationHistory, {
  foreignKey: 'notificationId',
  as: 'history'
});

// ScheduledNotification belongs to Notification
ScheduledNotification.belongsTo(Notification, {
  foreignKey: 'notificationId',
  as: 'notification'
});

// NotificationTemplate has many Notifications
NotificationTemplate.hasMany(Notification, {
  foreignKey: 'templateId',
  as: 'notifications'
});
```

## State Transitions

### Notification Status Flow
```
pending ──► sent ──► delivered
   │           │
   │           └──► failed
   │
   └──► failed
```

### Scheduled Notification Flow
```
scheduled ──► processing ──► sent
     │             │
     │             └──► failed ──► processing (retry)
     │
     └──► failed (max attempts reached)
```

## Data Constraints and Business Rules

### Notification Rules
1. Each notification must have a valid user ID that exists in the auth service
2. Recipient must match the channel type (email format for email, phone format for SMS)
3. Scheduled notifications must have `scheduledAt` in the future
4. Failed notifications can be retried up to the maximum attempt limit
5. Delivered notifications cannot change status

### Template Rules
1. Template names must be unique across the system
2. Template variables in content must match the variables JSON schema
3. Inactive templates cannot be used for new notifications
4. Template content must be valid for the target channel

### Preference Rules
1. Users can have only one preference setting per notification type/channel combination
2. System notifications cannot be completely disabled (minimum in-app delivery)
3. Promotional notifications default to opt-in required

### History Rules
1. All notification status changes must be recorded in history
2. History records are immutable once created
3. History must maintain chronological order per notification

## Migration Strategy

### Initial Schema Creation
1. Create tables in dependency order: templates → notifications → history, preferences, scheduled
2. Create indexes for performance
3. Insert default notification templates
4. Set up foreign key constraints

### Default Templates
The system will include these default templates:
- `welcome_email_registration` - User registration welcome
- `order_email_confirmation` - Order confirmation
- `order_sms_shipped` - Order shipped notification
- `payment_email_receipt` - Payment receipt
- `system_in_app_maintenance` - System maintenance alerts

## Performance Considerations

### Query Optimization
- User notification history queries use userId index
- Scheduled notification processing uses scheduledAt index
- Template lookups use name index for fast retrieval

### Data Retention
- Notification history older than 90 days can be archived
- Failed notifications older than 30 days can be cleaned up
- Scheduled notifications are automatically cleaned after completion

### Scaling Considerations
- Partitioning by date for large notification volumes
- Read replicas for notification history queries
- Message queue integration for high-volume scenarios (future enhancement)