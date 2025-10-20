import React, { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export const CompositionPieChart: React.FC = () => {
  const [data, setData] = useState<any>({});

  useEffect(() => {
    fetch("/api/v1/stats/minions")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  const labels = Object.keys(data);
  const chartData = {
    labels,
    datasets: [
      {
        data: labels.map((l) => data[l].top4_rate),
        backgroundColor: [
          "#36A2EB",
          "#FF6384",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
      },
    ],
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Top 4 Rate per Tipo di Composizione</h3>
      <Pie data={chartData} />
    </div>
  );
};
