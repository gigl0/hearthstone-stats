import React, { useEffect, useState } from "react";

interface GlobalStats {
  total_games: number;
  win_rate: number;
  top4_rate: number;
  avg_duration_min: number;
  avg_rating_delta: number;
}

export const GlobalStatsCards: React.FC = () => {
  const [stats, setStats] = useState<GlobalStats | null>(null);

  useEffect(() => {
    fetch("/api/v1/stats/global")
      .then((r) => r.json())
      .then(setStats)
      .catch(console.error);
  }, []);

  if (!stats) return <p>Caricamento statistiche...</p>;

  const cards = [
    { label: "Totale partite", value: stats.total_games },
    { label: "Win Rate", value: `${stats.win_rate.toFixed(1)}%` },
    { label: "Top 4 Rate", value: `${stats.top4_rate.toFixed(1)}%` },
    { label: "Durata media", value: `${stats.avg_duration_min.toFixed(1)} min` },
    { label: "Δ Rating medio", value: stats.avg_rating_delta.toFixed(1) },
  ];

  return (
    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
      {cards.map((c) => (
        <div
          key={c.label}
          style={{
                backgroundColor: "#1E1E1E", // sfondo scuro elegante
                color: "#F5F5F5",           // testo chiaro
                border: "1px solid #333",   // bordo sottile per definizione
                borderRadius: "12px",
                padding: "1rem",
                minWidth: "180px",
                boxShadow: "0 0 10px rgba(0,0,0,0.3)",
          }}
        >
          <h4 style={{ margin: "0 0 0.5rem" }}>{c.label}</h4>
          <strong style={{ fontSize: "1.4rem" }}>{c.value}</strong>
        </div>
      ))}
    </div>
  );
};

