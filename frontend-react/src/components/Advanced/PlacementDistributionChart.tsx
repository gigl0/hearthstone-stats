import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js";
import { getDistribution } from "../../api";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export const PlacementDistributionChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    getDistribution().then(setData).catch(console.error);
  }, []);

  if (!data.length) return <p>No distribution data.</p>;

  const chartData = {
    labels: data.map((d) => `#${d.placement}`),
    datasets: [
      {
        label: "Placement %",
        data: data.map((d) => d.percentage * 100),
        backgroundColor: "#36A2EB",
      },
    ],
  };

  return (
    <div>
      <h3>Placement Distribution (1–8)</h3>
      <Bar data={chartData} />
    </div>
  );
};
