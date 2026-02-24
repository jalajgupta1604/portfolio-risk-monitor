import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PATHS = ["/portfolios", "/dashboard"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the path requires auth
  const isProtected = PROTECTED_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  // Check for auth token in cookie or header
  // Since we use localStorage on the client, edge middleware can only check cookies.
  // We set a lightweight cookie flag from the client side as a hint.
  const hasToken = request.cookies.get("has_auth_token")?.value === "1";

  if (!hasToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/portfolios/:path*", "/dashboard/:path*"],
};
