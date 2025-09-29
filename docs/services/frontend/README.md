# Frontend Application Documentation

**Service**: Frontend Application  
**Technology**: Next.js 14, TypeScript, React 18  
**Port**: 3000  
**Owner**: Frontend Engineering Team  
**On-Call**: [See contacts/engineering-teams.md]  
**Status**: Active Development  
**Last Updated**: 2025-09-29  

## Quick Links

- [Architecture Overview](./architecture/overview.md)
- [Component Structure](./architecture/component-structure.md)
- [Deployment Guide](./deployment/deployment-guide.md)
- [API Integration](./integration/api-integration.md)
- [Troubleshooting](./troubleshooting/common-issues.md)
- [Performance Monitoring](./monitoring/performance-monitoring.md)

## Service Overview

The Project Zero App frontend is a modern, responsive web application built with Next.js 14 and TypeScript. It provides a complete e-commerce user experience including product browsing, cart management, order processing, and user account management. The application implements server-side rendering for optimal performance and SEO, with client-side hydration for rich interactivity.

### Key Features

- **Product Catalog**: Browse and search products with filtering and categorization
- **Shopping Cart**: Add, remove, and manage items in cart with real-time updates
- **User Authentication**: Login, logout, and user session management
- **Order Management**: Place orders, track status, and view order history
- **Payment Processing**: Secure payment workflows with multiple payment methods
- **User Profiles**: Manage personal information, addresses, and preferences
- **Notifications**: Real-time notifications for order updates and system messages
- **Responsive Design**: Mobile-first design that works across all device sizes

### Architecture Highlights

- **Framework**: Next.js 14 with App Router for modern React patterns
- **Styling**: Tailwind CSS for utility-first styling and consistent design
- **State Management**: Zustand for lightweight, scalable state management
- **API Communication**: Custom service layer with TypeScript interfaces
- **Testing**: Jest and React Testing Library for comprehensive test coverage
- **Performance**: Code splitting, lazy loading, and optimized bundle sizes

### Dependencies

The frontend application integrates with all backend services through the API Gateway:

- **API Gateway** (Port 8000): All API requests are routed through the gateway
- **Authentication Service**: User login, logout, and session management
- **Product Catalog Service**: Product data, search, and categorization
- **Cart Service**: Shopping cart operations and persistence
- **Order Service**: Order creation, tracking, and management
- **Payment Service**: Payment processing and transaction handling
- **User Profile Service**: User information and preference management
- **Notification Service**: Real-time notifications and messaging

### Technology Stack Details

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | Next.js | 14.x | React framework with SSR/SSG |
| Language | TypeScript | 5.x | Type-safe JavaScript |
| Styling | Tailwind CSS | 3.x | Utility-first CSS framework |
| State Management | Zustand | 4.x | Lightweight state management |
| HTTP Client | Fetch API | Native | API communication |
| Testing | Jest + RTL | Latest | Unit and integration testing |
| Build Tool | Webpack | 5.x | Module bundler (via Next.js) |
| Package Manager | npm | 10.x | Dependency management |

## Development Environment

### Prerequisites

- Node.js 18.x or higher
- npm 10.x or higher
- Git access to repository
- Access to backend services (via API Gateway)

### Local Development Setup

```bash
# Clone repository and navigate to frontend
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with appropriate values

# Start development server
npm run dev

# Application will be available at http://localhost:3000
```

### Environment Variables

| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | API Gateway URL | `http://localhost:8000` | Yes |
| `NEXT_PUBLIC_APP_NAME` | Application name | `Project Zero App` | No |
| `NEXT_PUBLIC_ENVIRONMENT` | Environment name | `development` | No |
| `NODE_ENV` | Node.js environment | `development` | No |

## API Integration

The frontend communicates exclusively with the API Gateway, which routes requests to appropriate backend services. All API communication is handled through a centralized service layer located in `src/services/`.

### Service Layer Structure

```
src/services/
├── auth.service.ts          # Authentication operations
├── product.service.ts       # Product catalog operations
├── cart.service.ts          # Shopping cart operations
├── order.service.ts         # Order management operations
├── payment.service.ts       # Payment processing
├── profile.service.ts       # User profile management
├── notification.service.ts  # Notification operations
├── api.config.ts           # API configuration and interceptors
└── types/                  # TypeScript type definitions
```

### Authentication Flow

1. User submits login credentials via login form
2. Frontend calls `auth.service.login()` method
3. Service sends POST request to `/api/auth/login`
4. API Gateway routes to Authentication Service
5. On success, JWT tokens are stored in secure HTTP-only cookies
6. All subsequent API requests include authentication headers
7. Frontend updates UI based on authentication state

## Performance Characteristics

### Bundle Sizes (Production)

- **Initial JavaScript**: ~180KB gzipped
- **CSS Bundle**: ~45KB gzipped
- **Total Initial Load**: ~225KB gzipped
- **Lighthouse Score**: 95+ (Performance, Accessibility, Best Practices, SEO)

### Core Web Vitals Targets

- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Input Delay (FID)**: < 100ms

### Caching Strategy

- **Static Assets**: 1 year cache with versioning
- **API Responses**: Configurable per endpoint (5min - 1 hour)
- **Page Data**: ISR (Incremental Static Regeneration) for product pages
- **User Data**: Real-time updates, no caching

## Security Considerations

### Authentication Security

- JWT tokens stored in secure, HTTP-only cookies
- CSRF protection enabled for all state-changing operations
- Automatic token refresh to maintain session security
- Secure logout with server-side token invalidation

### Data Protection

- All API communication over HTTPS in production
- Input validation and sanitization on all user inputs
- XSS protection through React's built-in escaping
- Content Security Policy (CSP) headers configured

### Access Control

- Route-level authentication guards
- Component-level permission checks
- Graceful degradation for unauthorized access
- Clear error messaging for security violations

## Monitoring and Observability

### Performance Monitoring

- Real User Monitoring (RUM) via Web Vitals API
- Error tracking with detailed stack traces
- Performance budgets and alerts
- Custom metrics for business-critical flows

### Analytics Integration

- User behavior tracking (privacy-compliant)
- Conversion funnel analysis
- A/B testing capability
- Performance correlation with business metrics

### Health Monitoring

- Application health checks via `/api/health`
- Dependency health monitoring (API Gateway connectivity)
- Client-side error reporting
- Uptime monitoring and alerting

## Deployment Information

### Build Process

```bash
# Production build
npm run build

# Build output validation
npm run start

# Static export (if needed)
npm run export
```

### Deployment Targets

- **Development**: Local development server (npm run dev)
- **Staging**: Preview deployments for testing
- **Production**: Optimized build with SSR/SSG

### Infrastructure Requirements

- Node.js 18.x runtime environment
- CDN for static asset delivery
- Load balancer for high availability
- SSL/TLS termination
- Environment-specific configuration

## Emergency Procedures

### Incident Response

1. **Check Application Health**: Verify frontend is responding at primary URL
2. **Verify API Gateway Connection**: Test `/api/health` endpoint
3. **Review Error Logs**: Check for JavaScript errors and API failures
4. **Check Performance**: Monitor Core Web Vitals and response times
5. **Escalate if Needed**: Follow escalation matrix in contacts/

### Rollback Procedure

1. Identify last known good deployment version
2. Execute rollback via deployment pipeline
3. Verify application functionality post-rollback
4. Clear CDN cache if necessary
5. Notify stakeholders of rollback completion

### Common Emergency Scenarios

- **API Gateway Failure**: Enable maintenance mode, display service unavailable message
- **Authentication Failure**: Redirect users to login, clear corrupted session data
- **Payment Processing Issues**: Disable checkout, display maintenance message
- **Performance Degradation**: Enable performance monitoring, consider CDN purge

---

**Service Owner**: Frontend Engineering Team  
**Technical Lead**: Sarah Chen <sarah.chen@projectzero.com>  
**On-Call Rotation**: [See contacts/on-call-schedule.md]  
**Last Health Check**: 2025-09-29 ✅ Healthy  
**Next Review**: 2025-12-29