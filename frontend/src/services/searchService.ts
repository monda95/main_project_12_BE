import type { FoodAnswer, InferencePayload, RecPopularItem, RecSuggestion } from '../types';
import { useApiContext } from './ApiContext';

interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}

const createCache = <T,>() => {
  const store = new Map<string, CacheEntry<T>>();

  return {
    get(key: string) {
      const entry = store.get(key);
      if (entry && entry.expiresAt > Date.now()) {
        return entry.data;
      }
      if (entry) store.delete(key);
      return null;
    },
    set(key: string, value: T, ttlMs: number) {
      store.set(key, { data: value, expiresAt: Date.now() + ttlMs });
    }
  };
};

const suggestionCache = createCache<RecSuggestion[]>();
const popularCache = createCache<RecPopularItem[]>();
const recommendationCache = createCache<RecSuggestion[]>();

export const useSearchService = () => {
  const api = useApiContext();

  const suggest = async (prefix: string) => {
    const cacheKey = `suggest:${prefix}`;
    const cached = suggestionCache.get(cacheKey);
    if (cached) return cached;

    const result = await api.get<string[]>('/api/v1/search/autocomplete/', {
      query: { prefix }
    });
    const mapped = result.map((text) => ({ text, reason: 'co-occur' as const }));
    suggestionCache.set(cacheKey, mapped, 90_000);
    return mapped;
  };

  const recommended = async () => {
    const cacheKey = 'recommended';
    const cached = recommendationCache.get(cacheKey);
    if (cached) return cached;

    const result = await api.get<{ results: string[] }>('/api/v1/search/recommended/');
    const mapped = result.results.map((text) => ({ text, reason: 'trend' as const }));
    recommendationCache.set(cacheKey, mapped, 20 * 60_000);
    return mapped;
  };

  const popular = async () => {
    const cacheKey = 'popular';
    const cached = popularCache.get(cacheKey);
    if (cached) return cached;

    const result = await api.get<RecPopularItem[]>('/api/v1/stats/popular-queries/');
    popularCache.set(cacheKey, result, 10 * 60_000);
    return result;
  };

  const history = async () => {
    return api.get<string[]>('/api/v1/search/recent/');
  };

  const inference = async (payload: InferencePayload) => {
    const result = await api.post<{
      content: Record<string, unknown>;
      self_check: {
        check_pass: boolean;
        retry_used: boolean;
        violations?: { code: string; detail?: string }[];
      };
      status: string;
      error_code?: string | null;
      error_message?: string | null;
    }>('/api/v1/inference/', {
      body: { prompt: payload.query }
    });

    return normalizeAnswer(result);
  };

  return { suggest, recommended, popular, history, inference };
};

const normalizeAnswer = (response: {
  content: Record<string, unknown>;
  self_check: {
    check_pass: boolean;
    retry_used: boolean;
    violations?: { code: string; detail?: string }[];
  };
  status: string;
  error_code?: string | null;
  error_message?: string | null;
}): FoodAnswer => {
  const content = response.content ?? {};

  if (response.status !== 'success') {
    const message = response.error_message ?? 'AI 응답을 가져오지 못했습니다.';
    return {
      nutrition: message,
      allergy: message,
      storage: message,
      processing: message,
      source: '정보 부족',
      meta: {
        check_pass: false,
        retry_used: response.self_check?.retry_used ?? false,
        violations: response.self_check?.violations ?? [{ code: response.error_code ?? 'UNKNOWN_ERROR' }]
      }
    };
  }

  const toText = (value: unknown) => {
    if (typeof value === 'string') return value;
    if (typeof value === 'number') return String(value);
    if (Array.isArray(value)) return value.join('\n');
    if (value && typeof value === 'object') {
      return Object.entries(value)
        .map(([key, val]) => `${key}: ${toText(val)}`)
        .join('\n');
    }
    return '정보 부족';
  };

  return {
    nutrition: toText(content['nutrition']),
    allergy: toText(content['allergy']),
    storage: toText(content['storage']),
    processing: toText(content['processing']),
    source: toText(content['source']),
    meta: {
      check_pass: response.self_check?.check_pass ?? false,
      retry_used: response.self_check?.retry_used ?? false,
      violations: response.self_check?.violations,
      latency_ms: undefined,
      hits: undefined
    }
  };
};
