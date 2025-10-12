import type { RecPopularItem, StatsOverview } from '../types';
import { useApiContext } from './ApiContext';

export const useStatsService = () => {
  const api = useApiContext();

  const overview = async () => api.get<StatsOverview>('/api/v1/stats/users/');
  const popularQueries = async () => api.get<RecPopularItem[]>('/api/v1/stats/popular-queries/');

  return { overview, popularQueries };
};
