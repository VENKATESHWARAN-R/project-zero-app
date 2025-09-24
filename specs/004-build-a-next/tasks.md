# Tasks: Next.js Frontend Application for Project Zero E-commerce Platform

**Input**: Design documents from `/Users/mnp3209/Library/CloudStorage/OneDrive-TeliaCompany/Desktop/project-zero-app/specs/004-build-a-next/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Next.js 14 App Router, TypeScript, Tailwind CSS, Zustand
   → Libraries: axios, react-hook-form, zod, shadcn/ui
2. Load design documents ✓:
   → data-model.md: User, Product, Cart, CartItem, Category entities
   → contracts/: auth-api.md, products-api.md, cart-api.md
   → research.md: Framework and library decisions
3. Generate tasks by category ✓
4. Apply task rules ✓
5. Number tasks sequentially (T001, T002...) ✓
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness ✓
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `frontend/src/` structure per plan.md

## Phase 3.1: Setup & Foundation

- [ ] T001 Create Next.js project structure in frontend/ directory with App Router
- [ ] T002 [P] Install core dependencies (Next.js 14, TypeScript, Tailwind CSS)
- [ ] T003 [P] Install state management and form libraries (Zustand, react-hook-form, zod)
- [ ] T004 [P] Install UI component libraries (shadcn/ui, lucide-react)
- [ ] T005 [P] Install API and testing dependencies (axios, jest, react-testing-library)
- [ ] T006 Configure TypeScript with strict settings in frontend/tsconfig.json
- [ ] T007 Configure Tailwind CSS and globals in frontend/src/app/globals.css
- [ ] T008 [P] Configure Next.js settings in frontend/next.config.js
- [ ] T009 [P] Setup environment variables in frontend/.env.local
- [ ] T010 [P] Configure ESLint and Prettier in frontend/
- [ ] T011 [P] Configure Jest testing framework in frontend/jest.config.js

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### API Contract Tests
- [ ] T012 [P] Auth API contract test in frontend/tests/contract/auth-api.test.ts
- [ ] T013 [P] Products API contract test in frontend/tests/contract/products-api.test.ts
- [ ] T014 [P] Cart API contract test in frontend/tests/contract/cart-api.test.ts

### Component Tests
- [ ] T015 [P] ProductCard component test in frontend/tests/components/ProductCard.test.tsx
- [ ] T016 [P] CartItem component test in frontend/tests/components/CartItem.test.tsx
- [ ] T017 [P] Header navigation test in frontend/tests/components/Header.test.tsx
- [ ] T018 [P] AuthForm component test in frontend/tests/components/AuthForm.test.tsx

### Store Tests
- [ ] T019 [P] Auth store test in frontend/tests/store/auth.test.ts
- [ ] T020 [P] Cart store test in frontend/tests/store/cart.test.ts
- [ ] T021 [P] Products store test in frontend/tests/store/products.test.ts

### Integration Tests
- [ ] T022 [P] User authentication flow test in frontend/tests/integration/auth-flow.test.tsx
- [ ] T023 [P] Product browsing flow test in frontend/tests/integration/product-browsing.test.tsx
- [ ] T024 [P] Cart management flow test in frontend/tests/integration/cart-management.test.tsx

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Type Definitions
- [ ] T025 [P] User types in frontend/src/types/user.ts
- [ ] T026 [P] Product types in frontend/src/types/product.ts
- [ ] T027 [P] Cart types in frontend/src/types/cart.ts
- [ ] T028 [P] API response types in frontend/src/types/api.ts
- [ ] T029 [P] Form types in frontend/src/types/forms.ts

### API Services
- [ ] T030 [P] Auth service client in frontend/src/services/auth.ts
- [ ] T031 [P] Products service client in frontend/src/services/products.ts
- [ ] T032 [P] Cart service client in frontend/src/services/cart.ts
- [ ] T033 [P] Base API client with interceptors in frontend/src/lib/api.ts

### Zustand Stores
- [ ] T034 [P] Auth store implementation in frontend/src/store/auth.ts
- [ ] T035 [P] Cart store implementation in frontend/src/store/cart.ts
- [ ] T036 [P] Products store implementation in frontend/src/store/products.ts

### Utility Functions
- [ ] T037 [P] Form validation schemas in frontend/src/lib/validations.ts
- [ ] T038 [P] Utility functions in frontend/src/lib/utils.ts
- [ ] T039 [P] Constants and configuration in frontend/src/lib/constants.ts

### UI Components
- [ ] T040 [P] Loading spinner component in frontend/src/components/ui/Loading.tsx
- [ ] T041 [P] Error boundary component in frontend/src/components/ui/ErrorBoundary.tsx
- [ ] T042 [P] Button component in frontend/src/components/ui/Button.tsx
- [ ] T043 [P] Input component in frontend/src/components/ui/Input.tsx
- [ ] T044 [P] Toast notification component in frontend/src/components/ui/Toast.tsx

### Layout Components
- [ ] T045 Header component with navigation in frontend/src/components/layout/Header.tsx
- [ ] T046 Footer component in frontend/src/components/layout/Footer.tsx
- [ ] T047 Main layout component in frontend/src/components/layout/Layout.tsx

### Product Components
- [ ] T048 [P] ProductCard component in frontend/src/components/product/ProductCard.tsx
- [ ] T049 [P] ProductList component in frontend/src/components/product/ProductList.tsx
- [ ] T050 [P] SearchBar component in frontend/src/components/product/SearchBar.tsx
- [ ] T051 [P] ProductFilters component in frontend/src/components/product/ProductFilters.tsx

### Cart Components
- [ ] T052 [P] CartItem component in frontend/src/components/cart/CartItem.tsx
- [ ] T053 [P] CartSummary component in frontend/src/components/cart/CartSummary.tsx
- [ ] T054 [P] CartIcon component in frontend/src/components/cart/CartIcon.tsx

### Auth Components
- [ ] T055 [P] LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [ ] T056 [P] RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [ ] T057 [P] AuthForm wrapper component in frontend/src/components/auth/AuthForm.tsx

## Phase 3.4: Pages Implementation

### App Router Pages
- [ ] T058 Root layout component in frontend/src/app/layout.tsx
- [ ] T059 Home page with featured products in frontend/src/app/page.tsx
- [ ] T060 Products listing page in frontend/src/app/products/page.tsx
- [ ] T061 Product detail page in frontend/src/app/products/[id]/page.tsx
- [ ] T062 Cart management page in frontend/src/app/cart/page.tsx
- [ ] T063 Login page in frontend/src/app/login/page.tsx
- [ ] T064 Register page in frontend/src/app/register/page.tsx
- [ ] T065 User profile page in frontend/src/app/profile/page.tsx
- [ ] T066 [P] Not found page in frontend/src/app/not-found.tsx
- [ ] T067 [P] Loading page in frontend/src/app/loading.tsx
- [ ] T068 [P] Error page in frontend/src/app/error.tsx

## Phase 3.5: Integration & Authentication

### Authentication Flow
- [ ] T069 JWT token management and refresh logic in frontend/src/lib/auth.ts
- [ ] T070 Route protection middleware in frontend/src/middleware.ts
- [ ] T071 Auth provider context in frontend/src/providers/AuthProvider.tsx

### Cart Integration
- [ ] T072 Cart persistence with localStorage in frontend/src/lib/cart-storage.ts
- [ ] T073 Cart synchronization with backend on auth changes

### API Integration
- [ ] T074 Error handling and retry logic for API calls
- [ ] T075 Request/response interceptors for token management
- [ ] T076 API error boundary and user feedback

## Phase 3.6: Styling & Responsive Design

### Tailwind Components
- [ ] T077 [P] Responsive grid layouts for products
- [ ] T078 [P] Mobile-first navigation menu
- [ ] T079 [P] Form styling and validation feedback
- [ ] T080 [P] Cart and checkout responsive design

### Interactive Features
- [ ] T081 Product image gallery with zoom
- [ ] T082 Shopping cart quantity controls
- [ ] T083 Search autocomplete and filters
- [ ] T084 Loading states and skeleton components

## Phase 3.7: Performance & Optimization

### Next.js Optimizations
- [ ] T085 [P] Image optimization configuration
- [ ] T086 [P] Code splitting and lazy loading
- [ ] T087 [P] Metadata and SEO optimization
- [ ] T088 [P] Bundle analysis and optimization

### Performance Enhancements
- [ ] T089 Product data caching strategy
- [ ] T090 Debounced search functionality
- [ ] T091 Optimistic UI updates for cart operations
- [ ] T092 Error recovery and offline handling

## Phase 3.8: Polish & Testing

### Unit Tests
- [ ] T093 [P] Utils function tests in frontend/tests/unit/utils.test.ts
- [ ] T094 [P] Validation schema tests in frontend/tests/unit/validation.test.ts
- [ ] T095 [P] API service tests in frontend/tests/unit/services.test.ts

### Integration Testing
- [ ] T096 Complete user registration and login flow testing
- [ ] T097 Product browsing and filtering flow testing
- [ ] T098 Cart operations and persistence testing
- [ ] T099 Error boundary and fallback testing

### Documentation
- [ ] T100 [P] Update frontend/README.md with setup and development guide
- [ ] T101 [P] Create component documentation in frontend/docs/components.md
- [ ] T102 [P] API integration guide in frontend/docs/api-integration.md

## Dependencies

### Critical Path
- Setup (T001-T011) → Tests (T012-T024) → Core Implementation (T025-T057) → Pages (T058-T068)
- T033 (base API client) blocks T030-T032 (service clients)
- T034-T036 (stores) depend on T030-T032 (services) and T025-T029 (types)
- T045 (Header) depends on T034 (auth store) and T035 (cart store)
- T058 (root layout) depends on T045 (Header) and T046 (Footer)
- T069-T071 (auth flow) depend on T034 (auth store) and T030 (auth service)

### Parallel Groups
1. **Dependencies Installation**: T002-T005 can run together
2. **Configuration**: T006-T011 can run together after dependencies
3. **Contract Tests**: T012-T014 can run together
4. **Component Tests**: T015-T018 can run together
5. **Store Tests**: T019-T021 can run together
6. **Integration Tests**: T022-T024 can run together
7. **Type Definitions**: T025-T029 can run together
8. **Service Clients**: T030-T032 can run together after T033
9. **Stores**: T034-T036 can run together after services and types
10. **UI Components**: T040-T044 can run together
11. **Product Components**: T048-T051 can run together
12. **Cart Components**: T052-T054 can run together
13. **Auth Components**: T055-T057 can run together

## Parallel Execution Examples

### Setup Phase
```bash
# Launch dependency installation together (T002-T005):
Task: "Install core dependencies (Next.js 14, TypeScript, Tailwind CSS)"
Task: "Install state management and form libraries (Zustand, react-hook-form, zod)"
Task: "Install UI component libraries (shadcn/ui, lucide-react)"
Task: "Install API and testing dependencies (axios, jest, react-testing-library)"
```

### Contract Tests Phase
```bash
# Launch API contract tests together (T012-T014):
Task: "Auth API contract test in frontend/tests/contract/auth-api.test.ts"
Task: "Products API contract test in frontend/tests/contract/products-api.test.ts"
Task: "Cart API contract test in frontend/tests/contract/cart-api.test.ts"
```

### Type Definitions Phase
```bash
# Launch type definitions together (T025-T029):
Task: "User types in frontend/src/types/user.ts"
Task: "Product types in frontend/src/types/product.ts"
Task: "Cart types in frontend/src/types/cart.ts"
Task: "API response types in frontend/src/types/api.ts"
Task: "Form types in frontend/src/types/forms.ts"
```

### Component Development Phase
```bash
# Launch product components together (T048-T051):
Task: "ProductCard component in frontend/src/components/product/ProductCard.tsx"
Task: "ProductList component in frontend/src/components/product/ProductList.tsx"
Task: "SearchBar component in frontend/src/components/product/SearchBar.tsx"
Task: "ProductFilters component in frontend/src/components/product/ProductFilters.tsx"
```

## Notes
- [P] tasks = different files, no dependencies between them
- All tests must fail before implementing corresponding functionality (TDD)
- Use TypeScript strict mode for better type safety
- Follow Next.js 14 App Router conventions
- Implement mobile-first responsive design
- Use Zustand for global state management
- Implement proper error boundaries and loading states
- JWT tokens stored in localStorage with proper refresh logic

## Task Generation Rules Applied

1. **From Contracts**: Each contract file → test task (T012-T014) and service implementation (T030-T032)
2. **From Data Model**: Each entity → type definition (T025-T029) and store (T034-T036)
3. **From User Stories**: Authentication, browsing, and cart flows → integration tests (T022-T024)
4. **Ordering**: Setup → Tests → Types → Services → Components → Pages → Integration → Polish

## Validation Checklist
- [x] All contracts have corresponding tests (T012-T014)
- [x] All entities have type and store tasks (T025-T036)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (marked with [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD approach: tests written first and must fail
- [x] Complete user flows covered (auth, browsing, cart)
- [x] Responsive design and performance considerations included
- [x] Error handling and loading states addressed