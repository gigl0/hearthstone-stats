import React, { useEffect, useState, useMemo } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

interface CompositionStats {
  [key: string]: { top4_rate: number };
}

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const CompositionPieChart: React.FC = () => {
  const [data, setData] = useState<CompositionStats>({});

  useEffect(() => {
    fetch(`${API_URL}/api/v1/stats/minions`)
      .then((r) => r.json())
      .then((d) => setData(d || {}))
      .catch((err) => console.error("Errore fetch minions:", err));
  }, []);

  const labels = Object.keys(data);
  const chartData = useMemo(
    () => ({
      labels,
      datasets: [
        {
          label: "Top 4 Rate %",
          data: labels.map((l) => (data[l]?.top4_rate ?? 0) * 100),
          backgroundColor: [
            "#36A2EB",
            "#FF6384",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#FF9F40",
            "#00C49F",
            "#FFB6C1",
          ],
          borderColor: "#111",
        },
      ],
    }),
    [data, labels]
  );

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Top 4 Rate per Tipo di Composizione</h3>
      {labels.length > 0 ? <Pie data={chartData} /> : <p>Nessuna composizione trovata</p>}
    </div>
  );
};
