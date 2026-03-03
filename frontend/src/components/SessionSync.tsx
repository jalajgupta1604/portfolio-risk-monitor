"use client";

import { useSession } from "next-auth/react";
import { useEffect, useRef } from "react";
import { setBackendToken, api } from "@/lib/api";

export default function SessionSync() {
  const { data: session } = useSession();
  const autoSyncDone = useRef(false);

  useEffect(() => {
    // backendToken is injected via the session callback in auth.ts
    const token = (session as Record<string, unknown> | null)?.backendToken as string | undefined;
    setBackendToken(token ?? null);

    // Auto-sync broker connections once after token is set
    if (token && !autoSyncDone.current) {
      autoSyncDone.current = true;
      api.autoSync().catch(() => {
        // Fire-and-forget: errors are logged server-side
      });
    }
  }, [session]);

  return null;
}
