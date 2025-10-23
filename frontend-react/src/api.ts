// src/api.ts
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function fetchJSON(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, options);
  if (!res.ok) {
    throw new Error(`Errore API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

// ---------- MATCHES ----------
export async function getRecentMatches() {
  return fetchJSON("/api/v1/matches/recent");
}

// ---------- STATS ----------
export async function getHeroStats() {
  return fetchJSON("/api/v1/stats/heroes");
}

export async function getGlobalStats() {
  return fetchJSON("/api/v1/stats/global");
}

export async function getTrendStats() {
  return fetchJSON("/api/v1/stats/trend");
}

// ---------- IMPORT ----------
export async function getImportLogs() {
  return fetchJSON("/api/v1/import/logs");
}

// ---------- SYNC ----------
export async function getSyncStatus() {
  return fetchJSON("/api/v1/sync/status");
}

// ---------- (Opzionale) TRIGGER IMPORT MANUALE ----------
export async function triggerImport() {
  return fetchJSON("/api/v1/import/start", { method: "POST" });
}
