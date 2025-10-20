import React, { useEffect, useState } from "react";

interface GlobalStats {
  total_games: number;
  win_rate: number;
  top4_rate: number;
  avg_duration_min: number;
  avg_rating_delta: number;
}

function App() {
  const [stats, setStats] = useState<GlobalStats | null>(null);

  useEffect(() => {
    fetch("/api/v1/stats/global")
      .then((res) => res.json())
      .then(setStats)
      .catch((err) => console.error("Errore nel fetch:", err));
  }, []);

  return (
    <div style={{ fontFamily: "Inter, sans-serif", padding: "2rem" }}>
      <h1>🔥 Hearthstone Battlegrounds Stats Dashboard</h1>

      {stats ? (
        <div>
          <h2>Statistiche Globali</h2>
          <ul>
            <li>Totale partite: {stats.total_games}</li>
            <li>Win Rate: {stats.win_rate.toFixed(2)}%</li>
            <li>Top4 Rate: {stats.top4_rate.toFixed(2)}%</li>
            <li>Durata media: {stats.avg_duration_min.toFixed(1)} min</li>
            <li>Δ Rating medio: {stats.avg_rating_delta.toFixed(1)}</li>
          </ul>
        </div>
      ) : (
        <p>Caricamento dati...</p>
      )}
    </div>
  );
}

export default App;
