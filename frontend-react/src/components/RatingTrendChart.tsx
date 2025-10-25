import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface TrendPoint {
  end_time: string;
  rating_after: number;
}

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const RatingTrendChart: React.FC = () => {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/stats/rating_trend`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Errore fetch rating trend:", err);
        setError("Errore nel caricamento dei dati");
      } finally {
        setLoading(false);
      }
    };
    fetchTrend();
  }, []);

  if (loading) return <p style={{ color: "#ccc" }}>Caricamento trend rating...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;
  if (!data.length) return <p style={{ color: "#ccc" }}>Nessun dato disponibile.</p>;

  const chartData = {
    labels: data.map((d) =>
      new Date(d.end_time).toLocaleString("it-IT", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    ),
    datasets: [
      {
        label: "Rating nel tempo",
        data: data.map((d) => Number(d.rating_after)),
        borderColor: "#4CAF50",
        borderWidth: 2,
        fill: false,
        tension: 0.2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: "bottom" as const } },
    scales: { x: { ticks: { color: "#aaa" } }, y: { ticks: { color: "#aaa" } } },
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>📈 Andamento del Rating nel Tempo</h3>
      <Line data={chartData} options={options} />
    </div>
  );
};
