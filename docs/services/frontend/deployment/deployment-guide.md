# Frontend Deployment Guide

**Author**: DevOps Team  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Frontend Engineering Team  
**Related**: [Architecture Overview](../architecture/overview.md)  
**Review Date**: 2025-12-29  

## Summary

Comprehensive deployment guide for the Project Zero App frontend application, covering build processes, environment configuration, deployment strategies, and rollback procedures.

## Build Process

### Development Build
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Development server runs on http://localhost:3000
```

### Production Build
```bash
# Create optimized production build
npm run build

# Start production server
npm start

# Verify build output
npm run analyze
```

### Build Optimization
- Code splitting by routes and components
- Tree shaking to remove unused code
- Image optimization and WebP conversion
- CSS minification and purging
- Bundle analysis and size monitoring

## Environment Configuration

### Environment Variables
| Variable | Development | Staging | Production | Purpose |
|----------|-------------|---------|------------|---------|
| NEXT_PUBLIC_API_BASE_URL | http://localhost:8000 | https://staging-api.projectzero.com | https://api.projectzero.com | API Gateway URL |
| NEXT_PUBLIC_ENVIRONMENT | development | staging | production | Environment identifier |
| NODE_ENV | development | production | production | Node.js environment |

### Configuration Files
- `next.config.ts` - Next.js configuration
- `.env.local` - Local development variables
- `.env.production` - Production variables
- `package.json` - Dependencies and scripts

## Deployment Strategies

### Vercel Deployment (Recommended)
1. Connect GitHub repository to Vercel
2. Configure environment variables
3. Set up custom domain
4. Enable automatic deployments

### Docker Deployment
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

### Static Export
```bash
# For static hosting (CDN)
npm run build && npm run export
```

## Rollback Procedures

### Automatic Rollback
1. Monitor deployment health checks
2. Automatically rollback on failure
3. Verify previous version functionality
4. Notify team of rollback completion

### Manual Rollback
1. Identify last known good deployment
2. Revert to previous version via deployment platform
3. Clear CDN cache if necessary
4. Update DNS if custom deployment
5. Verify application functionality

---
**Deployment Owner**: DevOps Team  
**Next Review**: 2025-12-29