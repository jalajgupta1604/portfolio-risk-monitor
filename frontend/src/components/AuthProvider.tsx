"use client";

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { User, UserCreate, UserLogin } from "@/lib/types";
import { authApi, getToken, setToken, clearToken } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (data: UserLogin) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

const PROTECTED_PATHS = ["/portfolios", "/dashboard"];

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const validateToken = useCallback(async () => {
    const stored = getToken();
    if (!stored) {
      setLoading(false);
      return;
    }
    setTokenState(stored);
    try {
      const me = await authApi.getMe();
      setUser(me);
      document.cookie = "has_auth_token=1; path=/; SameSite=Lax";
    } catch {
      clearToken();
      setTokenState(null);
      document.cookie = "has_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    validateToken();
  }, [validateToken]);

  // Redirect to login when user becomes unauthenticated on a protected page
  useEffect(() => {
    if (!loading && !user && PROTECTED_PATHS.some((p) => pathname === p || pathname.startsWith(p + "/"))) {
      router.replace("/login");
    }
  }, [loading, user, pathname, router]);

  const login = async (data: UserLogin) => {
    const resp = await authApi.login(data);
    setToken(resp.access_token);
    setTokenState(resp.access_token);
    document.cookie = "has_auth_token=1; path=/; SameSite=Lax";
    const me = await authApi.getMe();
    setUser(me);
  };

  const register = async (data: UserCreate) => {
    await authApi.register(data);
    // Auto-login after registration
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    clearToken();
    setTokenState(null);
    setUser(null);
    document.cookie = "has_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    router.replace("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
