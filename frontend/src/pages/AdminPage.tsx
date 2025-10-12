import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { EmptyState } from '../components/state/EmptyState';
import { ErrorState } from '../components/state/ErrorState';
import { LoadingSkeleton } from '../components/state/LoadingSkeleton';
import { NoAccess } from '../components/state/NoAccess';
import { useStatsService } from '../services/statsService';

export const AdminPage = () => {
  const statsService = useStatsService();
  const overviewQuery = useQuery({ queryKey: ['stats-overview'], queryFn: statsService.overview });
  const popularQuery = useQuery({ queryKey: ['stats-popular'], queryFn: statsService.popularQueries });

  if (overviewQuery.isLoading || popularQuery.isLoading) {
    return <LoadingSkeleton lines={10} className="glass-panel rounded-3xl p-6" />;
  }

  if (overviewQuery.isError || popularQuery.isError) {
    const httpError = (overviewQuery.error ?? popularQuery.error) as { status?: number } | undefined;
    if (httpError?.status === 403) {
      return <NoAccess description="관리자 권한이 필요합니다." />;
    }
    return <ErrorState description="대시보드 데이터를 불러오지 못했습니다." />;
  }

  if (!overviewQuery.data) {
    return <EmptyState description="표시할 통계가 없습니다." />;
  }

  const overview = overviewQuery.data;
  const dailyChart = useMemo(() => {
    return overview.daily_signups_last_7_days.map((item) => ({
      date: new Date(item.date).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }),
      count: item.count
    }));
  }, [overview.daily_signups_last_7_days]);

  return (
    <section className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="총 사용자" value={overview.total_users.toLocaleString()} helper="누적 가입자" />
        <StatCard title="활성 사용자" value={overview.active_users.toLocaleString()} helper="is_active=true" />
        <StatCard
          title="최근 7일 신규"
          value={overview.daily_signups_last_7_days.reduce((acc, cur) => acc + cur.count, 0).toLocaleString()}
          helper="최근 7일 가입자 합계"
        />
      </div>

      <div className="glass-panel rounded-3xl p-6">
        <header className="mb-4">
          <h2 className="text-base font-semibold text-white">최근 7일 신규 가입 추이</h2>
          <p className="text-xs text-slate-400">일별 가입자 수를 확인하세요.</p>
        </header>
        <div className="h-72">
          <ResponsiveContainer>
            <LineChart data={dailyChart} margin={{ left: 12, right: 12, top: 8, bottom: 8 }}>
              <XAxis dataKey="date" stroke="#94a3b8" tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  background: '#0f172a',
                  borderRadius: 16,
                  border: '1px solid rgba(148, 163, 184, 0.2)',
                  color: '#e2e8f0'
                }}
              />
              <Line type="monotone" dataKey="count" stroke="#22d3ee" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-panel rounded-3xl p-6">
        <header className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-white">인기 검색어 TOP 10</h2>
            <p className="text-xs text-slate-400">검색 로그 기반으로 집계된 데이터입니다.</p>
          </div>
        </header>
        <ol className="space-y-3">
          {(popularQuery.data ?? []).map((item, index) => (
            <li key={item.query} className="flex items-center justify-between rounded-2xl border border-white/5 bg-slate-900/60 px-5 py-3">
              <span className="text-sm text-slate-200">
                <span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full bg-brand.primary/20 text-xs text-brand.primary">
                  {index + 1}
                </span>
                {item.query}
              </span>
              <span className="text-xs text-slate-400">{item.cnt.toLocaleString()}회</span>
            </li>
          ))}
          {!popularQuery.data?.length && <p className="text-xs text-slate-500">데이터가 없습니다.</p>}
        </ol>
      </div>
    </section>
  );
};

interface StatCardProps {
  title: string;
  value: string;
  helper: string;
}

const StatCard = ({ title, value, helper }: StatCardProps) => (
  <div className="glass-panel rounded-2xl border border-white/5 p-5">
    <p className="text-xs text-slate-400">{title}</p>
    <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    <p className="mt-3 text-xs text-slate-500">{helper}</p>
  </div>
);
