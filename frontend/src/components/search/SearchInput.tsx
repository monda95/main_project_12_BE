import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import type { FormEvent } from 'react';
import { useTranslation } from 'react-i18next';

interface SearchInputProps {
  value: string;
  onSubmit: (value: string) => void;
  isLoading?: boolean;
  onChange?: (value: string) => void;
}

export const SearchInput = ({ value, onSubmit, isLoading, onChange }: SearchInputProps) => {
  const { t } = useTranslation();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!value.trim()) return;
    onSubmit(value.trim());
  };

  const handleChange = (next: string) => {
    onChange?.(next);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full items-center gap-3 rounded-full border border-white/10 bg-slate-900/60 px-5 py-3 shadow-glow"
      role="search"
    >
      <MagnifyingGlassIcon className="h-5 w-5 text-brand.primary" aria-hidden />
      <input
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={t('home.search_placeholder')}
        className="focus-ring flex-1 bg-transparent text-sm text-white placeholder:text-slate-400"
        aria-label="검색어 입력"
      />
      <button
        type="submit"
        className={clsx(
          'focus-ring rounded-full bg-brand.primary px-4 py-2 text-sm font-semibold text-slate-950 transition-colors',
          isLoading && 'pointer-events-none opacity-60'
        )}
        disabled={isLoading}
      >
        {isLoading ? '요청 중…' : t('home.submit')}
      </button>
    </form>
  );
};
