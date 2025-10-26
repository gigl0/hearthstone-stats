import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from "chart.js";
import { getStreaks } from "../../api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export const StreaksChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    getStreaks().then(setData).catch(console.error);
  }, []);

  if (!data.length) return <p>No streak data available.</p>;

  const chartData = {
    labels: data.map((d) => d.match_id || ""),
    datasets: [
      {
        label: "Win Streaks",
        data: data.map((d) => d.streak_length),
        borderColor: "#4CAF50",
        tension: 0.2,
      },
    ],
  };

  return (
    <div>
      <h3>Winning Streaks</h3>
      <Line data={chartData} />
    </div>
  );
};
