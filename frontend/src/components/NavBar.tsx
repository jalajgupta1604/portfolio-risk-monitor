"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";

export default function NavBar() {
  const { user, loading, logout } = useAuth();

  return (
    <nav className="flex items-center gap-1">
      {loading ? (
        <div className="w-4 h-4 border-2 border-slate-300 border-t-transparent rounded-full animate-spin" />
      ) : user ? (
        <>
          <Link
            href="/portfolios"
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Portfolios
          </Link>
          <Link
            href="/dashboard"
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Risk Dashboard
          </Link>
          <span className="px-3 py-2 text-sm text-slate-500">{user.email}</span>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            Logout
          </button>
        </>
      ) : (
        <>
          <Link
            href="/login"
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Register
          </Link>
        </>
      )}
    </nav>
  );
}
