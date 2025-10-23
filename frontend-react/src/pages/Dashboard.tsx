import React, { useEffect, useState } from "react";
import {
  getGlobalStats,
  getSyncStatus,
  getImportLogs,
  getTrendStats,
  triggerImport,
} from "../api";
import { GlobalStats, SyncStatus, ImportLog, TrendPoint } from "../types";
import { useNavigate } from "react-router-dom";
import toast, { Toaster } from "react-hot-toast";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// === Componenti secondari ===
import { HeroStatsChart } from "../components/HeroStatsChart";
import { CompositionPieChart } from "../components/CompositionPieChart";
import { RatingTrendChart } from "../components/RatingTrendChart";

console.log("✅ Dashboard.tsx caricato");

export const Dashboard: React.FC = () => {
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [lastImport, setLastImport] = useState<ImportLog | null>(null);
  const [trendStats, setTrendStats] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    console.log("📊 Caricamento dashboard...");
    const loadDashboard = async () => {
      try {
        setLoading(true);
        const [global, sync, logs, trend] = await Promise.all([
          getGlobalStats(),
          getSyncStatus(),
          getImportLogs(),
          getTrendStats(),
        ]);
        console.log("✅ Dati ricevuti:", { global, sync, logs, trend });
        setGlobalStats(global);
        setSyncStatus(sync);
        setLastImport(logs.length > 0 ? logs[0] : null);
        setTrendStats(trend.slice(-10));
      } catch (err) {
        console.error("❌ Errore caricamento dashboard:", err);
        setError("Impossibile caricare i dati della dashboard.");
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const formatPercent = (v: number) => `${(v * 100).toFixed(1)}%`;

  const statusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case "SUCCESS":
        return "limegreen";
      case "FAILURE":
        return "tomato";
      case "RUNNING":
        return "gold";
      default:
        return "#aaa";
    }
  };

  const handleManualImport = async () => {
    try {
      setImporting(true);
      toast.loading("Avvio importazione in corso...", { id: "import-toast" });
      await triggerImport();

      toast.success("✅ Importazione avviata con successo!", { id: "import-toast" });

      setTimeout(async () => {
        const sync = await getSyncStatus();
        const logs = await getImportLogs();
        setSyncStatus(sync);
        setLastImport(logs.length > 0 ? logs[0] : null);
        setImporting(false);
      }, 3000);
    } catch (err) {
      console.error("❌ Errore avvio import manuale:", err);
      toast.error("❌ Errore durante l'importazione.", { id: "import-toast" });
      setImporting(false);
    }
  };

  if (loading) return <p style={{ color: "#aaa" }}>Caricamento dashboard...</p>;
  if (error) return <p style={{ color: "tomato" }}>{error}</p>;

  return (
    <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif", color: "#F5F5F5" }}>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: "#1E1E1E",
            color: "#fff",
            borderRadius: "8px",
            border: "1px solid #333",
          },
        }}
      />

      <h1 style={{ color: "#fff", marginBottom: "1.5rem" }}>🎯 Dashboard</h1>

      {/* === KPI === */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        <KpiCard title="Totale Partite" value={globalStats?.total_matches ?? 0} color="#61dafb" />
        <KpiCard title="Win Rate" value={formatPercent(globalStats?.win_rate ?? 0)} color="limegreen" />
        <KpiCard title="Top 4 Rate" value={formatPercent(globalStats?.top4_rate ?? 0)} color="gold" />
        <KpiCard
          title="Posizione Media"
          value={globalStats?.avg_placement?.toFixed(2) ?? "-"}
          color="#ffb347"
        />
      </div>

      {/* === HERO & COMPOSITION === */}
      <div
        style={{
          background: "#1E1E1E",
          padding: "1.5rem",
          borderRadius: "12px",
          boxShadow: "0 0 10px rgba(0,0,0,0.3)",
          marginBottom: "2rem",
        }}
      >
        <h3 style={{ color: "#fff" }}>🧙‍♂️ Statistiche Eroi e Composizioni</h3>
        <HeroStatsChart />
        <CompositionPieChart />
      </div>

      {/* === TREND RATING === */}
      <div
        style={{
          background: "#1E1E1E",
          padding: "1.5rem",
          borderRadius: "12px",
          boxShadow: "0 0 10px rgba(0,0,0,0.3)",
          marginBottom: "2rem",
        }}
      >
        <h3 style={{ color: "#fff" }}>📈 Andamento Rating</h3>
        <RatingTrendChart />
      </div>

      {/* === TREND RECENTE (RECHARTS) === */}
      <div
        style={{
          background: "#1E1E1E",
          padding: "1rem",
          borderRadius: "12px",
          boxShadow: "0 0 10px rgba(0,0,0,0.3)",
          marginBottom: "2rem",
          height: 280,
        }}
      >
        <h3 style={{ marginBottom: "0.8rem", color: "#fff" }}>
          📊 Trend recente (ultimi 10 match)
        </h3>
        {trendStats.length > 0 ? (
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={trendStats}>
              <CartesianGrid stroke="#333" />
              <XAxis dataKey="date" tick={{ fill: "#aaa", fontSize: 12 }} />
              <YAxis tick={{ fill: "#aaa", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#222",
                  border: "1px solid #555",
                  color: "#fff",
                }}
                labelStyle={{ color: "#fff" }}
              />
              <Line
                type="monotone"
                dataKey="win_rate"
                stroke="limegreen"
                strokeWidth={2}
                name="Win Rate"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="avg_placement"
                stroke="#61dafb"
                strokeWidth={2}
                name="Posizione Media"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: "#aaa" }}>Dati trend non disponibili.</p>
        )}
      </div>

      {/* === SYNC STATUS === */}
      {syncStatus && (
        <div
          style={{
            background: "#1E1E1E",
            padding: "1.5rem",
            borderRadius: "12px",
            boxShadow: "0 0 10px rgba(0,0,0,0.3)",
            marginBottom: "2rem",
          }}
        >
          <h3 style={{ marginBottom: "0.5rem", color: "#fff" }}>🔄 Stato Sincronizzazione</h3>
          <p>
            Ultimo Import:{" "}
            <strong>
              {syncStatus.last_import_time
                ? new Date(syncStatus.last_import_time).toLocaleString("it-IT")
                : "N/A"}
            </strong>
          </p>
          <p>
            Stato:{" "}
            <strong style={{ color: statusColor(syncStatus.last_status || "N/A") }}>
              {syncStatus.last_status || "N/D"}
            </strong>
          </p>
          <button
            onClick={handleManualImport}
            disabled={importing}
            style={{
              marginTop: "1rem",
              padding: "0.7rem 1.2rem",
              borderRadius: "8px",
              border: "none",
              cursor: importing ? "not-allowed" : "pointer",
              backgroundColor: importing ? "#555" : "#3b82f6",
              color: "#fff",
              fontWeight: "bold",
              transition: "background 0.2s ease",
            }}
          >
            {importing ? "⏳ Import in corso..." : "▶️ Avvia Import Manuale"}
          </button>
        </div>
      )}

      {/* === LINK RAPIDI === */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginTop: "2rem",
        }}
      >
        <NavCard title="📜 Partite" onClick={() => navigate("/matches")} />
        <NavCard title="📊 Statistiche" onClick={() => navigate("/stats")} />
        <NavCard title="🧩 Log Import" onClick={() => navigate("/import-logs")} />
      </div>
    </div>
  );
};

// === COMPONENTI SECONDARI ===
interface KpiCardProps {
  title: string;
  value: string | number;
  color: string;
}

const KpiCard: React.FC<KpiCardProps> = ({ title, value, color }) => (
  <div
    style={{
      background: "#1E1E1E",
      borderRadius: "12px",
      padding: "1.5rem",
      textAlign: "center",
      boxShadow: "0 0 10px rgba(0,0,0,0.3)",
      transition: "transform 0.2s ease, box-shadow 0.2s ease",
    }}
  >
    <h4 style={{ color: "#ccc", marginBottom: "0.5rem" }}>{title}</h4>
    <h2 style={{ color, fontSize: "1.8rem", margin: 0 }}>{value}</h2>
  </div>
);

interface NavCardProps {
  title: string;
  onClick: () => void;
}

const NavCard: React.FC<NavCardProps> = ({ title, onClick }) => (
  <div
    onClick={onClick}
    style={{
      background: "#272727",
      padding: "1.2rem",
      borderRadius: "10px",
      textAlign: "center",
      color: "#fff",
      fontWeight: "bold",
      cursor: "pointer",
      transition: "background 0.2s ease, transform 0.2s ease",
    }}
    onMouseEnter={(e) => {
      (e.currentTarget as HTMLDivElement).style.background = "#333";
      (e.currentTarget as HTMLDivElement).style.transform = "scale(1.05)";
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLDivElement).style.background = "#272727";
      (e.currentTarget as HTMLDivElement).style.transform = "scale(1)";
    }}
  >
    {title}
  </div>
);
