import React, { useEffect, useState } from "react";
import { getMatchDuration } from "../../api";

interface MatchDurationStats {
  avg_duration_min: number;
  min_duration_min: number;
  max_duration_min: number;
}

export const MatchDurationCard: React.FC = () => {
  const [stats, setStats] = useState<MatchDurationStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDuration = async () => {
      try {
        const res = await getMatchDuration();
        setStats(res);
      } catch (err) {
        console.error("❌ Errore caricamento durata partite:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDuration();
  }, []);

  if (loading) return <p style={{ color: "#aaa" }}>Loading match duration...</p>;

  if (!stats)
    return <p style={{ color: "#aaa" }}>No duration data available.</p>;

  return (
    <div
      style={{
        background: "#1E1E1E",
        padding: "1.2rem",
        borderRadius: "10px",
        color: "#ccc",
        marginBottom: "1rem",
      }}
    >
      <h3 style={{ color: "#fff", marginBottom: "0.8rem" }}>Match Duration</h3>
      <p>Average: {stats.avg_duration_min?.toFixed(1)} min</p>
      <p>Shortest: {stats.min_duration_min?.toFixed(1)} min</p>
      <p>Longest: {stats.max_duration_min?.toFixed(1)} min</p>
    </div>
  );
};
