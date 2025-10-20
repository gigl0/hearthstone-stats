import React, { useEffect, useState } from "react";

interface Match {
  hero_name: string;
  hero_image: string;
  placement: number;
  game_result: string;
  rating_after: number;
  rating_delta: number;
  duration_min: number;
  end_time: string;
  minions_list: string[];
  minion_images: string[];
}

interface MinionInfo {
  name: string;
  type: string;
  effect: string;
  image: string;
}

export const MatchesPage: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [minionsInfo, setMinionsInfo] = useState<Record<string, MinionInfo>>({});

  // Percorso corretto del placeholder (frontend/public/images/minions/placeholder.png)
  const placeholder = "/images/minions/placeholder.png";

  // Carica le partite
  useEffect(() => {
    fetch("/api/v1/matches/recent")
      .then((r) => r.json())
      .then((data) => setMatches(data.matches))
      .catch(console.error);
  }, []);

  // Carica info minion (solo se disponibile)
  useEffect(() => {
    fetch("/data/minions_bg.json")
      .then((r) => r.json())
      .then(setMinionsInfo)
      .catch(() => console.warn("⚠️ minions_bg.json non trovato per i tooltip"));
  }, []);

  if (matches.length === 0)
    return <p style={{ color: "#aaa" }}>Caricamento partite...</p>;

  const resultColor = (res: string) =>
    res === "win" ? "limegreen" : res === "top4" ? "gold" : "tomato";

  return (
    <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif" }}>
      <h2 style={{ color: "#fff", marginBottom: "2rem" }}>📜 Ultime 10 Partite</h2>

      {matches.map((m, idx) => (
        <div
          key={idx}
          style={{
            marginBottom: "2rem",
            background: "#1E1E1E",
            color: "#F5F5F5",
            padding: "1.5rem",
            borderRadius: "12px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)",
          }}
        >
          {/* === HEADER HERO === */}
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <img
              src={m.hero_image || placeholder}
              alt={m.hero_name}
              width={80}
              height={80}
              style={{
                borderRadius: "10px",
                border: "1px solid #333",
                background: "#222",
                objectFit: "cover",
              }}
              onError={(e) => {
                (e.target as HTMLImageElement).src = placeholder;
              }}
            />
            <div>
              <h3 style={{ margin: 0 }}>{m.hero_name}</h3>
              <p style={{ margin: "0.3rem 0", color: "#bbb" }}>
                Posizione: <strong>{m.placement}</strong> •{" "}
                <span style={{ color: resultColor(m.game_result) }}>
                  {m.game_result.toUpperCase()}
                </span>{" "}
                • Δ Rating:{" "}
                <strong
                  style={{
                    color:
                      m.rating_delta > 0
                        ? "lime"
                        : m.rating_delta < 0
                        ? "red"
                        : "#ccc",
                  }}
                >
                  {m.rating_delta > 0
                    ? `+${m.rating_delta}`
                    : m.rating_delta}
                </strong>
              </p>
              <p style={{ margin: "0.3rem 0", color: "#aaa" }}>
                Durata: {m.duration_min} min — Rating finale: {m.rating_after}
              </p>
              <p style={{ margin: "0.3rem 0", color: "#888" }}>
                Fine: {new Date(m.end_time).toLocaleString("it-IT")}
              </p>
            </div>
          </div>

          {/* === BOARD MINIONI === */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.8rem",
              marginTop: "1rem",
              justifyContent: "flex-start",
            }}
          >
            {m.minion_images.map((src, i) => {
              const minionName = m.minions_list[i];
              const minion = Object.values(minionsInfo).find(
                (min) =>
                  min.name.toLowerCase() === minionName?.toLowerCase()
              );

              // usa placeholder se src è vuoto o errato
              const validSrc =
                src && src.trim() !== "" && !src.includes("|")
                  ? src
                  : placeholder;

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    width: "80px",
                  }}
                >
                  <img
                    src={validSrc}
                    alt={minionName}
                    width={70}
                    height={70}
                    style={{
                      borderRadius: "8px",
                      border: "1px solid #444",
                      objectFit: "cover",
                      background: "#222",
                      cursor: "pointer",
                    }}
                    title={
                      minion
                        ? `${minion.name}\n${minion.type}\n${minion.effect}`
                        : "Immagine non disponibile"
                    }
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = placeholder;
                    }}
                  />
                  <p
                    style={{
                      fontSize: "0.7rem",
                      color: "#ddd",
                      textAlign: "center",
                      marginTop: "0.3rem",
                      lineHeight: "1rem",
                      height: "2rem",
                      overflow: "hidden",
                    }}
                  >
                    {minionName || "Sconosciuto"}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
