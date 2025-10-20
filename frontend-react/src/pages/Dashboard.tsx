import React, { useEffect, useState } from "react";
import { getMatches } from "../api";

// ✅ Tipi definiti per chiarezza e sicurezza
interface Match {
  hero_name: string;
  hero_image: string;
  placement: number;
  rating_after: number;
  start_time: string;
}

const Dashboard: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMatches()
      .then((data) => {
        if (Array.isArray(data)) {
          setMatches(data);
        } else {
          setError("Invalid data format received from API.");
        }
      })
      .catch((err) => {
        console.error("❌ Errore nel fetch:", err);
        setError("Failed to fetch matches.");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p style={{ color: "#ccc" }}>Loading matches...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (matches.length === 0) return <p style={{ color: "#ccc" }}>No matches found.</p>;

  return (
    <div style={{ padding: "2rem", color: "white", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ marginBottom: "1rem" }}>🏆 Your Latest Battlegrounds Matches</h1>

      <div
        style={{
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
        }}
      >
        {matches.map((m, i) => (
          <div
            key={i}
            style={{
              background: "#1e1e1e",
              padding: "1rem",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              boxShadow: "0 0 10px rgba(0,0,0,0.4)",
              transition: "transform 0.2s",
            }}
          >
            <img
              src={m.hero_image}
              alt={m.hero_name}
              width={90}
              height={90}
              style={{
                borderRadius: "10px",
                marginRight: "1rem",
                border: "2px solid #444",
              }}
            />

            <div>
              <h3 style={{ margin: "0 0 0.5rem 0", color: "#ffd700" }}>{m.hero_name}</h3>
              <p>Placement: <strong>{m.placement}</strong></p>
              <p>Rating After: <strong>{m.rating_after}</strong></p>
              <p>
                Date:{" "}
                {new Date(m.start_time).toLocaleString("en-GB", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
