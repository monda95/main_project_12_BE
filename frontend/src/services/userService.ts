import { useApiContext } from './ApiContext';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  nickname?: string | null;
  image_url?: string | null;
  created_at: string;
  updated_at: string;
}

type UserUpdatePayload = Partial<Pick<UserProfile, 'username' | 'nickname' | 'image_url'>>;

export const useUserService = () => {
  const api = useApiContext();

  const profile = async () => api.get<UserProfile>('/api/v1/users/me/');
  const updateProfile = async (data: UserUpdatePayload) =>
    api.patch<UserProfile>('/api/v1/users/me/', { body: data });

  return { profile, updateProfile };
};
