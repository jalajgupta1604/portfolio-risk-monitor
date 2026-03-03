"use client";

import { Suspense, useEffect, useState, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

function ZerodhaCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const calledRef = useRef(false);

  useEffect(() => {
    if (calledRef.current) return;
    calledRef.current = true;

    const requestToken = searchParams.get("request_token");
    if (!requestToken) {
      setStatus("error");
      setErrorMsg("Missing request_token in callback URL");
      return;
    }

    api
      .zerodhaCallback(requestToken)
      .then(() => {
        setStatus("success");
        setTimeout(() => router.push("/portfolios"), 2000);
      })
      .catch((e) => {
        setStatus("error");
        setErrorMsg(e instanceof Error ? e.message : "Callback failed");
      });
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="bg-white rounded-xl border border-slate-200 p-8 max-w-md w-full text-center">
        {status === "loading" && (
          <>
            <div className="animate-spin w-10 h-10 border-3 border-orange-500 border-t-transparent rounded-full mx-auto" />
            <p className="mt-4 text-slate-600">Connecting your Zerodha account...</p>
          </>
        )}
        {status === "success" && (
          <>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="mt-4 text-slate-900 font-semibold">Zerodha Connected!</p>
            <p className="mt-1 text-sm text-slate-500">Redirecting to portfolios...</p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="mt-4 text-slate-900 font-semibold">Connection Failed</p>
            <p className="mt-1 text-sm text-red-600">{errorMsg}</p>
            <button
              onClick={() => router.push("/portfolios")}
              className="mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
            >
              Back to Portfolios
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function ZerodhaCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin w-10 h-10 border-3 border-orange-500 border-t-transparent rounded-full" />
      </div>
    }>
      <ZerodhaCallbackContent />
    </Suspense>
  );
}
