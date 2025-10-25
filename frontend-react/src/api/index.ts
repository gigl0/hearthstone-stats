// === FRONTEND API (DEV MODE) ===
// Tutte le chiamate al backend FastAPI (porta 8000)
// Funziona perfettamente con CRA (npm start) + uvicorn

const API_URL = process.env.REACT_APP_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
console.log("🌍 API BASE URL:", API_URL);

// === Utility interna per fetch con logging ===
async function fetchJSON(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  console.log(`📡 Fetching: ${url}`);

  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      console.error(`❌ API Error ${res.status}: ${url}`);
      throw new Error(`Errore API ${res.status}`);
    }
    return res.json();
  } catch (err) {
    console.error(`💥 Errore chiamata ${url}:`, err);
    throw err;
  }
}

// === MATCHES ===
export const getRecentMatches = () => fetchJSON("/api/v1/matches/recent");

// === STATS ===
export const getGlobalStats = () => fetchJSON("/api/v1/stats/global");
export const getHeroStats = () => fetchJSON("/api/v1/stats/heroes");
export const getTrendStats = () => fetchJSON("/api/v1/stats/rating_trend");
export const getMinionStats = () => fetchJSON("/api/v1/stats/minions");

// === IMPORT ===
export const getImportLogs = () => fetchJSON("/api/v1/import/logs");
export const getSyncStatus = () => fetchJSON("/api/v1/import/status");

// === IMPORT MANUALE ===
export const triggerImport = () =>
  fetchJSON("/api/v1/import/start", { method: "POST" });
