# User Profile Service Documentation

**Service Type**: Backend User Profile Management Service  
**Technology**: FastAPI (Python 3.13+)  
**Port**: 8002  
**Repository Path**: `services/user-profile-service/`

## Overview

The User Profile Service manages comprehensive user profile information for the Project Zero App e-commerce platform. It handles user preferences, contact information, address management, and profile data while maintaining strict data privacy and GDPR compliance standards.

## Purpose and Responsibilities

### Core Functions

- **Profile Management**: Comprehensive user profile data management
- **Address Management**: Multiple shipping and billing address support
- **Preference Management**: User preferences for notifications and settings
- **Data Privacy**: GDPR compliance and data protection
- **Contact Information**: Email, phone, and communication preferences

### In-Scope Features

- User profile CRUD operations with comprehensive validation
- Multiple address management (shipping, billing, default addresses)
- User preference management for notifications and communication
- GDPR compliance features including data export and deletion
- Profile picture and avatar management
- Privacy settings and data sharing preferences
- Health monitoring and dependency validation

### Out-of-Scope (Future Considerations)

- Social media profile integration
- Advanced user analytics and behavioral tracking
- Customer support ticket management
- Loyalty program and rewards management
- Advanced privacy controls and consent management

## Architecture Overview

```text
┌─── FastAPI Application ───┐
│  ├── /profile/* routes    │
│  ├── GDPR compliance      │
│  ├── JWT authentication   │
│  └── Health monitoring    │
├─── Business Logic ────────┤
│  ├── Profile operations   │
│  ├── Address management   │
│  ├── Preference handling  │
│  └── Privacy controls     │
├─── Data Access Layer ─────┤
│  ├── SQLAlchemy ORM       │
│  ├── Profile models       │
│  ├── Address models       │
│  └── Privacy audit        │
├─── External Integration ──┤
│  ├── Auth service         │
│  └── Notification service │
└─── Infrastructure ────────┘
   ├── PostgreSQL/SQLite
   ├── File storage
   └── Privacy compliance
```

## API Endpoints

### Profile Management

- `GET /profile` - Get current user's profile information
- `PUT /profile` - Update user profile data
- `DELETE /profile` - Delete user profile (GDPR compliance)
- `GET /profile/export` - Export all user data (GDPR compliance)

### Address Management

- `GET /profile/addresses` - List user's addresses
- `POST /profile/addresses` - Add new address
- `PUT /profile/addresses/{address_id}` - Update address
- `DELETE /profile/addresses/{address_id}` - Delete address
- `PUT /profile/addresses/{address_id}/default` - Set default address

### Preference Management

- `GET /profile/preferences` - Get user preferences
- `PUT /profile/preferences` - Update user preferences
- `GET /profile/privacy` - Get privacy settings
- `PUT /profile/privacy` - Update privacy settings

### Health and Monitoring

- `GET /health` - Basic service health check
- `GET /health/ready` - Readiness check with dependencies

## Technology Stack

### Core Technologies

- **FastAPI**: High-performance web framework with OpenAPI documentation
- **Python 3.13+**: Latest Python with enhanced security and performance
- **SQLAlchemy**: Advanced ORM with relationship management
- **Pydantic**: Data validation with privacy-aware models

### Data Management

- **PostgreSQL**: Production database with GDPR compliance features
- **SQLite**: Development and testing environment
- **File Storage**: Profile pictures and document storage
- **Encryption**: Sensitive data encryption at rest

### Privacy and Compliance

- **GDPR Libraries**: Data protection and compliance validation
- **Audit Logging**: Comprehensive data access logging
- **Anonymization**: Data anonymization and pseudonymization

## Configuration

### Environment Variables

| Variable | Purpose | Default | Required | Notes |
|----------|---------|---------|----------|-------|
| `DATABASE_URL` | Database connection | `sqlite:///./user_profile.db` | No | PostgreSQL for production |
| `JWT_SECRET_KEY` | JWT verification | Auto-generated | Recommended | Must match auth service |
| `AUTH_SERVICE_URL` | Auth service endpoint | `http://localhost:8001` | Yes | User authentication |
| `FILE_STORAGE_PATH` | Profile file storage | `./uploads` | No | File system or cloud storage |
| `GDPR_COMPLIANCE_MODE` | GDPR enforcement | `strict` | No | Privacy compliance level |
| `DATA_RETENTION_DAYS` | Data retention period | `2555` (7 years) | No | GDPR compliance |
| `HOST` | Service bind address | `0.0.0.0` | No | Container deployment |
| `PORT` | Service port | `8002` | No | Service mesh configuration |

## Data Model

### User Profile Schema

```json
{
  "user_id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "date_of_birth": "date",
  "profile_picture_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "preferences": {
    "language": "string",
    "currency": "string",
    "timezone": "string",
    "notifications": {
      "email": "boolean",
      "sms": "boolean",
      "push": "boolean"
    }
  },
  "privacy": {
    "profile_visibility": "string",
    "data_sharing": "boolean",
    "marketing_consent": "boolean"
  }
}
```

### Address Schema

```json
{
  "id": "integer",
  "user_id": "string",
  "type": "string",
  "is_default": "boolean",
  "first_name": "string",
  "last_name": "string",
  "company": "string",
  "address_line_1": "string",
  "address_line_2": "string",
  "city": "string",
  "state": "string",
  "postal_code": "string",
  "country": "string",
  "phone": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## GDPR Compliance

### Data Protection Features

- **Right to Access**: Complete user data export functionality
- **Right to Rectification**: Profile update and correction capabilities
- **Right to Erasure**: Secure data deletion with audit trails
- **Right to Portability**: Structured data export in JSON format
- **Right to Restrict Processing**: Data processing restriction controls

### Privacy Controls

- **Consent Management**: Granular consent for data processing
- **Data Minimization**: Collect only necessary profile information
- **Purpose Limitation**: Clear data usage purposes and limitations
- **Retention Policies**: Automatic data deletion after retention period

### Audit and Compliance

- **Access Logging**: Comprehensive logging of all data access
- **Change Tracking**: Audit trail for all profile modifications
- **Compliance Reporting**: GDPR compliance status and reports
- **Data Breach Procedures**: Automated breach detection and notification

## Address Management

### Address Types

- **SHIPPING**: Default shipping address for orders
- **BILLING**: Billing address for payment processing
- **WORK**: Work address for business deliveries
- **OTHER**: Additional addresses for special cases

### Address Validation

- **Format Validation**: Address format validation by country
- **Postal Code Validation**: Postal code format and existence validation
- **Delivery Validation**: Address deliverability verification (planned)
- **Duplicate Prevention**: Detection and prevention of duplicate addresses

## Preference Management

### Notification Preferences

- **Email Notifications**: Order updates, promotions, system notifications
- **SMS Notifications**: Critical alerts and delivery notifications
- **Push Notifications**: Real-time app notifications
- **Frequency Controls**: Notification frequency and timing preferences

### Display Preferences

- **Language**: User interface language selection
- **Currency**: Preferred currency for pricing display
- **Timezone**: User timezone for date/time formatting
- **Theme**: UI theme and display preferences

## Integration Patterns

### Service Dependencies

```text
User Profile Service ──► Auth Service (/auth/verify)
           │
           └────────────► Notification Service (preferences)
```

### Data Flow

- **Profile Updates**: Trigger preference updates to notification service
- **Authentication**: Validate user identity via auth service
- **Privacy Controls**: Apply privacy settings across integrated services

## Security and Privacy

### Data Protection

- **Encryption**: Sensitive profile data encrypted at rest
- **Access Controls**: Role-based access to profile information
- **Anonymization**: Personal data anonymization for analytics
- **Secure Deletion**: Cryptographic deletion of sensitive data

### Privacy by Design

- **Data Minimization**: Collect minimal necessary profile data
- **Purpose Limitation**: Clear data usage purposes and consent
- **Transparency**: Clear privacy policies and data usage information
- **User Control**: Granular user control over profile data

## Deployment and Operations

### Local Development

```bash
cd services/user-profile-service
uv sync
uv run uvicorn main:app --reload --port 8002
```

### Docker Deployment

```bash
docker build -t user-profile-service:latest services/user-profile-service
docker run -p 8002:8002 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/profiledb" \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  user-profile-service:latest
```

### GDPR Compliance Deployment

- **Data Encryption**: Encrypt all personal data at rest and in transit
- **Access Logging**: Enable comprehensive access and modification logging
- **Retention Policies**: Configure automatic data retention and deletion
- **Compliance Monitoring**: Enable GDPR compliance monitoring and alerting

## Monitoring and Observability

### Profile Metrics

- **Profile Completeness**: User profile completion rates
- **Address Usage**: Address creation and usage patterns
- **Preference Changes**: User preference modification trends
- **Privacy Settings**: Privacy control adoption and usage

### GDPR Compliance Metrics

- **Data Requests**: GDPR data request processing times
- **Data Deletions**: User data deletion completion rates
- **Consent Management**: Consent collection and withdrawal tracking
- **Compliance Violations**: Privacy compliance issue tracking

### Security Monitoring

- **Profile Access**: Unusual profile access pattern detection
- **Data Modifications**: Suspicious profile modification alerts
- **Privacy Violations**: Privacy setting bypass attempts
- **Authentication Failures**: Failed authentication tracking

## Related Documentation

### Service Documentation

- [API Documentation](./api-docs/endpoints.md) - Complete API reference
- [Data Model](./architecture/data-model.md) - Database schema and relationships
- [Architecture Overview](./architecture/overview.md) - Technical architecture
- [Data Privacy](./security/data-privacy.md) - Privacy and security design

### Operational Documentation

- [GDPR Compliance](./operations/gdpr-compliance.md) - Compliance procedures
- [Auth Integration](./integration/auth-integration.md) - Authentication integration
- [Data Management](./operations/data-management.md) - Profile data procedures
- [Monitoring Setup](./monitoring/profile-monitoring.md) - Observability configuration

---

**Last Updated**: 2025-09-29  
**Maintainer**: Engineering Team  
**Service Version**: 1.0.0  
**Documentation Version**: 1.0.0