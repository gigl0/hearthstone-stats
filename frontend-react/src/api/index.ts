// === FRONTEND API ===
// Tutte le chiamate sono già allineate con il backend attuale FastAPI

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
console.log("🌍 API BASE URL:", API_URL);

// === MATCHES ===
export const getRecentMatches = async () => {
  const res = await fetch(`${API_URL}/api/v1/matches/recent`);
  if (!res.ok) throw new Error(`Errore API Matches ${res.status}`);
  return res.json();
};

// === STATS ===
export const getGlobalStats = async () => {
  const res = await fetch(`${API_URL}/api/v1/stats/global`);
  if (!res.ok) throw new Error(`Errore API Stats Global ${res.status}`);
  return res.json();
};

export const getHeroStats = async () => {
  const res = await fetch(`${API_URL}/api/v1/stats/heroes`);
  if (!res.ok) throw new Error(`Errore API Hero Stats ${res.status}`);
  return res.json();
};

export const getTrendStats = async () => {
  const res = await fetch(`${API_URL}/api/v1/stats/rating_trend`);
  if (!res.ok) throw new Error(`Errore API Trend ${res.status}`);
  return res.json();
};

export const getMinionStats = async () => {
  const res = await fetch(`${API_URL}/api/v1/stats/minions`);
  if (!res.ok) throw new Error(`Errore API Minions ${res.status}`);
  return res.json();
};

// === IMPORT ===
export const getImportLogs = async () => {
  const res = await fetch(`${API_URL}/api/v1/import/logs`);
  if (!res.ok) throw new Error(`Errore API Import Logs ${res.status}`);
  return res.json();
};

export const getSyncStatus = async () => {
  const res = await fetch(`${API_URL}/api/v1/import/status`);
  if (!res.ok) throw new Error(`Errore API Sync Status ${res.status}`);
  return res.json();
};

// === IMPORT MANUALE ===
export const triggerImport = async () => {
  const res = await fetch(`${API_URL}/api/v1/import/start`, { method: "POST" });
  if (!res.ok) throw new Error(`Errore API Trigger Import ${res.status}`);
  return res.json();
};
