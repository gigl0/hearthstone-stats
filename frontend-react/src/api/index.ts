// src/api/index.ts

export interface Match {
  hero_name: string;
  hero_image: string;
  placement: number;
  rating_after: number;
  start_time: string;
}

/**
 * Fetch matches from FastAPI backend
 */
export async function getMatches() {
  const API_URL = "http://localhost:8000/api/v1/bg/matches"; // ✅ percorso giusto

  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("❌ Error fetching matches:", err);
    return [];
  }
}

