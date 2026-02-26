import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";

// Server-side URL for NextAuth authorize (inside Docker: http://app:8000/api/v1)
const API_BASE =
  process.env.API_URL_INTERNAL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const OAUTH_BRIDGE_SECRET = process.env.OAUTH_BRIDGE_SECRET || "";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google,
    Credentials({
      credentials: {
        email: {},
        password: {},
      },
      async authorize(credentials) {
        const { email, password } = credentials as {
          email: string;
          password: string;
        };

        // Call backend /auth/login
        const loginRes = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!loginRes.ok) return null;

        const { access_token } = await loginRes.json();

        // Fetch user profile
        const meRes = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        if (!meRes.ok) return null;

        const user = await meRes.json();

        return {
          id: user.id,
          email: user.email,
          name: user.full_name,
          backendToken: access_token,
        };
      },
    }),
  ],
  session: { strategy: "jwt", maxAge: 23 * 60 * 60 },
  pages: { signIn: "/login" },
  callbacks: {
    authorized({ auth: session, request }) {
      const isLoggedIn = !!session?.user;
      const { pathname } = request.nextUrl;
      const isProtected =
        pathname.startsWith("/portfolios") || pathname.startsWith("/dashboard");
      if (isProtected && !isLoggedIn) {
        return false; // redirects to pages.signIn
      }
      return true;
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async jwt({ token, user, account }: any) {
      // Credentials flow: user object already has backendToken
      if (user?.backendToken) {
        token.backendToken = user.backendToken;
        token.userId = user.id;
      }

      // Google OAuth flow: exchange Google identity for backend JWT
      if (account?.provider === "google" && user) {
        const res = await fetch(`${API_BASE}/auth/oauth-login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-OAuth-Bridge-Secret": OAUTH_BRIDGE_SECRET,
          },
          body: JSON.stringify({
            email: user.email,
            full_name: user.name,
            oauth_provider: "google",
          }),
        });

        if (res.ok) {
          const { access_token } = await res.json();
          token.backendToken = access_token;

          // Fetch backend user ID
          const meRes = await fetch(`${API_BASE}/auth/me`, {
            headers: { Authorization: `Bearer ${access_token}` },
          });
          if (meRes.ok) {
            const me = await meRes.json();
            token.userId = me.id;
          }
        }
      }

      return token;
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    session({ session, token }: any) {
      session.backendToken = token.backendToken;
      if (token.userId) {
        session.user.id = token.userId;
      }
      return session;
    },
  },
});
