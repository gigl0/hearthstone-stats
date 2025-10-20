import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Legend, Tooltip);

interface HeroStats {
  hero_name: string;
  win_rate: number;
  top4_rate: number;
}

export const HeroStatsChart: React.FC = () => {
  const [data, setData] = useState<HeroStats[]>([]);

  useEffect(() => {
    fetch("/api/v1/stats/heroes")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  const chartData = {
    labels: data.map((h) => h.hero_name),
    datasets: [
      {
        label: "Win Rate %",
        data: data.map((h) => h.win_rate),
        backgroundColor: "rgba(75,192,192,0.6)",
      },
      {
        label: "Top 4 Rate %",
        data: data.map((h) => h.top4_rate),
        backgroundColor: "rgba(153,102,255,0.6)",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: "bottom" as const } },
    scales: { y: { beginAtZero: true } },
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Winrate e Top 4 Rate per Eroe</h3>
      <Bar data={chartData} options={options} />
    </div>
  );
};
