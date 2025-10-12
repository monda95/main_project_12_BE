import { useTranslation } from 'react-i18next';

interface NoAccessProps {
  description?: string;
}

export const NoAccess = ({ description }: NoAccessProps) => {
  const { t } = useTranslation();

  return (
    <div className="glass-panel flex flex-col gap-3 rounded-2xl border border-yellow-500/30 px-6 py-8 text-center">
      <span className="text-3xl">🔒</span>
      <p className="text-sm text-slate-200">{description ?? t('common.no_access')}</p>
    </div>
  );
};
