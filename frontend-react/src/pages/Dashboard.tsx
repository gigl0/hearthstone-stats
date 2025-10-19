import React, { useEffect, useState } from "react";
import { getMatches } from "../api";

interface Match {
  hero_name: string;
  hero_image: string;
  placement: number;
  rating_after: number;
  start_time: string;
}

function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMatches()
      .then((data) => setMatches(data))
      .catch((err) => console.error("Errore nel fetch:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading matches...</p>;
  if (matches.length === 0) return <p>No matches found.</p>;

  return (
    <div style={{ padding: "1rem" }}>
      <h1>🏆 Your Latest Battlegrounds Matches</h1>
      <div style={{ display: "grid", gap: "1rem" }}>
        {matches.map((m, i) => (
          <div
            key={i}
            style={{
              background: "#222",
              padding: "1rem",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              gap: "1rem",
            }}
          >
            <img
              src={m.hero_image}
              alt={m.hero_name}
              width={80}
              height={80}
              style={{ borderRadius: "10px" }}
            />
            <div>
              <h3>{m.hero_name}</h3>
              <p>Placement: {m.placement}</p>
              <p>Rating: {m.rating_after}</p>
              <p>
                Date: {new Date(m.start_time).toLocaleDateString()}{" "}
                {new Date(m.start_time).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
