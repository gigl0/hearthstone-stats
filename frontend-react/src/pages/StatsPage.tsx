import React, { useEffect, useState } from "react";
import { getGlobalStats, getHeroStats, getTrendStats } from "../api";
import { GlobalStats, HeroStats, TrendPoint } from "../types";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export const StatsPage: React.FC = () => {
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [heroStats, setHeroStats] = useState<HeroStats[]>([]);
  const [trendStats, setTrendStats] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // === Carica tutte le statistiche ===
  const loadStats = async () => {
    try {
      setLoading(true);
      const [global, heroes, trend] = await Promise.all([
        getGlobalStats(),
        getHeroStats(),
        getTrendStats(),
      ]);
      setGlobalStats(global);
      setHeroStats(heroes || []);
      setTrendStats(trend || []);
      setError(null);
    } catch (err) {
      console.error("❌ Errore nel caricamento delle statistiche:", err);
      setError("Impossibile caricare le statistiche dal server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) return <p style={{ color: "#aaa" }}>Caricamento statistiche...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;

  return (
    <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif", color: "#F5F5F5" }}>
      <h2 style={{ color: "#fff", marginBottom: "1.5rem" }}>📊 Statistiche Generali</h2>

      {/* === GLOBAL STATS === */}
      {globalStats && (
        <div
          style={{
            background: "#1E1E1E",
            padding: "1.5rem",
            borderRadius: "12px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)",
            marginBottom: "2rem",
          }}
        >
          <p>
            Totale partite: <strong>{globalStats.total_matches ?? 0}</strong>
          </p>
          <p>
            Posizione media:{" "}
            <strong>{globalStats?.avg_placement?.toFixed(2) ?? "-"}</strong>
          </p>
          <p>
            Top 4 rate:{" "}
            <strong>
              {globalStats?.top4_rate != null
                ? (globalStats.top4_rate * 100).toFixed(1) + "%"
                : "-"}
            </strong>
          </p>
          <p>
            Win rate:{" "}
            <strong style={{ color: "limegreen" }}>
              {globalStats?.win_rate != null
                ? (globalStats.win_rate * 100).toFixed(1) + "%"
                : "-"}
            </strong>
          </p>
          {globalStats.last_update && (
            <p style={{ color: "#888" }}>
              Ultimo aggiornamento:{" "}
              {new Date(globalStats.last_update).toLocaleString("it-IT")}
            </p>
          )}

          {/* 🔁 Bottone aggiornamento */}
          <button
            onClick={async () => {
              setRefreshing(true);
              await loadStats();
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
            {refreshing ? "⏳ Aggiornamento..." : "🔄 Aggiorna Statistiche"}
          </button>
        </div>
      )}

      {/* === HERO STATS TABLE === */}
      <h3 style={{ marginTop: "2rem", marginBottom: "1rem" }}>🧙‍♂️ Eroi più giocati</h3>
      <div
        style={{
          background: "#1E1E1E",
          padding: "1rem",
          borderRadius: "12px",
          boxShadow: "0 0 8px rgba(0,0,0,0.3)",
          overflowX: "auto",
        }}
      >
        {heroStats.length > 0 ? (
          <table
            style={{ width: "100%", borderCollapse: "collapse", color: "#eee" }}
          >
            <thead style={{ borderBottom: "1px solid #333" }}>
              <tr>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Eroe</th>
                <th style={{ textAlign: "center", padding: "0.5rem" }}>
                  Posizione Media
                </th>
                <th style={{ textAlign: "center", padding: "0.5rem" }}>
                  Pick Rate
                </th>
                <th style={{ textAlign: "center", padding: "0.5rem" }}>
                  Win Rate
                </th>
              </tr>
            </thead>
            <tbody>
              {heroStats.map((h, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #2a2a2a" }}>
                  <td style={{ padding: "0.5rem" }}>{h.hero_name || "Sconosciuto"}</td>
                  <td style={{ textAlign: "center" }}>
                    {h.average_placement != null
                      ? h.average_placement.toFixed(2)
                      : "-"}
                  </td>
                  <td style={{ textAlign: "center" }}>
                    {h.pick_rate != null ? (h.pick_rate * 100).toFixed(1) + "%" : "-"}
                  </td>
                  <td style={{ textAlign: "center", color: "limegreen" }}>
                    {h.win_rate != null ? (h.win_rate * 100).toFixed(1) + "%" : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "#aaa" }}>Nessun dato eroe disponibile.</p>
        )}
      </div>

      {/* === TREND CHART === */}
      <h3 style={{ marginTop: "2rem", marginBottom: "1rem" }}>
        📈 Andamento nel tempo
      </h3>
      <div
        style={{
          background: "#1E1E1E",
          padding: "1rem",
          borderRadius: "12px",
          boxShadow: "0 0 8px rgba(0,0,0,0.3)",
          height: 300,
        }}
      >
        {trendStats.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendStats}>
              <CartesianGrid stroke="#333" />
              <XAxis dataKey="date" tick={{ fill: "#aaa" }} />
              <YAxis tick={{ fill: "#aaa" }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#222", border: "1px solid #555" }}
                labelStyle={{ color: "#fff" }}
              />
              <Line
                type="monotone"
                dataKey="avg_placement"
                stroke="#61dafb"
                name="Posizione Media"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="win_rate"
                stroke="limegreen"
                name="Win Rate"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: "#aaa" }}>Dati trend non disponibili.</p>
        )}
      </div>
    </div>
  );
};
