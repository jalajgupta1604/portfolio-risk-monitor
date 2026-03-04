"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useSubscription } from "@/hooks/useSubscription";

const PLANS = [
  {
    name: "Free",
    tier: "free",
    price: "0",
    features: [
      "Portfolio risk scoring",
      "Stress testing",
      "Correlation matrix",
      "Email alerts",
      "5 portfolios",
    ],
  },
  {
    name: "Paid",
    tier: "paid",
    price: "499",
    features: [
      "Everything in Free",
      "AI risk explanations",
      "WhatsApp alerts",
      "Weekly PDF reports",
      "Unlimited portfolios",
    ],
    popular: true,
  },
  {
    name: "Premium",
    tier: "premium",
    price: "999",
    features: [
      "Everything in Paid",
      "Macro sensitivity analysis",
      "Smart hedge suggestions",
      "Priority support",
      "API access",
    ],
  },
];

export default function PricingPage() {
  const { tier: currentTier, loading } = useSubscription();
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);

  const handleCheckout = async (tier: string) => {
    if (tier === "free") return;
    setCheckoutLoading(tier);
    try {
      const data = await api.createCheckout(tier);
      if (data.short_url) {
        window.location.href = data.short_url;
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : "Checkout failed");
    } finally {
      setCheckoutLoading(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-slate-900">Choose Your Plan</h1>
        <p className="text-slate-500 mt-2">Unlock advanced risk analytics for your portfolio</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {PLANS.map((plan) => {
          const isCurrent = currentTier === plan.tier;
          return (
            <div
              key={plan.tier}
              className={`relative bg-white rounded-xl border-2 p-6 flex flex-col ${
                plan.popular ? "border-blue-500 shadow-lg" : "border-slate-200"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                  Most Popular
                </span>
              )}
              <h2 className="text-xl font-bold text-slate-900">{plan.name}</h2>
              <div className="mt-4 mb-6">
                <span className="text-4xl font-bold text-slate-900">&#8377;{plan.price}</span>
                <span className="text-slate-500 text-sm">/month</span>
              </div>
              <ul className="space-y-3 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-slate-600">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleCheckout(plan.tier)}
                disabled={isCurrent || loading || checkoutLoading === plan.tier}
                className={`mt-6 w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                  isCurrent
                    ? "bg-green-100 text-green-700 cursor-default"
                    : plan.popular
                    ? "bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:opacity-50"
                }`}
              >
                {isCurrent ? "Current Plan" : checkoutLoading === plan.tier ? "Loading..." : "Get Started"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
