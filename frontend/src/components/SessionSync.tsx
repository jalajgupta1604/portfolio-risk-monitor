"use client";

import { useSession } from "next-auth/react";
import { useEffect } from "react";
import { setBackendToken } from "@/lib/api";

export default function SessionSync() {
  const { data: session } = useSession();

  useEffect(() => {
    // backendToken is injected via the session callback in auth.ts
    const token = (session as Record<string, unknown> | null)?.backendToken as string | undefined;
    setBackendToken(token ?? null);
  }, [session]);

  return null;
}
