import { useCallback, useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import type { FoodAnswer, RecPopularItem, RecSuggestion } from '../types';
import { useSearchService } from '../services/searchService';

interface SearchExperienceState {
  answer: FoodAnswer | null;
  history: string[];
  suggestions: RecSuggestion[];
  recommended: RecSuggestion[];
  popular: RecSuggestion[];
}

export const useSearchExperience = () => {
  const service = useSearchService();
  const [query, setQuery] = useState('');

  const historyQuery = useQuery({
    queryKey: ['search-history'],
    queryFn: service.history
  });

  const recommendedQuery = useQuery({
    queryKey: ['search-recommended'],
    queryFn: service.recommended
  });

  const popularQuery = useQuery({
    queryKey: ['search-popular'],
    queryFn: service.popular
  });

  const inferenceMutation = useMutation({
    mutationFn: service.inference
  });

  const suggestMutation = useMutation({
    mutationFn: service.suggest
  });

  const updateQuery = useCallback(
    (value: string) => {
      setQuery(value);
      if (!value) {
        suggestMutation.reset();
      }
    },
    [suggestMutation]
  );

  const runInference = useCallback(
    async (value: string) => {
      setQuery(value);
      await inferenceMutation.mutateAsync({ query: value });
      historyQuery.refetch();
    },
    [historyQuery, inferenceMutation]
  );

  const fetchSuggestions = useCallback(
    async (value: string) => {
      if (!value.trim() || value.trim().length < 2) {
        suggestMutation.reset();
        return;
      }
      await suggestMutation.mutateAsync(value);
    },
    [suggestMutation]
  );

  const state: SearchExperienceState = useMemo(
    () => ({
      answer: (inferenceMutation.data as FoodAnswer | undefined) ?? null,
      history: historyQuery.data ?? [],
      suggestions: suggestMutation.data ?? [],
      recommended: recommendedQuery.data ?? [],
      popular: transformPopular(popularQuery.data)
    }),
    [
      historyQuery.data,
      inferenceMutation.data,
      popularQuery.data,
      recommendedQuery.data,
      suggestMutation.data
    ]
  );

  return {
    state,
    query,
    isLoading:
      inferenceMutation.isPending ||
      historyQuery.isFetching ||
      recommendedQuery.isFetching ||
      popularQuery.isFetching,
    inferenceMutation,
    historyQuery,
    recommendedQuery,
    popularQuery,
    suggestMutation,
    runInference,
    fetchSuggestions,
    updateQuery
  };
};

const transformPopular = (items?: RecPopularItem[]): RecSuggestion[] => {
  if (!items) return [];
  return items.map((item) => ({ text: item.query, reason: 'popular' as const }));
};
