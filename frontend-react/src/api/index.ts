// ==============================
// 🌍 API Client - Hearthstone BG
// ==============================
console.log("🌍 API URL:", process.env.REACT_APP_API_URL);

// Base API URL (da .env) — deve finire con /api/v1
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Helper generale per fetch con gestione errori
async function safeFetch(endpoint: string, errorLabel: string) {
  const res = await fetch(`${API_URL}${endpoint}`);
  if (!res.ok) throw new Error(`Errore API ${errorLabel}: ${res.status}`);
  return res.json();
}

// === 🧩 MATCHES ===
export const getRecentMatches = async () => {
  return safeFetch(`/matches/recent`, "Matches");
};

// === 📊 STATS ===
export const getGlobalStats = async () => {
  return safeFetch(`/stats/global`, "Stats Global");
};

export const getHeroStats = async () => {
  return safeFetch(`/stats/heroes`, "Hero Stats");
};

export const getTrendStats = async () => {
  return safeFetch(`/stats/rating_trend`, "Trend");
};

// === 🔄 IMPORT & SYNC ===
export const getImportLogs = async () => {
  return safeFetch(`/import/logs`, "Import Logs");
};

export const getSyncStatus = async () => {
  return safeFetch(`/import/status`, "Sync Status");
};

// === ▶ Avvio Import Manuale ===
export const triggerImport = async () => {
  const res = await fetch(`${API_URL}/import/start`, { method: "POST" });
  if (!res.ok) throw new Error(`Errore API Import Start: ${res.status}`);
  return res.json();
};
