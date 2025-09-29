# Runbook Template

**Runbook Title**: [Descriptive Title]  
**Service**: [Service Name]  
**Version**: 1.0  
**Created**: [YYYY-MM-DD]  
**Last Updated**: [YYYY-MM-DD]  
**Owner**: [Team/Individual]  
**On-Call Contact**: [Contact Information]  
**Related**: [Links to related documentation]  

## Purpose

Brief description of what this runbook covers and when to use it.

## Service Overview

### Service Description
- **Service Name**: [Name]
- **Primary Function**: [What the service does]
- **Technology Stack**: [Languages, frameworks, databases]
- **Dependencies**: [Upstream/downstream services]

### Architecture Summary
```
[Simple ASCII diagram or description of service architecture]
```

### Key Metrics
- **SLA Target**: [Response time/availability target]
- **Normal Load**: [Expected traffic/requests]
- **Peak Load**: [Maximum expected load]

## Common Scenarios

### Scenario 1: [Common Issue Name]

**Symptoms**:
- [Symptom 1]
- [Symptom 2]

**Immediate Actions**:
1. [First action to take]
2. [Second action to take]

**Diagnosis Steps**:
1. [How to confirm this is the issue]
2. [Where to look for evidence]

**Resolution**:
1. [Step-by-step fix]
2. [Verification steps]

**Escalation**: If above steps don't work within [X minutes], escalate to [contact].

### Scenario 2: [Another Common Issue]

**Symptoms**:
- [Symptom 1]
- [Symptom 2]

**Immediate Actions**:
1. [First action to take]
2. [Second action to take]

**Diagnosis Steps**:
1. [How to confirm this is the issue]
2. [Where to look for evidence]

**Resolution**:
1. [Step-by-step fix]
2. [Verification steps]

**Escalation**: If above steps don't work within [X minutes], escalate to [contact].

## Health Checks

### Service Health Endpoints
- **Health Check**: `GET /health`
  - **Expected Response**: `200 OK` with `{"status": "healthy"}`
  - **Timeout**: 5 seconds

- **Readiness Check**: `GET /health/ready`
  - **Expected Response**: `200 OK` with dependency status
  - **Timeout**: 10 seconds

### Manual Health Verification
1. [Manual step to verify service health]
2. [Expected outcomes]
3. [What unhealthy looks like]

## Monitoring and Alerting

### Key Dashboards
- **Primary Dashboard**: [Link to main dashboard]
- **Infrastructure Dashboard**: [Link to infra metrics]
- **Application Dashboard**: [Link to app metrics]

### Critical Alerts
| Alert Name | Condition | Severity | Response Time |
|------------|-----------|----------|---------------|
| [Alert 1] | [Trigger condition] | Critical | Immediate |
| [Alert 2] | [Trigger condition] | High | 5 minutes |
| [Alert 3] | [Trigger condition] | Medium | 15 minutes |

### Log Locations
- **Application Logs**: [Path/URL to application logs]
- **Error Logs**: [Path/URL to error logs]
- **Access Logs**: [Path/URL to access logs]

## Troubleshooting Commands

### Service Status
```bash
# Check service status
kubectl get pods -l app=[service-name]

# Check service logs
kubectl logs -l app=[service-name] --tail=100

# Check recent events
kubectl get events --sort-by='.lastTimestamp'
```

### Database Operations
```bash
# Check database connectivity
[command to test DB connection]

# Check database performance
[command to check DB metrics]

# View recent DB logs
[command to view DB logs]
```

### Performance Analysis
```bash
# Check CPU and memory usage
[command to check resource usage]

# Check network connectivity
[command to test network]

# Analyze slow queries
[command to check slow operations]
```

## Emergency Procedures

### Service Restart
1. [Pre-restart checks]
2. [Restart command/procedure]
3. [Post-restart verification]
4. [What to do if restart fails]

### Traffic Diversion
1. [How to divert traffic away from service]
2. [Verification that traffic is diverted]
3. [How to restore traffic]

### Rollback Procedure
1. [How to identify if rollback is needed]
2. [Rollback commands/procedure]
3. [Verification of rollback]
4. [Communication requirements]

## Escalation Procedures

### Escalation Matrix
| Severity | Initial Response | Escalation (15 min) | Escalation (30 min) |
|----------|------------------|-------------------|-------------------|
| Critical | On-call engineer | Team lead | Service owner |
| High | On-call engineer | Team lead | Manager |
| Medium | On-call engineer | Next business day | Team lead |

### Contact Information
- **Primary On-Call**: [Contact method]
- **Secondary On-Call**: [Contact method]
- **Team Lead**: [Contact method]
- **Service Owner**: [Contact method]

### Communication Channels
- **Incident Channel**: [Slack channel/Teams]
- **Status Updates**: [Where to post updates]
- **Customer Communication**: [Process for external comms]

## Useful Resources

### Documentation Links
- [Service Architecture Documentation]
- [API Documentation]
- [Database Schema Documentation]
- [Deployment Documentation]

### Tools and Access
- **Monitoring**: [Links to monitoring tools]
- **Logging**: [Links to logging systems]
- **Deployment**: [Links to deployment tools]
- **Database**: [Links to database management tools]

### Historical Information
- [Link to recent incidents]
- [Link to common issues documentation]
- [Link to performance baselines]

---

**Template Version**: 1.0  
**Last Updated**: 2025-09-29  
**Next Review**: 2025-12-29