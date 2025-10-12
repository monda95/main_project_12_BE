import { useTranslation } from 'react-i18next';

interface EmptyStateProps {
  description?: string;
}

export const EmptyState = ({ description }: EmptyStateProps) => {
  const { t } = useTranslation();

  return (
    <div className="glass-panel flex flex-col items-center gap-3 rounded-2xl px-6 py-10 text-center">
      <span className="text-3xl">🍽️</span>
      <p className="text-sm text-slate-300">{description ?? t('common.empty')}</p>
    </div>
  );
};
