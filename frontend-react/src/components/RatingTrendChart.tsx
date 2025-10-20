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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface TrendPoint {
  end_time: string;
  rating_after: number;
}

export const RatingTrendChart: React.FC = () => {
  const [data, setData] = useState<TrendPoint[]>([]);

  useEffect(() => {
    fetch("/api/v1/stats/rating_trend")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (data.length === 0) {
    return <p>Caricamento trend rating...</p>;
  }

  // Genera array di colori per ogni segmento
  const segmentColors = data.map((point, i) => {
    if (i === 0) return "#36A2EB"; // primo punto blu
    const diff = point.rating_after - data[i - 1].rating_after;
    return diff >= 0 ? "#4CAF50" : "#E53935"; // verde se guadagni, rosso se perdi
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
        fill: false,
        borderColor: (ctx: any) => {
          const index = ctx.p0DataIndex;
          return segmentColors[index] || "#36A2EB";
        },
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 8,
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
      y: {
        beginAtZero: false,
        title: { display: true, text: "Rating" },
      },
    },
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Andamento del Rating nel Tempo</h3>
      <Line data={chartData} options={options} />
    </div>
  );
};
