import clsx from 'clsx';
import type { RecSuggestion } from '../../types';

interface SuggestionListProps {
  title: string;
  items: RecSuggestion[];
  onSelect: (value: string) => void;
  isLoading?: boolean;
}

const reasonLabel: Record<RecSuggestion['reason'], string> = {
  'co-occur': '연관',
  popular: '인기',
  trend: '트렌드'
};

export const SuggestionList = ({ title, items, onSelect, isLoading }: SuggestionListProps) => {
  return (
    <section className="glass-panel rounded-2xl p-5">
      <header className="mb-4 flex items-center justify-between text-sm font-semibold text-slate-200">
        <h2>{title}</h2>
        {isLoading && <span className="text-xs text-slate-400">로딩 중…</span>}
      </header>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={`${item.text}-${item.reason}`}>
            <button
              type="button"
              onClick={() => onSelect(item.text)}
              className={clsx(
                'focus-ring flex w-full items-center justify-between rounded-xl border border-white/5 bg-slate-900/60 px-4 py-3 text-left text-sm transition hover:bg-slate-800/80'
              )}
            >
              <span className="font-medium text-slate-200">{item.text}</span>
              <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-400">
                {reasonLabel[item.reason]}
              </span>
            </button>
          </li>
        ))}
        {!items.length && (
          <li className="text-xs text-slate-500">추천 데이터가 없습니다.</li>
        )}
      </ul>
    </section>
  );
};
