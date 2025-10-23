// src/types.ts

// ---------- MATCH ----------
export interface BattlegroundsMatch {
  id?: number;
  hero_name: string;
  placement: number;
  rating_delta: number;
  mmr_after?: number; // vecchio campo usato in alcune versioni
  rating_after?: number; // nuovo nome coerente con backend
  date?: string; // fallback più generico
  end_time?: string; // campo usato per il timestamp della partita
  duration_min?: number;
  game_result?: string;
  minions_list?: string[] | string;
  minion_images?: string[] | string;
}


// ---------- IMPORT LOG ----------
export interface ImportLog {
  timestamp: string;
  matches_imported: number;
  status: "SUCCESS" | "FAILURE" | "RUNNING" | string;
}

// ---------- SYNC STATUS ----------
export interface SyncStatus {
  id?: number;
  last_import_time: string | null;
  last_status?: string;
}

// ---------- HERO STATS ----------
export interface HeroStats {
  hero_name: string;
  average_placement: number;
  pick_rate: number;
  win_rate: number;
}

// ---------- GLOBAL STATS ----------
export interface GlobalStats {
  total_matches: number;
  avg_placement: number;
  top4_rate: number;
  win_rate: number;
  last_update: string;
}

// ---------- TREND STATS ----------
export interface TrendPoint {
  date: string;
  avg_placement: number;
  win_rate: number;
}
