import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

const navItems = [
  { to: '/', label: '홈' },
  { to: '/history', label: '히스토리' },
  { to: '/mypage', label: '마이페이지' },
  { to: '/admin', label: '관리자' }
];

export const AppLayout = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="glass-panel sticky top-0 z-50 border-b border-white/5 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-brand.primary/80">Nourisher</p>
            <h1 className="text-lg font-semibold text-white">{t('home.title')}</h1>
          </div>
          <nav className="flex gap-2 text-sm">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  clsx(
                    'focus-ring rounded-full px-4 py-2 transition-colors',
                    isActive
                      ? 'bg-brand.primary/20 text-brand.primary shadow-glow'
                      : 'text-slate-300 hover:text-white'
                  )
                }
                end={item.to === '/'}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto flex max-w-6xl flex-1 flex-col gap-6 px-6 pb-12 pt-8">
        <Outlet />
      </main>
      <footer className="border-t border-white/5 bg-slate-950/80 py-6 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} Nourisher. All rights reserved.
      </footer>
    </div>
  );
};
