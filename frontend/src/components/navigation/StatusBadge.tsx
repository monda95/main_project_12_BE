import clsx from 'clsx';

interface StatusBadgeProps {
  status: 'success' | 'warning' | 'error';
  label: string;
}

export const StatusBadge = ({ status, label }: StatusBadgeProps) => {
  const styles = {
    success: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    warning: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    error: 'bg-rose-500/20 text-rose-300 border-rose-500/40'
  } as const;

  return (
    <span className={clsx('rounded-full border px-3 py-1 text-xs font-medium', styles[status])}>
      {label}
    </span>
  );
};
