# Data Model: User Profile Management Service

**Generated**: 2025-09-27 | **Phase**: 1 | **Based on**: Feature spec requirements

## Core Entities

### 1. UserProfile
**Purpose**: Main user profile entity containing personal information and preferences
**Relationships**: One-to-many with Address, ActivityLog; One-to-one with UserPreferences

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,  -- Links to auth service user

    -- Personal Information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    profile_picture_url TEXT,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Indexes
    UNIQUE INDEX idx_user_profiles_user_id (user_id),
    INDEX idx_user_profiles_created_at (created_at)
);
```

**Validation Rules**:
- `user_id`: Required, must exist in auth service
- `phone`: Optional, E.164 format validation when provided
- `profile_picture_url`: Optional, must be valid HTTP/HTTPS URL
- `first_name`, `last_name`: Optional, max 100 characters, alphanumeric + spaces
- `date_of_birth`: Optional, must be valid date, not in future

### 2. Address
**Purpose**: Shipping and billing address management with default selection
**Relationships**: Many-to-one with UserProfile

```sql
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,  -- Foreign key to user_profiles

    -- Address Information
    address_type VARCHAR(20) NOT NULL,  -- 'shipping' or 'billing'
    street_address TEXT NOT NULL,
    address_line_2 TEXT,
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(2) NOT NULL,  -- ISO 3166-1 alpha-2

    -- Address Metadata
    label VARCHAR(50),  -- e.g., 'Home', 'Work', 'Office'
    is_default BOOLEAN DEFAULT FALSE,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_addresses_user_id (user_id),
    INDEX idx_addresses_user_type (user_id, address_type),
    INDEX idx_addresses_default (user_id, address_type, is_default)
);
```

**Validation Rules**:
- `user_id`: Required, must reference existing user profile
- `address_type`: Required, enum ['shipping', 'billing']
- `street_address`: Required, max 255 characters
- `city`: Required, max 100 characters, alphanumeric + spaces + hyphens
- `postal_code`: Required, format validation by country
- `country`: Required, valid ISO 3166-1 alpha-2 country code
- `is_default`: Only one default address per user per type

### 3. UserPreferences
**Purpose**: User notification, communication, and account preferences
**Relationships**: One-to-one with UserProfile

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,  -- Foreign key to user_profiles

    -- Notification Preferences
    email_marketing BOOLEAN DEFAULT TRUE,
    email_order_updates BOOLEAN DEFAULT TRUE,
    email_security_alerts BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,

    -- Account Preferences
    preferred_language VARCHAR(5) DEFAULT 'en-US',  -- ISO 639-1 + ISO 3166-1
    preferred_currency VARCHAR(3) DEFAULT 'USD',    -- ISO 4217
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Privacy Settings
    profile_visibility VARCHAR(20) DEFAULT 'private',  -- 'public', 'private'
    data_sharing_consent BOOLEAN DEFAULT FALSE,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Indexes
    UNIQUE INDEX idx_user_preferences_user_id (user_id)
);
```

**Validation Rules**:
- `user_id`: Required, must reference existing user profile
- `preferred_language`: Must be valid locale code (ISO 639-1 + ISO 3166-1)
- `preferred_currency`: Must be valid ISO 4217 currency code
- `timezone`: Must be valid IANA timezone identifier
- `profile_visibility`: Enum ['public', 'private']

### 4. ActivityLog
**Purpose**: Audit trail of significant account activities
**Relationships**: Many-to-one with UserProfile

```sql
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,  -- Foreign key to user_profiles

    -- Activity Information
    activity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    entity_type VARCHAR(50),     -- e.g., 'profile', 'address', 'preferences'
    entity_id INTEGER,           -- ID of affected entity

    -- Request Context
    ip_address INET,
    user_agent TEXT,
    correlation_id VARCHAR(36),  -- Request correlation ID

    -- Change Details (JSON)
    old_values JSONB,
    new_values JSONB,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_activity_logs_user_id (user_id),
    INDEX idx_activity_logs_created_at (created_at),
    INDEX idx_activity_logs_user_type (user_id, activity_type),
    INDEX idx_activity_logs_entity (entity_type, entity_id)
);
```

**Validation Rules**:
- `user_id`: Required, must reference existing user profile
- `activity_type`: Required, predefined activity types
- `description`: Required, human-readable activity description
- `ip_address`: Optional, valid IPv4 or IPv6 address
- `correlation_id`: Optional, UUID v4 format

## Entity Relationships

```
UserProfile (1) ──── (1) UserPreferences
     │
     └─── (1) ──── (*) Address
     │
     └─── (1) ──── (*) ActivityLog
```

## Activity Types Enumeration

### Profile Activities
- `profile_created`: New user profile created
- `profile_updated`: Profile information modified
- `profile_viewed`: Profile accessed (admin only)

### Address Activities
- `address_created`: New address added
- `address_updated`: Address information modified
- `address_deleted`: Address removed
- `address_default_changed`: Default address selection changed

### Preference Activities
- `preferences_updated`: User preferences modified
- `notification_settings_changed`: Notification preferences updated
- `privacy_settings_changed`: Privacy settings modified

### Authentication Activities
- `profile_access_denied`: Unauthorized access attempt
- `admin_access`: Administrative access to profile data

## State Transitions

### Address Default Management
```
State: User has no addresses
├─ Add first address → Automatically becomes default
└─ Add subsequent address → User choice for default

State: User changes default
├─ Previous default → is_default = FALSE
└─ New default → is_default = TRUE
```

### Profile Completion Status
```
State: Incomplete Profile (missing required fields)
├─ Add first_name → Check completion status
├─ Add last_name → Check completion status
└─ Add required fields → Mark as complete

State: Complete Profile
├─ Remove required field → Mark as incomplete
└─ Update fields → Maintain complete status
```

## Data Validation Rules

### Profile Validation
- Phone number: E.164 format regex validation
- Profile picture URL: HTTP/HTTPS URL validation with image format check
- Name fields: Alphanumeric characters, spaces, hyphens only
- Date of birth: Must be valid date, not in future, reasonable age limits

### Address Validation
- Street address: Required, no PO Box restrictions
- Postal code: Format validation based on country
- Country: Valid ISO 3166-1 alpha-2 code
- Default constraint: Only one default per user per address type

### Preference Validation
- Language: Valid locale code from supported list
- Currency: Valid ISO 4217 code from supported list
- Timezone: Valid IANA timezone identifier

### Activity Log Validation
- Activity type: Must be from predefined enum
- JSON fields: Valid JSON format with schema validation
- IP address: Valid IPv4/IPv6 format when provided

## Performance Considerations

### Indexing Strategy
- Primary keys: Auto-indexed
- Foreign keys: Indexed for join performance
- Common queries: user_id fields heavily indexed
- Composite indexes: user_id + type combinations
- Temporal queries: created_at/updated_at indexed

### Query Optimization
- User profile retrieval: Single query with eager loading
- Address lookup: Filtered by user_id and type
- Activity logs: Paginated with date range filtering
- Default addresses: Optimized lookup with composite index

### Data Archival
- Activity logs: Consider partitioning by date for large volumes
- Soft deletes: Retain audit trail for deleted addresses
- Data retention: Configurable retention policy for activity logs

## Security Considerations

### Data Protection
- No sensitive data in activity logs (passwords, tokens)
- IP address hashing for privacy compliance
- User agent sanitization to prevent injection
- JSON field validation to prevent malicious content

### Access Control
- User isolation: Strict user_id filtering in all queries
- Admin access: Separate permissions for cross-user access
- Audit trail: All access and modifications logged

### Data Integrity
- Foreign key constraints: Maintain referential integrity
- Check constraints: Validate enum values at database level
- Transaction boundaries: Atomic operations for related changes

## Migration Strategy

### Initial Schema Creation
1. Create user_profiles table
2. Create user_preferences table with foreign key
3. Create addresses table with foreign key
4. Create activity_logs table with foreign key
5. Create indexes for performance
6. Insert default preferences for existing users (if applicable)

### Future Schema Changes
- Use Alembic for versioned migrations
- Backward compatibility for API versions
- Data migration scripts for schema changes
- Rollback procedures for failed migrations