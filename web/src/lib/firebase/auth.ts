import { signInWithPopup, signOut } from 'firebase/auth';
import { auth, googleProvider } from './config';
import { apiClient } from '../api/client';

export async function loginWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider);
  const idToken = await result.user.getIdToken();

  const { data } = await apiClient.post('/auth/google', { id_token: idToken });
  const responseData = data.data;

  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', responseData.access_token);
    localStorage.setItem('refresh_token', responseData.refresh_token);
  }

  return responseData.user;
}

export async function logout() {
  await signOut(auth);
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
