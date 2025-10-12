import { Link } from 'react-router-dom';

export const NotFoundPage = () => {
  return (
    <div className="glass-panel mx-auto mt-24 flex max-w-md flex-col items-center gap-4 rounded-3xl px-6 py-10 text-center">
      <span className="text-6xl">🥄</span>
      <h2 className="text-xl font-semibold text-white">페이지를 찾을 수 없습니다.</h2>
      <p className="text-sm text-slate-400">
        요청하신 페이지가 존재하지 않거나 이동되었어요. 홈으로 돌아가 다시 탐색해 주세요.
      </p>
      <Link
        to="/"
        className="focus-ring rounded-full bg-brand.primary px-5 py-2 text-sm font-semibold text-slate-950"
      >
        홈으로 돌아가기
      </Link>
    </div>
  );
};
