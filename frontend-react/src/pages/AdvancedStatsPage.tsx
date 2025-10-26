import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  BarChart,
  Bar,
  ResponsiveContainer,
} from "recharts";
import {
  getStreaks,
  getDistribution,
  getMatchDuration,
  getEloProgression,
} from "../api";

// === Tipi ===
interface EloPoint {
  date: string;
  rating: number;
}

interface DistributionItem {
  placement: string;
  percentage: number;
}

interface MatchDuration {
  avg_duration: number;
  min_duration: number;
  max_duration: number;
}

// === COMPONENTE PRINCIPALE ===
export const AdvancedStatsPage: React.FC = () => {
  const [streaks, setStreaks] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<DistributionItem[]>([]);
  const [durations, setDurations] = useState<MatchDuration | null>(null);
  const [elo, setElo] = useState<EloPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [streakData, distData, durationData, eloData] = await Promise.all([
          getStreaks(),
          getDistribution(),
          getMatchDuration(),
          getEloProgression(),
        ]);

        // === Winning Streaks ===
        setStreaks(
          Array.isArray(streakData)
            ? streakData.map((s) => ({
                streak: s.streak_length,
                count: s.count,
              }))
            : []
        );

        // === Placement Distribution ===
        const parsedDist = Object.values(distData || {}).map((item: any) => ({
          placement: `#${item.placement}`,
          percentage: item.percentage * 100, // percentuale %
        }));
        setDistribution(parsedDist);

        // === Match Duration ===
        setDurations(durationData || null);

        // === ELO Progression ===
        setElo(
  Array.isArray(eloData)
    ? eloData.map((p) => ({
        date: new Date(p.time).toLocaleDateString("it-IT", {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        }),
        rating: p.rating ?? 0,
        diff: p.diff ?? 0,
      }))
    : []
);

      } catch (err) {
        console.error("❌ Errore caricamento dati advanced stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  if (loading) {
    return <p style={{ color: "#aaa" }}>Loading advanced stats...</p>;
  }

  return (
    <div style={{ padding: "1rem" }}>
      <h2 style={{ color: "#fff", marginBottom: "1.5rem" }}>Advanced Stats</h2>

      {/* === Winning Streaks === */}
      <section style={sectionStyle}>
        <h3 style={titleStyle}>Winning Streaks</h3>
        {streaks.length === 0 ? (
          <p style={noDataStyle}>No data available.</p>
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={streaks}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="streak" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend />
              <Bar dataKey="count" fill="#00FF7F" name="Win Streaks" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      {/* === Placement Distribution === */}
      <section style={sectionStyle}>
        <h3 style={titleStyle}>Placement Distribution (1–8)</h3>
        {distribution.length === 0 ? (
          <p style={noDataStyle}>No data available.</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="placement" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend />
              <Bar dataKey="percentage" fill="#1E90FF" name="Placement %" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      {/* === Match Duration === */}
      <section style={sectionStyle}>
        <h3 style={titleStyle}>Match Duration</h3>
        {durations ? (
          <div style={durationBoxStyle}>
            <p>
              Average:{" "}
              {durations.avg_duration
                ? durations.avg_duration.toFixed(1)
                : "-"}{" "}
              min
            </p>
            <p>
              Shortest:{" "}
              {durations.min_duration
                ? durations.min_duration.toFixed(1)
                : "-"}{" "}
              min
            </p>
            <p>
              Longest:{" "}
              {durations.max_duration
                ? durations.max_duration.toFixed(1)
                : "-"}{" "}
              min
            </p>
          </div>
        ) : (
          <p style={noDataStyle}>No duration data available.</p>
        )}
      </section>

      
    {/* === ELO Progression === */}
<section style={sectionStyle}>
  <h3 style={titleStyle}>ELO Progression</h3>
  {elo.length === 0 ? (
    <p style={noDataStyle}>No ELO data available.</p>
  ) : (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={elo}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis dataKey="date" stroke="#ccc" />
        <YAxis stroke="#ccc" domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e1e1e",
            border: "1px solid #333",
            borderRadius: "6px",
            color: "#fff",
          }}
          formatter={(value: any, name: any, props: any) => {
            const diff = props.payload.diff ?? 0;
            const sign = diff > 0 ? "+" : "";
            return [`${value} (${sign}${diff})`, "Rating"];
          }}
          labelStyle={{ color: "#FFD700" }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="rating"
          stroke="#FFD700"
          strokeWidth={2}
          dot={{ r: 2 }}
          activeDot={{ r: 4, fill: "#fff" }}
          name="ELO Progression"
        />
      </LineChart>
    </ResponsiveContainer>
  )}
</section>
    </div>
  );
};

// === STYLE OBJECTS ===
const sectionStyle: React.CSSProperties = {
  backgroundColor: "#1b1b1b",
  borderRadius: "10px",
  padding: "1rem",
  marginBottom: "2rem",
  boxShadow: "0 0 8px rgba(255,255,255,0.05)",
};

const titleStyle: React.CSSProperties = {
  color: "#fff",
  marginBottom: "1rem",
  fontSize: "1.1rem",
};

const noDataStyle: React.CSSProperties = {
  color: "#888",
  fontStyle: "italic",
};

const tooltipStyle: React.CSSProperties = {
  backgroundColor: "#222",
  border: "1px solid #444",
  color: "#fff",
};

const durationBoxStyle: React.CSSProperties = {
  display: "flex",
  gap: "2rem",
  justifyContent: "space-around",
  color: "#ccc",
  backgroundColor: "#222",
  padding: "1rem",
  borderRadius: "8px",
};
