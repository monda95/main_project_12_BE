export interface FoodAnswerSection {
  title: string;
  content: string;
}

export interface FoodAnswerMetaViolation {
  code: string;
  detail?: string;
}

export interface FoodAnswerMeta {
  check_pass: boolean;
  retry_used: boolean;
  violations?: FoodAnswerMetaViolation[];
  latency_ms?: number;
  hits?: number;
}

export interface FoodAnswer {
  nutrition: string;
  allergy: string;
  storage: string;
  processing: string;
  source: string;
  meta?: FoodAnswerMeta;
}

export interface RecSuggestion {
  text: string;
  reason: 'co-occur' | 'popular' | 'trend';
}

export interface RecPopularItem {
  query: string;
  cnt: number;
}

export interface StatsOverview {
  total_users: number;
  active_users: number;
  daily_signups_last_7_days: { date: string; count: number }[];
}

export interface InferencePayload {
  query: string;
}

export interface PopularQueryChartDatum {
  date: string;
  count: number;
}
