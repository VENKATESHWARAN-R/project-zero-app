# Research Findings: Order Processing Service

**Phase**: 0 - Research & Technical Decision Making
**Date**: 2025-09-25
**Status**: Complete

## Overview

This document consolidates research findings for all technical decisions and clarifications needed for the Order Processing Service implementation in Project Zero App.

## Research Areas

### 1. Tax Calculation Method

**Decision**: Fixed Rate Tax Calculation (8.5% flat rate)

**Rationale**:
- Aligns with demo platform simplicity requirements
- Demonstrates tax calculation concepts without overwhelming complexity
- No external dependencies or extensive database requirements
- Immediate implementation with minimal code changes
- Educational value while remaining comprehensible

**Alternatives Considered**:
- Location-based tax calculation - Rejected due to massive complexity (11,000+ jurisdictions, extensive database maintenance)
- External tax services (Avalara, TaxJar) - Rejected due to external dependencies, API costs, operational complexity for demo purposes

**Implementation Notes**:
- Add `TAX_RATE` as environment variable (default: 0.085)
- Simple multiplication in order calculation logic
- Include tax breakdown in order response schema
- Clear migration path to more complex systems if needed

### 2. Shipping Cost Calculation

**Decision**: Configurable Flat Rate with Weight Tiers

**Rationale**:
- Demonstrates realistic business logic without over-engineering
- Shows shipping calculation concepts clearly
- Microservices-friendly with minimal external dependencies
- Easy to understand, test, and showcase
- Balances realism with simplicity

**Alternatives Considered**:
- Pure flat rate - Rejected as too simplistic, lacks educational value
- Full carrier API integration - Rejected as over-engineered for demo, adds complexity
- Complex location-based system - Rejected due to extensive geographic data requirements

**Implementation Structure**:
```
Shipping Tiers:
- Light (≤1 lb): $5.99
- Medium (≤5 lb): $8.99
- Heavy (≤20 lb): $15.99
- Freight (>20 lb): $25.99

Optional zone multipliers:
- Local: 1.0x
- Regional: 1.2x
- National: 1.5x
- Expedited: 2.0x
```

### 3. Payment Processing Integration Scope

**Decision**: Order Service focuses on Order Lifecycle Management, separate Payment Service handles payment processing

**Rationale**:
- Follows microservices architecture best practices (separation of concerns)
- Aligns with Project Zero App architecture (separate Order and Payment services planned)
- Single Responsibility Principle - order management vs payment processing
- Independent scalability and security boundaries
- Proper demonstration of service coordination patterns

**Alternatives Considered**:
- Combined order-payment service - Rejected for violating microservices principles
- Order service with payment gateway integration - Rejected for coupling concerns
- Event-driven payment coordination - Considered for future enhancement

**Implementation Notes**:
- Order Service creates orders in "pending" status
- Payment Service handles payment processing (mock for demo)
- Communication via HTTP APIs and events
- Order status updates based on payment events
- Each service maintains its own database

### 4. Admin User Authorization Levels

**Decision**: Simple Role-Based Authorization with Two Admin Levels

**Admin Roles**:
- **Super Admin**: Full system access and user management
- **Order Admin**: Order management permissions only

**Rationale**:
- Demonstrates RBAC principles without over-engineering
- Clear security boundaries for educational purposes
- Maintainable complexity suitable for demo platform
- Integrates cleanly with existing JWT-based auth service
- Realistic but not overwhelming for showcase purposes

**Alternatives Considered**:
- Single admin role - Rejected as too simplistic
- Complex RBAC with fine-grained permissions - Rejected as over-engineered
- Resource-based permissions - Rejected as beyond demo scope

**Implementation Notes**:
- Extend User model with role field (enum: user, order_admin, super_admin)
- Include role in JWT payload for stateless authorization
- Create reusable FastAPI dependencies for role checking
- Simple database migration to add role field

### 5. Order Modification Policy

**Decision**: Flexible Status-Based Modification Policy

**Modification Rules by Status**:
- **Pending**: Full modifications (items, quantities, addresses, cancellation)
- **Confirmed**: Limited modifications (address updates, partial cancellations)
- **Processing**: Minimal modifications (address corrections only)
- **Shipped/Delivered/Cancelled**: No modifications (separate return processes)

**Rationale**:
- Demonstrates industry-standard practices
- Educational value showing real-world business constraints
- Balances user experience with operational constraints
- Provides clear API design patterns
- Shows proper audit trail implementation

**Alternatives Considered**:
- Amazon-style (very restrictive) - Rejected as too limiting for demo
- Full flexibility (always modifiable) - Rejected as unrealistic
- Binary (modifiable until shipped) - Rejected as too simplistic

**Implementation Notes**:
- Status-dependent validation logic
- Audit trail with order_modifications table
- Business constraints (max 2 address changes, no modifications within 1 hour of shipping)
- RESTful endpoints for different modification types

## Technology Stack Confirmation

Based on research and constitutional requirements:

- **Language**: Python 3.13+
- **Framework**: FastAPI (consistent with auth/catalog services)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Database**: SQLite (dev), PostgreSQL (production)
- **Testing**: pytest with TestClient
- **Containerization**: Docker with multi-stage builds
- **Port**: 8008
- **Dependencies**: Minimal, aligned with existing services

## Integration Points Clarified

1. **Cart Service (port 8007)**: Retrieve cart contents and clear cart after order creation
2. **Auth Service (port 8001)**: User verification and JWT token validation
3. **Product Catalog Service (port 8004)**: Product details and inventory validation
4. **Future Payment Service**: Payment processing coordination

## Risk Assessment

**Low Risk**:
- Technical stack alignment with existing services
- Clear service boundaries and responsibilities
- Well-established patterns for FastAPI/SQLAlchemy

**Medium Risk**:
- Inter-service communication coordination
- Order status workflow complexity
- Audit trail implementation

**Mitigation Strategies**:
- Start with simple inter-service HTTP calls
- Implement comprehensive testing for status transitions
- Use existing logging patterns for audit trails

## Ready for Phase 1

All NEEDS CLARIFICATION items have been resolved with appropriate decisions for the demonstration platform scope. Technical approach is fully defined and aligned with constitutional requirements.