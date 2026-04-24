import { apiClient } from './client';
import type { User } from '@/types/user';

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get('/auth/me');
  return data.data;
}

export async function logoutApi(): Promise<void> {
  await apiClient.post('/auth/logout');
}
