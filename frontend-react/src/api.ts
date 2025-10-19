// src/api.ts
export async function getMatches() {
  const API_URL = "http://localhost:8000/api/matches"; // o l’indirizzo del backend nella VM

  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("❌ Error fetching matches:", error);
    return [];
  }
}
