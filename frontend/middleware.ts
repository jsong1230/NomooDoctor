/**
 * 미들웨어 - 인증 가드 및 리다이렉트
 * navigation.md의 미들웨어 로직 참조
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 공개 라우트 (인증 불필요)
  const publicRoutes = ['/', '/login', '/register', '/forgot-password', '/callback/kakao'];
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // API 라우트는 미들웨어에서 처리하지 않음
  if (pathname.startsWith('/api')) {
    return NextResponse.next();
  }

  // 정적 파일은 미들웨어에서 처리하지 않음
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // 인증 체크
  const accessToken = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;

  // 토큰이 없으면 로그인 페이지로 리다이렉트
  if (!accessToken && !refreshToken) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // 대시보드 라우트
  if (pathname.startsWith('/dashboard')) {
    // 사업장 등록 체크 (제외 경로)
    const excludeRoutes = ['/company/new', '/settings', '/subscription'];
    if (!excludeRoutes.some((route) => pathname.startsWith(route))) {
      const hasCompany = request.cookies.get('has_company')?.value;
      if (!hasCompany) {
        const companyNewUrl = new URL('/company/new', request.url);
        return NextResponse.redirect(companyNewUrl);
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
