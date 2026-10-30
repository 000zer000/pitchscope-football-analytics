export type Player = {
  id: number;
  name: string;
  teams: string[];
  roles: string[];
  appearances: number;
  minutes: number | null;
  uncertain_appearances: number;
  shots: number;
  goals: number;
  xg: number | null;
  passes: number;
  completed: number;
  pass_pct: number | null;
  shots_p90: number | null;
  goals_p90: number | null;
  xg_p90: number | null;
  passes_p90: number | null;
  penalties: number;
  rate_note: string | null;
  percentiles?: Record<string, number>;
};
export type Match = {
  id: number;
  home: string;
  away: string;
  home_id: number;
  away_id: number;
  home_score: number;
  away_score: number;
  date: string;
  stage: string;
  duration: number | null;
  periods: Record<string, number>;
  minutes?: number;
  role?: string;
  uncertainty?: string;
};
export type Coverage = {
  synthetic?: boolean;
  seasons: { id: string; name: string }[];
  imported_matches: number;
  expected_matches: number;
  complete?: boolean;
  source_commit?: string;
  events: number;
  players: number;
  uncertain_appearances?: number;
  teams: { id: number; name: string }[];
  imports?: {
    match_id: number;
    imported_at: string;
    transform_version: string;
    hashes: Record<string, string>;
  }[];
  matches?: Match[];
};
export type Comparison = {
  players: Player[];
  population: {
    season: string;
    role: string;
    min_minutes: number;
    count: number;
  };
  warnings: string[];
  metrics: { key: keyof Player; label: string; unit: string }[];
  source_commit: string;
};
export type SourceEvent = {
  id: string;
  index: number;
  period: number;
  minute: number;
  second: number;
  kind: string;
  team_id: number;
  player_id: number;
  x: number | null;
  y: number | null;
  attributes: {
    player?: { name: string };
    team: { name: string };
    shot?: {
      statsbomb_xg?: number;
      outcome: { name: string };
      type: { name: string };
      body_part?: { name: string };
    };
    [key: string]: unknown;
  };
};
export const format = (v: unknown, digits = 2): string =>
  typeof v === "number"
    ? v.toLocaleString("en-GB", {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
      })
    : "N/A";
