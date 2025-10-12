import clsx from 'clsx';
import { useMemo, useState } from 'react';

import type { FoodAnswer } from '../../types';

const tabs = [
  { key: 'nutrition', label: '영양' },
  { key: 'allergy', label: '알레르기' },
  { key: 'storage', label: '보관' },
  { key: 'processing', label: '가공법' }
] as const;

interface ResultTabsProps {
  answer: FoodAnswer;
}

export const ResultTabs = ({ answer }: ResultTabsProps) => {
  const [activeKey, setActiveKey] = useState<(typeof tabs)[number]['key']>('nutrition');

  const sections = useMemo(() => {
    return tabs.map((tab) => ({ key: tab.key, label: tab.label, content: answer[tab.key] }));
  }, [answer]);

  return (
    <div className="glass-panel flex flex-col gap-4 rounded-3xl p-6">
      <div className="flex flex-wrap gap-2">
        {sections.map((section) => (
          <button
            key={section.key}
            type="button"
            onClick={() => setActiveKey(section.key)}
            className={clsx(
              'focus-ring rounded-full px-4 py-2 text-sm transition',
              activeKey === section.key
                ? 'bg-brand.secondary/20 text-brand.secondary shadow-glow'
                : 'bg-slate-900/70 text-slate-300 hover:text-white'
            )}
          >
            {section.label}
          </button>
        ))}
      </div>
      <article className="min-h-[160px] whitespace-pre-line rounded-2xl border border-white/5 bg-slate-900/60 px-4 py-5 text-sm leading-relaxed text-slate-100">
        {sections.find((section) => section.key === activeKey)?.content ?? '정보가 없습니다.'}
      </article>
      <footer className="border-t border-white/5 pt-4 text-xs text-slate-400">
        출처: {answer.source || '정보 부족'}
        {answer.meta?.latency_ms && ` · 응답속도 ${answer.meta.latency_ms}ms`}
        {answer.meta?.hits && ` · 누적 조회 ${answer.meta.hits}회`}
        {!answer.meta?.check_pass && (
          <p className="mt-2 text-red-300">
            ⚠️ Self-Check 실패. {answer.meta?.violations?.map((v) => v.code).join(', ')}
          </p>
        )}
      </footer>
    </div>
  );
};
