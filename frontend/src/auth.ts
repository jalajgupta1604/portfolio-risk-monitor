import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
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
    jwt({ token, user }: any) {
      if (user) {
        token.backendToken = user.backendToken;
        token.userId = user.id;
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
