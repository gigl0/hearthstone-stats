import React, { useEffect, useState } from "react";
import { getRecentMatches } from "../api";
import { BattlegroundsMatch } from "../types";

interface CardInfo {
  name: string;
  type?: string;
  effect?: string;
  image: string;
}

export const MatchesPage: React.FC = () => {
  const [matches, setMatches] = useState<BattlegroundsMatch[]>([]);
  const [minionsInfo, setMinionsInfo] = useState<Record<string, CardInfo>>({});
  const [heroesInfo, setHeroesInfo] = useState<Record<string, CardInfo>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const placeholder = "/images/placeholder.png";

  // === Carica partite ===
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
    const interval = setInterval(loadMatches, 15000);
    return () => clearInterval(interval);
  }, []);

  // === Carica dati minion e eroi ===
  useEffect(() => {
    fetch("/minions_bg.json")
      .then((r) => r.json())
      .then((data) => setMinionsInfo(data))
      .catch(() => console.warn("⚠️ minions_bg.json non trovato"));

    fetch("/heroes_bg.json")
      .then((r) => r.json())
      .then((data) => setHeroesInfo(data))
      .catch(() => console.warn("⚠️ heroes_bg.json non trovato"));
  }, []);

  if (loading) return <p style={{ color: "#aaa" }}>Caricamento partite...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;
  if (matches.length === 0)
    return <p style={{ color: "#aaa" }}>Nessuna partita trovata.</p>;

  const resultColor = (res: string) =>
    res === "win" ? "limegreen" : res === "top4" ? "gold" : "tomato";

  return (
    <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif", color: "#f5f5f5" }}>
      <h1 style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.5rem" }}>
        📜 Ultime Partite
        <span
          title="Aggiornamento automatico ogni 15s"
          style={{ animation: "spin 15s linear infinite", fontSize: "1.3rem" }}
        >
          🔄
        </span>
      </h1>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>

      {matches.map((m, idx) => {
        const gameResult = Array.isArray(m.game_result)
          ? m.game_result[0]
          : m.game_result || "";

        const placementText =
          m.placement && m.placement > 0 ? m.placement : "⏳ In attesa...";

        // === HERO IMAGE ===
        const hero = Object.values(heroesInfo).find(
          (h: any) => h.name?.toLowerCase() === m.hero_name?.toLowerCase()
        ) as CardInfo | undefined;

        let heroImg = placeholder;
        if (hero?.image) {
          if (hero.image.startsWith("http")) heroImg = hero.image;
          else heroImg = `/images/heroes/${hero.image.split("/").pop()}`;
        } else {
          // fallback CDN
          const heroId = Object.keys(heroesInfo).find((k) =>
            k.includes(m.hero_name?.replace(/\s/g, "_") || "")
          );
          if (heroId)
            heroImg = `https://art.hearthstonejson.com/v1/render/latest/enUS/512x/${heroId}.png`;
        }


        // === MINION IMAGES ===
        const minionNames = Array.isArray(m.minions_list)
          ? m.minions_list
          : typeof m.minions_list === "string"
          ? m.minions_list.split(",").map((s) => s.trim())
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
            }}
          >
            {/* === HERO INFO === */}
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <img
                src={heroImg || placeholder}
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
                  Posizione:{" "}
                  <strong style={{ color: m.placement ? "#fff" : "#777" }}>
                    {placementText}
                  </strong>{" "}
                  •{" "}
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
                {minionNames.map((name, i) => {
                  const minion = Object.values(minionsInfo).find(
                    (min: any) =>
                      min.name?.toLowerCase() === name?.toLowerCase()
                  ) as CardInfo | undefined;

                  const src = minion?.image || placeholder;

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
                        alt={name}
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
                            ? `${minion.name}\n${minion.type || ""}\n${minion.effect || ""}`
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
                        {name || "Sconosciuto"}
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
