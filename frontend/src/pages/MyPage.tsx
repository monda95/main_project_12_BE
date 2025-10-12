import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';

import { ErrorState } from '../components/state/ErrorState';
import { LoadingSkeleton } from '../components/state/LoadingSkeleton';
import { NoAccess } from '../components/state/NoAccess';
import { useUserService } from '../services/userService';

interface ProfileForm {
  username: string;
  nickname?: string;
  image_url?: string;
}

export const MyPage = () => {
  const userService = useUserService();
  const queryClient = useQueryClient();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['user-profile'],
    queryFn: userService.profile
  });

  const mutation = useMutation({
    mutationFn: userService.updateProfile,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user-profile'] })
  });

  const { register, handleSubmit, reset } = useForm<ProfileForm>({
    defaultValues: {
      username: data?.username ?? '',
      nickname: data?.nickname ?? '',
      image_url: data?.image_url ?? ''
    }
  });

  useEffect(() => {
    if (data) {
      reset({
        username: data.username ?? '',
        nickname: data.nickname ?? '',
        image_url: data.image_url ?? ''
      });
    }
  }, [data, reset]);

  if (isLoading) {
    return <LoadingSkeleton lines={6} className="glass-panel rounded-3xl p-6" />;
  }

  if (isError) {
    if ((error as { status?: number })?.status === 401) {
      return <NoAccess description="마이페이지는 로그인 사용자에게만 제공됩니다." />;
    }
    return <ErrorState description="프로필 정보를 불러오지 못했습니다." />;
  }

  const onSubmit = (values: ProfileForm) => {
    mutation.mutate(values);
  };

  return (
    <section className="glass-panel rounded-3xl p-8">
      <header className="mb-6">
        <h2 className="text-lg font-semibold text-white">계정 설정</h2>
        <p className="text-xs text-slate-400">기본 프로필 정보를 관리합니다.</p>
        <p className="mt-2 text-xs text-slate-500">{data.email}</p>
      </header>
      <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-1">
          <label className="text-xs text-slate-400" htmlFor="username">
            사용자 이름
          </label>
          <input
            id="username"
            className="focus-ring rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm"
            {...register('username', { required: true })}
          />
        </div>
        <div className="grid gap-1">
          <label className="text-xs text-slate-400" htmlFor="nickname">
            닉네임
          </label>
          <input
            id="nickname"
            className="focus-ring rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm"
            {...register('nickname')}
          />
        </div>
        <div className="grid gap-1">
          <label className="text-xs text-slate-400" htmlFor="image_url">
            프로필 이미지 URL
          </label>
          <input
            id="image_url"
            className="focus-ring rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm"
            placeholder="https://example.com/avatar.png"
            {...register('image_url')}
          />
        </div>
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="focus-ring rounded-full bg-brand.primary px-5 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            저장
          </button>
          <button
            type="button"
            onClick={() => reset()}
            className="focus-ring rounded-full border border-white/10 px-5 py-2 text-sm text-slate-300"
          >
            초기화
          </button>
          {mutation.isSuccess && <span className="text-xs text-emerald-400">저장되었습니다.</span>}
          {mutation.isError && <span className="text-xs text-rose-400">저장에 실패했습니다.</span>}
        </div>
      </form>
    </section>
  );
};
