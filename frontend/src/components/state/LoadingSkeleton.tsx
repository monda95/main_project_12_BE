import clsx from 'clsx';

interface LoadingSkeletonProps {
  lines?: number;
  className?: string;
}

export const LoadingSkeleton = ({ lines = 4, className }: LoadingSkeletonProps) => {
  return (
    <div className={clsx('space-y-3', className)} aria-live="polite" role="status">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="h-4 animate-pulse rounded-full bg-slate-700/60"
          style={{ animationDelay: `${index * 80}ms` }}
        />
      ))}
    </div>
  );
};
