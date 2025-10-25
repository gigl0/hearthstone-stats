import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface HeroStats {
  hero: string;
  win_rate: number;
  top4_rate: number;
}

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const HeroStatsChart: React.FC = () => {
  const [data, setData] = useState<HeroStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHeroes = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/stats/heroes`);
        if (!res.ok) throw new Error(`Errore API ${res.status}`);
        const json = await res.json();
        setData(json || []);
        setError(null);
      } catch (err) {
        console.error("❌ Errore fetch heroes:", err);
        setError("Errore nel caricamento dei dati eroi");
      } finally {
        setLoading(false);
      }
    };
    fetchHeroes();
  }, []);

  if (loading) return <p style={{ color: "#ccc" }}>Caricamento dati eroi...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;
  if (!data.length) return <p style={{ color: "#ccc" }}>Nessun dato disponibile.</p>;

  // Prepara i dati per il grafico
  const labels = data.map((d) => d.hero);
  const chartData = {
    labels,
    datasets: [
      {
        label: "Win Rate (%)",
        data: data.map((d) => (d.win_rate ?? 0) * 100),
        backgroundColor: "#4CAF50",
      },
      {
        label: "Top 4 Rate (%)",
        data: data.map((d) => (d.top4_rate ?? 0) * 100),
        backgroundColor: "#2196F3",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "bottom" as const },
      title: {
        display: true,
        text: "Winrate e Top 4 Rate per Eroe",
        color: "#fff",
        font: { size: 16 },
      },
    },
    scales: {
      x: {
        ticks: { color: "#aaa", autoSkip: false },
      },
      y: {
        ticks: { color: "#aaa", callback: (v: any) => `${v}%` },
        beginAtZero: true,
      },
    },
  };

  return (
    <div
      style={{
        marginTop: "2rem",
        background: "#1E1E1E",
        padding: "1rem",
        borderRadius: "10px",
      }}
    >
      <h3 style={{ color: "#fff", marginBottom: "1rem" }}>
        🧙‍♂️ Winrate e Top 4 Rate per Eroe
      </h3>
      <Bar data={chartData} options={options} />
    </div>
  );
};
