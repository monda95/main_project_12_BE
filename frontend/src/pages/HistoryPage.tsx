import { useQuery } from '@tanstack/react-query';
import { EmptyState } from '../components/state/EmptyState';
import { ErrorState } from '../components/state/ErrorState';
import { LoadingSkeleton } from '../components/state/LoadingSkeleton';
import { NoAccess } from '../components/state/NoAccess';
import { useSearchService } from '../services/searchService';

export const HistoryPage = () => {
  const searchService = useSearchService();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['search-history-page'],
    queryFn: searchService.history
  });

  if (isLoading) {
    return <LoadingSkeleton lines={8} className="glass-panel rounded-3xl p-6" />;
  }

  if (isError) {
    if ((error as { status?: number })?.status === 401) {
      return <NoAccess description="히스토리를 확인하려면 로그인하세요." />;
    }
    return <ErrorState description="히스토리를 불러오지 못했습니다." />;
  }

  if (!data || data.length === 0) {
    return <EmptyState description="최근 검색 기록이 없습니다." />;
  }

  return (
    <section className="glass-panel rounded-3xl p-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">검색 히스토리</h2>
          <p className="text-xs text-slate-400">최근 30건까지 표시됩니다.</p>
        </div>
      </header>
      <ol className="space-y-4">
        {data.map((query, index) => (
          <li key={`${query}-${index}`} className="rounded-2xl border border-white/5 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between text-sm">
              <div>
                <p className="text-slate-200">{query}</p>
              </div>
              <span className="text-xs text-slate-500">최근</span>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
};
