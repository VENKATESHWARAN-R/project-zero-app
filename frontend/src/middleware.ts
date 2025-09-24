import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define routes that require authentication
const protectedRoutes = [
  '/profile',
  '/cart'
]

// Define routes that should redirect authenticated users
const authRoutes = [
  '/login',
  '/register'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if user has auth tokens (simple check for middleware)
  const authTokens = request.cookies.get('auth-tokens')?.value
  const isAuthenticated = Boolean(authTokens)

  // Handle protected routes
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      const url = new URL('/login', request.url)
      url.searchParams.set('redirect', pathname)
      return NextResponse.redirect(url)
    }
  }

  // Handle auth routes (redirect if already authenticated)
  if (authRoutes.some(route => pathname.startsWith(route))) {
    if (isAuthenticated) {
      const redirectUrl = request.nextUrl.searchParams.get('redirect') || '/'
      return NextResponse.redirect(new URL(redirectUrl, request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}