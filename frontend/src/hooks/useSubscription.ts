"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SubscriptionTier } from "@/lib/types";

interface SubscriptionState {
  tier: SubscriptionTier;
  expiresAt: string | null;
  active: boolean;
  loading: boolean;
}

export function useSubscription(): SubscriptionState {
  const [state, setState] = useState<SubscriptionState>({
    tier: "free",
    expiresAt: null,
    active: false,
    loading: true,
  });

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await api.getSubscriptionStatus();
        if (!cancelled) {
          setState({
            tier: data.tier as SubscriptionTier,
            expiresAt: data.expires_at,
            active: data.active,
            loading: false,
          });
        }
      } catch {
        if (!cancelled) {
          setState((s) => ({ ...s, loading: false }));
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
