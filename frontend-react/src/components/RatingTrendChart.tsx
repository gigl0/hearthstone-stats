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

// ⚙️ Registrazione componenti Chart.js (obbligatoria con CRA)
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface TrendPoint {
  end_time: string;
  rating_after: number;
}

export const RatingTrendChart: React.FC = () => {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log("✅ RatingTrendChart montato");
    const fetchTrend = async () => {
      try {
        console.log("📡 Fetching /api/v1/stats/rating_trend ...");
        const res = await fetch("/api/v1/stats/rating_trend");
        const json = await res.json();
        console.log("✅ Dati ricevuti:", json);
        setData(json);
      } catch (err) {
        console.error("❌ Errore fetch rating trend:", err);
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

  // 🎨 Colori dinamici
  const segmentColors = data.map((point, i) => {
    if (i === 0) return "#36A2EB";
    const diff = point.rating_after - data[i - 1].rating_after;
    return diff >= 0 ? "#4CAF50" : "#E53935";
  });

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
        pointBackgroundColor: segmentColors,
        fill: false,
        tension: 0.2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "bottom" as const },
      tooltip: {
        callbacks: {
          label: function (ctx: any) {
            const prev = ctx.dataset.data[ctx.dataIndex - 1];
            const delta = prev ? ctx.parsed.y - prev : 0;
            const sign = delta > 0 ? "+" : "";
            return `Rating: ${ctx.parsed.y} (${sign}${delta})`;
          },
        },
      },
    },
    scales: {
      x: { ticks: { color: "#aaa" } },
      y: {
        ticks: { color: "#aaa" },
        title: { display: true, text: "Rating", color: "#ccc" },
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
        📈 Andamento del Rating nel Tempo
      </h3>
      <Line data={chartData} options={options} />
    </div>
  );
};
