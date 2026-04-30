import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isAuthenticated = request.cookies.has("refresh_token");

  const isAuthPage = pathname.startsWith("/login") || 
                     pathname.startsWith("/register") || 
                     pathname.startsWith("/forgot-password") || 
                     pathname.startsWith("/reset-password") ||
                     pathname.startsWith("/verify-email");

  if (!isAuthenticated && !isAuthPage && pathname !== "/") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthenticated && isAuthPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
