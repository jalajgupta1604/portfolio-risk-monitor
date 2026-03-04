export { auth as middleware } from "@/auth";

export const config = {
  matcher: ["/portfolios/:path*", "/dashboard/:path*", "/brokers/:path*", "/settings/:path*", "/pricing/:path*"],
};
