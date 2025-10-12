import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { ResultTabs } from '../components/search/ResultTabs';
import { SearchInput } from '../components/search/SearchInput';
import { SuggestionList } from '../components/search/SuggestionList';
import { EmptyState } from '../components/state/EmptyState';
import { ErrorState } from '../components/state/ErrorState';
import { LoadingSkeleton } from '../components/state/LoadingSkeleton';
import { useSearchExperience } from '../hooks/useSearchExperience';

export const HomePage = () => {
  const { t } = useTranslation();
  const {
    state,
    query,
    inferenceMutation,
    historyQuery,
    recommendedQuery,
    popularQuery,
    suggestMutation,
    runInference,
    fetchSuggestions,
    updateQuery
  } = useSearchExperience();

  useEffect(() => {
    if (!query) return;
    const timeout = window.setTimeout(() => fetchSuggestions(query), 300);
    return () => window.clearTimeout(timeout);
  }, [query, fetchSuggestions]);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <section className="space-y-6">
        <SearchInput
          value={query}
          onSubmit={runInference}
          isLoading={inferenceMutation.isPending}
          onChange={updateQuery}
        />
        {state.suggestions.length > 0 && (
          <SuggestionList
            title="자동완성"
            items={state.suggestions}
            onSelect={runInference}
            isLoading={suggestMutation.isPending}
          />
        )}
        {inferenceMutation.isPending && <LoadingSkeleton className="glass-panel rounded-3xl p-6" />}
        {inferenceMutation.isError && (
          <ErrorState
            description={resolveErrorMessage(inferenceMutation.error)}
            action={
              <button
                type="button"
                className="focus-ring rounded-full bg-brand.primary/80 px-4 py-2 text-sm font-semibold text-slate-950"
                onClick={() => query && runInference(query)}
              >
                {t('common.retry')}
              </button>
            }
          />
        )}
        {state.answer ? <ResultTabs answer={state.answer} /> : <EmptyState description="응답을 받아보려면 질문을 입력해 주세요." />}
      </section>
      <aside className="space-y-5">
        <SuggestionList
          title={t('home.suggestions')}
          items={state.recommended}
          onSelect={runInference}
          isLoading={recommendedQuery.isFetching}
        />
        <SuggestionList
          title={t('home.history')}
          items={state.history.map((text) => ({ text, reason: 'trend' as const }))}
          onSelect={runInference}
          isLoading={historyQuery.isFetching}
        />
        <SuggestionList
          title={t('home.popular')}
          items={state.popular}
          onSelect={runInference}
          isLoading={popularQuery.isFetching}
        />
      </aside>
    </div>
  );
};

const resolveErrorMessage = (error: unknown) => {
  if (typeof error === 'object' && error && 'status' in error) {
    const status = (error as { status: number }).status;
    switch (status) {
      case 401:
      case 403:
        return '로그인이 필요합니다.';
      case 408:
        return '요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.';
      case 429:
        return '요청이 많습니다. 잠시 후 다시 시도해 주세요.';
      default:
        if (status >= 500) {
          return '서버에 문제가 발생했습니다. 불편을 드려 죄송합니다.';
        }
    }
  }
  return '요청 처리 중 문제가 발생했습니다.';
};
