import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

interface ErrorStateProps {
  title?: string;
  description?: string;
  action?: ReactNode;
}

export const ErrorState = ({ title, description, action }: ErrorStateProps) => {
  const { t } = useTranslation();

  return (
    <div
      role="alert"
      className="glass-panel flex flex-col gap-4 rounded-2xl border border-red-500/30 px-6 py-8"
    >
      <div>
        <h2 className="text-base font-semibold text-red-300">{title ?? t('common.error')}</h2>
        <p className="mt-2 text-sm text-slate-300">
          {description ?? '잠시 후 다시 시도해 주세요.'}
        </p>
      </div>
      {action && <div className="flex justify-end">{action}</div>}
    </div>
  );
};
