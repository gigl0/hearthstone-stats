import React, { useEffect, useState } from "react";
import { getImportLogs, getSyncStatus } from "../api";
import { ImportLog, SyncStatus } from "../types";

export const ImportLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<ImportLog[]>([]);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // === Carica log e stato sincronizzazione ===
  const loadData = async () => {
    try {
      setLoading(true);
      const [importLogs, sync] = await Promise.all([
        getImportLogs(),
        getSyncStatus(),
      ]);

      // Ordina i log dal più recente al più vecchio
      const sortedLogs = [...(importLogs || [])].sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      setLogs(sortedLogs);
      setSyncStatus(sync);
      setError(null);
    } catch (err) {
      console.error("❌ Errore nel caricamento dei log:", err);
      setError("Impossibile caricare i log di importazione.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // === Funzione colore in base allo stato ===
  const getStatusColor = (status?: string) => {
    switch ((status || "").toUpperCase()) {
      case "SUCCESS":
        return "limegreen";
      case "FAILURE":
        return "tomato";
      case "RUNNING":
        return "gold";
      default:
        return "#ccc";
    }
  };

  // === Stati ===
  if (loading) return <p style={{ color: "#aaa" }}>Caricamento log...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;

  // === RENDER ===
  return (
    <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif" }}>
      <h2 style={{ color: "#fff", marginBottom: "1.5rem" }}>🧩 Log Importazioni</h2>

      {/* === STATO SINCRONIZZAZIONE === */}
      {syncStatus && (
        <div
          style={{
            background: "#1E1E1E",
            padding: "1.2rem 1.5rem",
            borderRadius: "12px",
            marginBottom: "2rem",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)",
          }}
        >
          <p>
            Ultimo import:{" "}
            <strong>
              {syncStatus.last_import_time
                ? new Date(syncStatus.last_import_time).toLocaleString("it-IT")
                : "N/A"}
            </strong>
          </p>
          <p style={{ color: "#aaa" }}>
            Stato:{" "}
            <strong style={{ color: getStatusColor(syncStatus.last_status) }}>
              {syncStatus.last_status || "N/D"}
            </strong>
          </p>

          {/* 🔁 Bottone aggiornamento */}
          <button
            onClick={async () => {
              setRefreshing(true);
              await loadData();
              setRefreshing(false);
            }}
            disabled={refreshing}
            style={{
              marginTop: "0.8rem",
              padding: "0.6rem 1rem",
              border: "none",
              borderRadius: "8px",
              backgroundColor: refreshing ? "#555" : "#3b82f6",
              color: "#fff",
              cursor: refreshing ? "not-allowed" : "pointer",
              fontWeight: "bold",
              transition: "background 0.2s ease",
            }}
          >
            {refreshing ? "⏳ Aggiornamento..." : "🔄 Aggiorna Log"}
          </button>
        </div>
      )}

      {/* === TABELLA LOG === */}
      <div
        style={{
          background: "#1E1E1E",
          padding: "1rem",
          borderRadius: "12px",
          boxShadow: "0 0 10px rgba(0,0,0,0.4)",
        }}
      >
        {logs.length > 0 ? (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              color: "#eee",
            }}
          >
            <thead style={{ borderBottom: "1px solid #333" }}>
              <tr>
                <th style={{ textAlign: "left", padding: "0.6rem" }}>Data</th>
                <th style={{ textAlign: "center", padding: "0.6rem" }}>
                  Partite Importate
                </th>
                <th style={{ textAlign: "center", padding: "0.6rem" }}>Stato</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid #2a2a2a" }}>
                  <td style={{ padding: "0.5rem" }}>
                    {log.timestamp
                      ? new Date(log.timestamp).toLocaleString("it-IT")
                      : "N/A"}
                  </td>
                  <td style={{ textAlign: "center" }}>
                    {log.matches_imported ?? "-"}
                  </td>
                  <td
                    style={{
                      textAlign: "center",
                      color: getStatusColor(log.status),
                      fontWeight: "bold",
                    }}
                  >
                    {log.status || "N/D"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "#aaa" }}>Nessun log di import trovato.</p>
        )}
      </div>
    </div>
  );
};
