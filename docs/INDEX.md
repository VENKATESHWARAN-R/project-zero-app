# Project Zero App Documentation Index

**Version**: 1.0.0  
**Last Updated**: 2025-09-29  
**Owner**: Engineering Team  
**Purpose**: Master index for all Project Zero App documentation  

## Welcome to Project Zero App Documentation

This documentation system provides comprehensive information about Project Zero App, a polyglot microservices e-commerce platform designed to demonstrate enterprise-grade development patterns, security practices, and operational procedures.

## Quick Navigation

### 🚀 Getting Started
- [System Overview](./shared/architecture/system-overview.md)
- [Development Setup](./shared/onboarding/developer-guide.md)
- [API Gateway Guide](./services/api-gateway/README.md)

### 📚 Service Documentation
- [Frontend Application](./services/frontend/README.md)
- [API Gateway Service](./services/api-gateway/README.md)
- [Authentication Service](./services/auth-service/README.md)
- [Product Catalog Service](./services/product-catalog-service/README.md)
- [Shopping Cart Service](./services/cart-service/README.md)
- [Order Processing Service](./services/order-service/README.md)
- [Payment Service](./services/payment-service/README.md)
- [User Profile Service](./services/user-profile-service/README.md)
- [Notification Service](./services/notification-service/README.md)

### 🏗️ Architecture & Design
- [System Architecture](./shared/architecture/system-overview.md)
- [Service Mesh Documentation](./shared/architecture/service-mesh.md)
- [Data Flow Diagrams](./shared/architecture/data-flow-diagrams.md)

### 🔧 Operations
- [Incident Response](./shared/operations/incident-response.md)
- [On-Call Guide](./shared/operations/on-call-guide.md)
- [Deployment Strategy](./shared/operations/deployment-strategy.md)
- [Monitoring Platform](./shared/monitoring/platform-monitoring.md)

### 📞 Contacts & Teams
- [Engineering Teams](./contacts/engineering-teams.md)
- [On-Call Schedule](./contacts/on-call-schedule.md)
- [Escalation Matrix](./contacts/escalation-matrix.md)
- [Emergency Contacts](./contacts/emergency-contacts.md)

### 📋 Compliance & Security
- [Data Privacy Policy](./compliance/data-privacy-policy.md)
- [PCI DSS Compliance](./compliance/pci-dss-compliance.md)
- [Security Audit Reports](./compliance/security-audit-reports.md)
- [Access Control Policies](./compliance/access-control-policies.md)

### 🛠️ Infrastructure
- [Docker Compose Guide](./infrastructure/docker-compose-guide.md)
- [Database Administration](./infrastructure/database-administration.md)
- [Network Architecture](./infrastructure/network-architecture.md)
- [Backup Strategy](./infrastructure/backup-strategy.md)

## Documentation Structure

### Service Documentation Categories
Each service includes documentation in these categories:
- **API Documentation**: OpenAPI specs, endpoint guides, authentication
- **Architecture**: System design, technology choices, ADRs
- **Operations**: Runbooks, SOPs, deployment procedures
- **Incidents**: Reports, post-mortems, lessons learned
- **Disaster Recovery**: DR plans, backup procedures, restoration guides
- **Integration**: Service dependencies, API contracts, data exchange
- **Security**: Threat models, policies, vulnerability reports
- **Monitoring**: Alerting rules, dashboards, SLI/SLOs
- **Deployment**: CI/CD pipelines, rollback procedures, canary deployment
- **Troubleshooting**: Common issues, debugging guides, performance tuning

### Technology Stack Overview

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| Frontend | Next.js, TypeScript | 3000 | User interface |
| API Gateway | Go, Gorilla Mux | 8000 | Request routing, auth middleware |
| Auth Service | FastAPI, SQLAlchemy | 8001 | Authentication & authorization |
| Product Catalog | FastAPI, SQLAlchemy | 8004 | Product management |
| Cart Service | Node.js, Express | 8007 | Shopping cart management |
| Order Service | FastAPI, SQLAlchemy | 8008 | Order processing |
| Payment Service | FastAPI, SQLAlchemy | 8009 | Payment processing |
| User Profile | FastAPI, SQLAlchemy | 8002 | User profile management |
| Notification | Node.js, Express | 8011 | Multi-channel notifications |

## Search and Navigation Tips

### Finding Information Quickly
1. **Service-specific info**: Navigate to `services/{service-name}/README.md`
2. **Cross-cutting concerns**: Check `shared/` directory
3. **Operational procedures**: Look in service `operations/` folders
4. **Incident history**: Check service `incidents/` folders
5. **Emergency contacts**: Always available in `contacts/`

### Documentation Standards
- All documents include metadata headers with ownership and review dates
- Cross-references link related documentation
- Incident reports follow standardized templates
- SOPs include step-by-step procedures with verification steps
- Architecture decisions are documented in ADR format

## Recent Updates

| Date | Update | Impact |
|------|--------|--------|
| 2025-09-29 | Initial documentation system created | All services now have comprehensive docs |
| 2025-09-29 | Incident report templates standardized | Consistent incident documentation |
| 2025-09-29 | Contact directories established | Clear escalation paths defined |

## Feedback and Contributions

### Documentation Improvement
- **Feedback**: Report issues or suggestions via team channels
- **Updates**: Follow change management process in `compliance/change-management-log.md`
- **Templates**: Use templates in `templates/` directory for consistency

### Review Schedule
- **Quarterly Reviews**: All documentation reviewed for accuracy
- **Incident-Triggered Updates**: Documentation updated after major incidents
- **Architecture Changes**: ADRs updated when architecture decisions change

## Emergency Information

### Critical Contacts
- **Primary On-Call**: Check `contacts/on-call-schedule.md`
- **Escalation**: Follow `contacts/escalation-matrix.md`
- **Emergency**: See `contacts/emergency-contacts.md`

### Service Status
- **Health Checks**: All services expose `/health` and `/health/ready` endpoints
- **Monitoring**: Primary dashboards linked in each service's monitoring documentation
- **Incident Response**: Follow procedures in `shared/operations/incident-response.md`

---

**Last Updated**: 2025-09-29  
**Documentation System Version**: 1.0.0  
**Next Review**: 2025-12-29