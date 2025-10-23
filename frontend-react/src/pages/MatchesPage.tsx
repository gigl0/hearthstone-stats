import React, { useEffect, useState } from "react";
import { getRecentMatches } from "../api";
import { BattlegroundsMatch } from "../types";

interface MinionInfo {
  name: string;
  type: string;
  effect: string;
  image: string;
}

export const MatchesPage: React.FC = () => {
  const [matches, setMatches] = useState<BattlegroundsMatch[]>([]);
  const [minionsInfo, setMinionsInfo] = useState<Record<string, MinionInfo>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const placeholder = "/images/minions/placeholder.png";

  useEffect(() => {
    const loadMatches = async () => {
      try {
        setLoading(true);
        const data = await getRecentMatches();
        setMatches(data.matches || data);
      } catch (err) {
        console.error("❌ Errore caricamento partite:", err);
        setError("Impossibile caricare le partite dal server.");
      } finally {
        setLoading(false);
      }
    };
    loadMatches();
  }, []);

  useEffect(() => {
    fetch("/data/minions_bg.json")
      .then((r) => r.json())
      .then((data: Record<string, MinionInfo>) => setMinionsInfo(data))
      .catch(() => console.warn("⚠️ minions_bg.json non trovato per i tooltip"));
  }, []);

  if (loading) return <p style={{ color: "#aaa" }}>Caricamento partite...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;
  if (matches.length === 0)
    return <p style={{ color: "#aaa" }}>Nessuna partita trovata.</p>;

  const resultColor = (res: string) =>
    res === "win" ? "limegreen" : res === "top4" ? "gold" : "tomato";

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "Inter, sans-serif",
        color: "#f5f5f5",
      }}
    >
      <h1 style={{ marginBottom: "1.5rem" }}>📜 Ultime Partite</h1>

      {matches.map((m, idx) => {
        const gameResult: string = Array.isArray(m.game_result)
          ? m.game_result[0]
          : m.game_result || "";

          const minionNames: string[] = Array.isArray(m.minions_list)
            ? m.minions_list.filter(Boolean)
            : typeof m.minions_list === "string"
            ? (m.minions_list as string)
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean)
            : [];


        const minionImgs: string[] =
          typeof m.minion_images === "string"
            ? m.minion_images.split("|").map((s) => s.trim())
            : Array.isArray(m.minion_images)
            ? m.minion_images
            : [];

        return (
          <div
            key={m.id ?? idx}
            style={{
              marginBottom: "2rem",
              background: "#1E1E1E",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 0 12px rgba(0,0,0,0.4)",
              transition: "transform 0.2s ease",
            }}
          >
            {/* === HERO INFO === */}
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <img
                src={`/images/heroes/${m.hero_name}.png`}
                alt={m.hero_name}
                width={80}
                height={80}
                style={{
                  borderRadius: "10px",
                  border: "1px solid #333",
                  background: "#222",
                  objectFit: "cover",
                }}
                onError={(e) =>
                  ((e.target as HTMLImageElement).src = placeholder)
                }
              />
              <div>
                <h3 style={{ margin: 0 }}>{m.hero_name}</h3>
                <p style={{ margin: "0.3rem 0", color: "#bbb" }}>
                  Posizione: <strong>{m.placement}</strong> •{" "}
                  <span style={{ color: resultColor(gameResult) }}>
                    {gameResult.toUpperCase()}
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
                  <p style={{ margin: "0.3rem 0", color: "#888" }}>
                Giocata il:{" "}
                {m.end_time
                  ? new Date(m.end_time).toLocaleString("it-IT")
                  : m.date
                  ? new Date(m.date).toLocaleString("it-IT")
                  : "data sconosciuta"}
              </p>
              </div>
            </div>

            {/* === MINION BOARD === */}
            {minionNames.length > 0 && (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.8rem",
                  marginTop: "1rem",
                }}
              >
                {minionNames.map((minionName, i) => {
                  const minion = Object.values(minionsInfo || {}).find((min: any) => {
                    if (!min || !min.name || !minionName) return false;
                    return min.name.toLowerCase() === minionName.toLowerCase();
                  }) as MinionInfo | undefined;

                  const src =
                    minionImgs[i]?.trim() ||
                    minion?.image ||
                    placeholder;

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
                        src={src}
                        alt={minionName}
                        width={70}
                        height={70}
                        style={{
                          borderRadius: "8px",
                          border: "1px solid #444",
                          background: "#222",
                          objectFit: "cover",
                        }}
                        title={
                          minion
                            ? `${minion.name}\n${minion.type}\n${minion.effect}`
                            : "Immagine non disponibile"
                        }
                        onError={(e) =>
                          ((e.target as HTMLImageElement).src = placeholder)
                        }
                      />
                      <p
                        style={{
                          fontSize: "0.7rem",
                          color: "#ddd",
                          textAlign: "center",
                          marginTop: "0.3rem",
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
            )}
          </div>
        );
      })}

      <button
        onClick={() => window.history.back()}
        style={{
          marginTop: "1rem",
          padding: "0.7rem 1.2rem",
          borderRadius: "8px",
          border: "none",
          backgroundColor: "#3b82f6",
          color: "#fff",
          fontWeight: "bold",
          cursor: "pointer",
        }}
      >
        ⬅️ Torna alla Dashboard
      </button>
    </div>
  );
};
