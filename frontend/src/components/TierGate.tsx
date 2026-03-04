"use client";

import Link from "next/link";
import { SubscriptionTier } from "@/lib/types";
import { useSubscription } from "@/hooks/useSubscription";

const TIER_ORDER: Record<string, number> = { free: 0, paid: 1, premium: 2 };

interface TierGateProps {
  minTier: SubscriptionTier;
  children: React.ReactNode;
}

export default function TierGate({ minTier, children }: TierGateProps) {
  const { tier, loading } = useSubscription();

  if (loading) return null;

  const userOrder = TIER_ORDER[tier] ?? 0;
  const requiredOrder = TIER_ORDER[minTier] ?? 0;

  if (userOrder >= requiredOrder) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      <div className="blur-sm pointer-events-none select-none">{children}</div>
      <div className="absolute inset-0 flex items-center justify-center bg-white/60 rounded-xl">
        <div className="text-center">
          <svg className="w-8 h-8 text-slate-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
          </svg>
          <p className="text-sm font-medium text-slate-600 capitalize">{minTier} plan required</p>
          <Link href="/pricing" className="text-xs text-blue-600 hover:text-blue-700 mt-1 inline-block">
            Upgrade now
          </Link>
        </div>
      </div>
    </div>
  );
}
