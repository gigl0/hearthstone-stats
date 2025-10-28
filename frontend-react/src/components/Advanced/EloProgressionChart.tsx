import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { getEloProgression } from "../../api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface EloEntry {
  end_time: string;
  rating_after: number;
}

export const EloProgressionChart: React.FC = () => {
  const [data, setData] = useState<EloEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchElo = async () => {
      try {
        const res = await getEloProgression();
        if (Array.isArray(res)) {
          // Filtra record validi
          const cleanData = res
            .filter((d) => d.rating_after && d.end_time)
            .map((d) => ({
              end_time: new Date(d.end_time).toLocaleDateString("it-IT"),
              rating_after: Number(d.rating_after),
            }));
          setData(cleanData);
        }
      } catch (err) {
        console.error("❌ Errore caricamento ELO progression:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchElo();
  }, []);

  if (loading) return <p style={{ color: "#aaa" }}>Loading ELO progression...</p>;
  if (!data.length)
    return <p style={{ color: "#aaa" }}>No ELO data available.</p>;

  const chartData = {
    labels: data.map((d) => d.end_time),
    datasets: [
      {
        label: "ELO Progression",
        data: data.map((d) => d.rating_after),
        borderColor: "#FFD700",
        backgroundColor: "rgba(255, 215, 0, 0.3)",
        tension: 0.3,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    plugins: {
      legend: { labels: { color: "#ccc" } },
      tooltip: { mode: "index" as const, intersect: false },
    },
    scales: {
      x: { ticks: { color: "#aaa" }, grid: { color: "#333" } },
      y: { ticks: { color: "#aaa" }, grid: { color: "#333" } },
    },
  };

  return (
    <div
      style={{
        background: "#1E1E1E",
        padding: "1.2rem",
        borderRadius: "10px",
        color: "#ccc",
      }}
    >
      <h3 style={{ color: "#fff", marginBottom: "0.8rem" }}>ELO Progression</h3>
      <Line data={chartData} options={chartOptions} />
    </div>
    
  );
};
