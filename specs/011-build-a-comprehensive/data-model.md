# Data Model: Documentation System Entities

**Date**: 2025-09-29  
**Status**: Complete  
**Related**: [spec.md](./spec.md) | [plan.md](./plan.md) | [research.md](./research.md)

## Core Entities

### DocumentationSystem
Root entity representing the entire documentation collection.

**Fields**:
- `root_path`: String - Base directory path ("docs/")
- `creation_date`: Date - System creation timestamp
- `last_updated`: Date - Most recent update across all documents
- `total_documents`: Integer - Count of all markdown files
- `total_services`: Integer - Number of services documented (10: frontend + 9 backend)
- `version`: String - Documentation system version

**Validation Rules**:
- root_path must exist and be writable
- total_services must equal 10 (frontend + 9 backend services)
- version must follow semantic versioning (x.y.z)

**Relationships**:
- Has many ServiceDocumentation entities
- Has one SharedDocumentation entity
- Has one ContactDirectory entity
- Has one ComplianceDocumentation entity

### ServiceDocumentation
Documentation collection for a single service (frontend or backend service).

**Fields**:
- `service_name`: String - Service identifier (api-gateway, auth-service, etc.)
- `service_type`: Enum - [frontend, backend]
- `technology_stack`: Array[String] - Technologies used (FastAPI, Node.js, etc.)
- `port`: Integer - Service port number (if applicable)
- `base_path`: String - Service documentation directory path
- `readme_path`: String - Main service README.md path
- `last_updated`: Date - Most recent update to any service document
- `document_count`: Integer - Number of documents in service directory

**Validation Rules**:
- service_name must match existing Project Zero App services
- service_type must be 'frontend' or 'backend'
- port must be unique across services (if specified)
- base_path must follow pattern: docs/services/{service_name}/

**Relationships**:
- Belongs to DocumentationSystem
- Has many DocumentCategory entities
- Has many IncidentReport entities
- Has one ServiceContact entity

### DocumentCategory
Standardized documentation categories within each service.

**Fields**:
- `category_name`: Enum - [api-docs, architecture, operations, incidents, disaster-recovery, integration, security, monitoring, deployment, troubleshooting]
- `category_path`: String - Directory path for category
- `description`: String - Category purpose description
- `document_count`: Integer - Number of documents in category
- `required`: Boolean - Whether category is mandatory for all services

**Validation Rules**:
- category_name must be from predefined enum list
- category_path must follow pattern: {service_base_path}/{category_name}/
- required categories must exist for all services

**Relationships**:
- Belongs to ServiceDocumentation
- Has many Document entities

### Document
Individual markdown documentation file.

**Fields**:
- `file_name`: String - Document filename (including .md extension)
- `file_path`: String - Full path to document
- `title`: String - Document title from metadata
- `description`: String - Document description from metadata
- `author`: String - Document author (dummy name)
- `creation_date`: Date - Document creation date
- `last_updated`: Date - Last modification date
- `version`: String - Document version
- `owner`: String - Document owner/maintainer
- `word_count`: Integer - Approximate word count
- `cross_references`: Array[String] - Paths to referenced documents

**Validation Rules**:
- file_name must end with .md extension
- word_count must be between 500-2000 for main documents
- title and description are required in metadata
- version must follow semantic versioning

**Relationships**:
- Belongs to DocumentCategory
- References other Document entities (cross-references)

### IncidentReport
Historical incident documentation for services.

**Fields**:
- `incident_id`: String - Unique incident identifier
- `incident_date`: Date - When incident occurred
- `severity`: Enum - [critical, high, medium, low]
- `service_affected`: String - Primary service affected
- `title`: String - Brief incident description
- `duration`: Integer - Incident duration in minutes
- `root_cause`: String - Identified root cause
- `resolution`: String - How incident was resolved
- `lessons_learned`: Array[String] - Key takeaways
- `action_items`: Array[String] - Follow-up actions
- `postmortem_path`: String - Path to detailed post-mortem document

**Validation Rules**:
- incident_id must be unique across all incidents
- incident_date cannot be in the future
- severity must be from predefined enum
- service_affected must match existing service names
- duration must be positive integer

**Relationships**:
- Belongs to ServiceDocumentation
- May reference Document entities in postmortem

### ContactDirectory
Organizational structure and contact information.

**Fields**:
- `directory_type`: Enum - [engineering-teams, on-call-schedule, escalation-matrix, vendor-contacts, stakeholder-directory, emergency-contacts]
- `last_updated`: Date - Most recent contact update
- `contact_count`: Integer - Number of contacts in directory

**Validation Rules**:
- directory_type must be from predefined enum
- contact_count must be positive integer

**Relationships**:
- Belongs to DocumentationSystem
- Has many Contact entities

### Contact
Individual contact information entry.

**Fields**:
- `contact_id`: String - Unique contact identifier
- `name`: String - Contact name (dummy name)
- `role`: String - Job role/title
- `team`: String - Team or department
- `email`: String - Email address (dummy)
- `phone`: String - Phone number (dummy)
- `slack_channel`: String - Slack channel (dummy)
- `pager_duty_schedule`: String - PagerDuty schedule name (if applicable)
- `contact_type`: Enum - [internal, vendor, stakeholder, emergency]
- `availability`: String - Availability description

**Validation Rules**:
- contact_id must be unique across all contacts
- email must follow valid email format (even if dummy)
- phone must follow valid phone number format (even if dummy)
- contact_type must be from predefined enum

**Relationships**:
- Belongs to ContactDirectory

### ComplianceDocumentation
Compliance and audit-related documentation.

**Fields**:
- `compliance_type`: Enum - [data-privacy, pci-dss, security-audit, access-control, data-retention, change-management]
- `document_path`: String - Path to compliance document
- `compliance_date`: Date - When compliance was last verified
- `next_review_date`: Date - When next review is due
- `status`: Enum - [compliant, non-compliant, pending-review, not-applicable]
- `auditor`: String - Auditing party (dummy name)

**Validation Rules**:
- compliance_type must be from predefined enum
- next_review_date must be after compliance_date
- status must be from predefined enum

**Relationships**:
- Belongs to DocumentationSystem
- May reference Document entities

## State Transitions

### Document Lifecycle
1. **Draft** → Document created with basic metadata
2. **Review** → Document under review for accuracy
3. **Published** → Document approved and available
4. **Outdated** → Document needs updates
5. **Archived** → Document no longer current but preserved

### Incident Report Lifecycle
1. **Reported** → Incident identified and logged
2. **Investigating** → Root cause analysis in progress
3. **Resolved** → Incident resolved, monitoring for recurrence
4. **Post-Mortem Complete** → Analysis complete, lessons learned documented
5. **Archived** → Historical record maintained

### Compliance Status Lifecycle
1. **Not Started** → Compliance assessment not begun
2. **In Progress** → Assessment or remediation underway
3. **Compliant** → Requirements fully met
4. **Non-Compliant** → Deficiencies identified, remediation needed
5. **Pending Review** → Awaiting external audit or verification

## Integration Points

### Cross-Service References
Documents may reference other services' documentation for:
- Integration guides showing service dependencies
- Shared infrastructure documentation
- Common operational procedures
- Escalation paths crossing team boundaries

### External System Integration
Documentation may reference:
- Project Zero App source code and configuration
- External monitoring systems (dummy configurations)
- Cloud infrastructure components
- Third-party service integrations

## Validation Rules Summary

### Content Requirements
- All main documents must be 500-2000 words
- All documents must include proper metadata headers
- Cross-references must point to existing documents
- Contact information must use realistic dummy data

### Structure Requirements
- All services must have standardized directory structure
- Each service must have all required document categories
- File naming must follow consistent conventions
- Directory organization must match specification

### Quality Requirements
- Documents must include specific technical details
- Incident reports must include realistic scenarios
- Compliance documents must be demo-appropriate
- Contact information must follow organizational hierarchy