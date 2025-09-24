# Quickstart Guide: Next.js Frontend Application

**Date**: 2025-09-24
**Estimated Time**: 30 minutes setup + 2-3 hours development

## Prerequisites

### Required Software
- Node.js 18.17+ or 20.0+ (LTS recommended)
- npm 8+ or yarn 1.22+ or pnpm 8+
- Git 2.25+
- VS Code or similar editor with TypeScript support

### Backend Services
Ensure the following services are running before starting:
- Auth Service: `http://localhost:8001`
- Product Catalog Service: `http://localhost:8004`
- Cart Service: `http://localhost:8007`

## Quick Setup (10 minutes)

### 1. Create Next.js Application
```bash
# Navigate to project root
cd project-zero-app

# Create frontend directory
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
```

### 2. Install Dependencies
```bash
# Core dependencies
npm install zustand axios react-hook-form @hookform/resolvers zod

# UI components and utilities
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-toast
npm install lucide-react clsx tailwind-merge

# Development dependencies
npm install -D @types/node @types/react @types/react-dom
npm install -D jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```

### 3. Configure Environment
```bash
# Create environment file
cp .env.local.example .env.local

# Edit .env.local with your configuration
NEXT_PUBLIC_AUTH_API_URL=http://localhost:8001
NEXT_PUBLIC_PRODUCTS_API_URL=http://localhost:8004
NEXT_PUBLIC_CART_API_URL=http://localhost:8007
NEXT_PUBLIC_APP_NAME="Project Zero Store"
```

### 4. Update Next.js Configuration
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'example.com'],
    dangerouslyAllowSVG: true,
  },
  env: {
    AUTH_API_URL: process.env.NEXT_PUBLIC_AUTH_API_URL,
    PRODUCTS_API_URL: process.env.NEXT_PUBLIC_PRODUCTS_API_URL,
    CART_API_URL: process.env.NEXT_PUBLIC_CART_API_URL,
  },
}

module.exports = nextConfig
```

## Development Workflow (15 minutes)

### 1. Start Development Server
```bash
npm run dev
# Application available at http://localhost:3000
```

### 2. Verify Backend Connectivity
```bash
# Test auth service
curl http://localhost:8001/health

# Test products service
curl http://localhost:8004/health

# Test cart service
curl http://localhost:8007/health
```

### 3. Create Basic Layout Structure
```bash
# Create core directories
mkdir -p src/components/ui
mkdir -p src/components/layout
mkdir -p src/lib
mkdir -p src/store
mkdir -p src/types
mkdir -p src/services
mkdir -p src/hooks
```

## Key Development Tasks

### 1. Set Up Store Management (20 minutes)
Create Zustand stores for:
- `src/store/auth.ts` - Authentication state
- `src/store/cart.ts` - Cart management
- `src/store/products.ts` - Product data

### 2. Create API Services (30 minutes)
Implement API clients for:
- `src/services/auth.ts` - Authentication endpoints
- `src/services/products.ts` - Product catalog endpoints
- `src/services/cart.ts` - Cart management endpoints

### 3. Build Core Components (45 minutes)
- Navigation header with cart count
- Product card component
- Cart item component
- Authentication forms (login/register)
- Loading and error states

### 4. Implement Pages (60 minutes)
- `/` - Home page with featured products
- `/products` - Product listing with filters
- `/products/[id]` - Product detail page
- `/cart` - Shopping cart management
- `/login` - User authentication
- `/register` - User registration
- `/profile` - User profile management

## Testing Strategy

### 1. Unit Tests
```bash
# Run unit tests
npm run test

# Watch mode during development
npm run test:watch

# Coverage report
npm run test:coverage
```

### 2. Integration Testing
Test key user flows:
- User registration and login
- Product browsing and filtering
- Cart operations (add, update, remove)
- Authentication state persistence

### 3. E2E Testing (Optional)
```bash
# Install Playwright
npm install -D @playwright/test

# Run E2E tests
npm run test:e2e
```

## Deployment Preparation

### 1. Production Build
```bash
# Create production build
npm run build

# Test production build locally
npm run start
```

### 2. Environment Configuration
Ensure production environment variables are set:
- `NEXT_PUBLIC_AUTH_API_URL`
- `NEXT_PUBLIC_PRODUCTS_API_URL`
- `NEXT_PUBLIC_CART_API_URL`

### 3. Performance Optimization
- Image optimization configured
- Code splitting enabled
- Lazy loading implemented
- Bundle analysis completed

## Common Issues & Solutions

### Authentication Issues
```bash
# Clear browser storage
localStorage.clear()
sessionStorage.clear()

# Check JWT token validity
curl -H "Authorization: Bearer <token>" http://localhost:8001/auth/verify
```

### API Connection Issues
```bash
# Verify service health
curl http://localhost:8001/health
curl http://localhost:8004/health
curl http://localhost:8007/health

# Check CORS configuration
# Ensure backend services allow frontend origin
```

### Build Issues
```bash
# Clear Next.js cache
rm -rf .next
npm run build

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development Commands Reference

```bash
# Development
npm run dev              # Start development server
npm run build           # Create production build
npm run start           # Start production server
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues

# Testing
npm run test            # Run unit tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Generate coverage report

# Type checking
npm run type-check      # Run TypeScript compiler check

# Code formatting
npm run format          # Format code with Prettier
npm run format:check    # Check code formatting
```

## Next Steps

After completing quickstart:
1. Implement advanced filtering and search
2. Add product image galleries
3. Implement user profile management
4. Add cart persistence across sessions
5. Integrate with checkout preparation
6. Add performance monitoring
7. Implement comprehensive error boundaries

## Getting Help

- **Documentation**: Check `/docs` directory for detailed guides
- **API Contracts**: Review `/contracts` for endpoint specifications
- **Issues**: Common problems documented in troubleshooting section
- **Development**: Use React Developer Tools and browser DevTools

## Success Validation

Your setup is successful when:
- [x] Application loads at `http://localhost:3000`
- [x] Navigation between pages works
- [x] User can register and login
- [x] Products display on home and products pages
- [x] Cart operations work for authenticated users
- [x] All backend services respond to health checks
- [x] TypeScript compilation passes without errors
- [x] Basic tests pass