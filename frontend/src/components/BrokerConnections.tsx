"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { BrokerConnection, BrokerInfo } from "@/lib/types";

interface BrokerConnectionsProps {
  onSynced?: () => void;
}

export default function BrokerConnections({ onSynced }: BrokerConnectionsProps) {
  const [connections, setConnections] = useState<BrokerConnection[]>([]);
  const [brokers, setBrokers] = useState<BrokerInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [connRes, brokerRes] = await Promise.all([
        api.listConnections(),
        api.listBrokers(),
      ]);
      setConnections(connRes.connections);
      setBrokers(brokerRes.brokers);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load broker data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const connectZerodha = async () => {
    try {
      const res = await api.getZerodhaLoginUrl();
      window.location.href = res.login_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to get Zerodha login URL");
    }
  };

  const syncConnection = async (id: string) => {
    setSyncingId(id);
    setError("");
    try {
      await api.syncConnection(id);
      await load();
      onSynced?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncingId(null);
    }
  };

  const disconnectBroker = async (id: string) => {
    try {
      await api.deleteConnection(id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to disconnect");
    }
  };

  const hasZerodhaApi = brokers.some((b) => b.name === "zerodha" && b.supports_api);
  const isZerodhaConnected = connections.some((c) => c.broker_name === "zerodha");

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="animate-pulse flex items-center gap-2">
          <div className="w-4 h-4 bg-slate-200 rounded" />
          <div className="h-4 bg-slate-200 rounded w-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Broker Connections</h3>
        {hasZerodhaApi && !isZerodhaConnected && (
          <button
            onClick={connectZerodha}
            className="px-3 py-1.5 bg-orange-500 text-white text-xs font-medium rounded-lg hover:bg-orange-600 transition-colors"
          >
            Connect Zerodha
          </button>
        )}
      </div>

      {error && (
        <div className="mx-4 mt-3 p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-500 hover:text-red-700 font-bold ml-2">&times;</button>
        </div>
      )}

      {connections.length === 0 ? (
        <div className="p-4 text-center text-sm text-slate-400">
          No broker accounts connected.
          {hasZerodhaApi && " Connect Zerodha to auto-sync your holdings."}
        </div>
      ) : (
        <div className="divide-y divide-slate-50">
          {connections.map((conn) => (
            <div key={conn.id} className="p-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-900 capitalize">{conn.broker_name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${conn.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                    {conn.is_active ? "Active" : "Expired"}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {conn.last_synced_at
                    ? `Last synced: ${new Date(conn.last_synced_at).toLocaleString()}`
                    : "Never synced"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {conn.is_active && (
                  <button
                    onClick={() => syncConnection(conn.id)}
                    disabled={syncingId === conn.id}
                    className="px-3 py-1.5 text-xs font-medium text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 disabled:opacity-50 transition-colors"
                  >
                    {syncingId === conn.id ? "Syncing..." : "Sync Now"}
                  </button>
                )}
                <button
                  onClick={() => disconnectBroker(conn.id)}
                  className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                >
                  Disconnect
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
