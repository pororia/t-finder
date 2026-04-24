import { apiClient } from './client';
import type { Toilet, ToiletNearby, ToiletHistory, Review } from '@/types/toilet';

export interface ToiletCreateInput {
  location: { lat: number; lng: number };
  address: string;
  address_detail?: string;
  name?: string;
  cleanliness: number;
  description?: string;
  has_password: boolean;
  password_value?: string;
  is_unisex: boolean;
  is_accessible: boolean;
  seat_count: number;
  urinal_count: number;
  payment_type: 'FREE' | 'PAID';
  cost?: number;
}

export async function getToilets(offset = 0, limit = 20) {
  const { data } = await apiClient.get('/toilets', { params: { offset, limit } });
  return data.data;
}

export async function getToilet(id: string): Promise<Toilet> {
  const { data } = await apiClient.get(`/toilets/${id}`);
  return data.data;
}

export async function createToilet(input: ToiletCreateInput): Promise<{ id: string }> {
  const { data } = await apiClient.post('/toilets', input);
  return data.data;
}

export async function updateToilet(id: string, input: Partial<ToiletCreateInput>): Promise<void> {
  await apiClient.put(`/toilets/${id}`, input);
}

export async function deleteToilet(id: string): Promise<void> {
  await apiClient.delete(`/toilets/${id}`);
}

export async function getToiletHistory(id: string): Promise<ToiletHistory[]> {
  const { data } = await apiClient.get(`/toilets/${id}/history`);
  return data.data.results;
}

export async function getNearbyToilets(lat: number, lng: number, radius = 1000): Promise<ToiletNearby[]> {
  const { data } = await apiClient.get('/toilets/nearby', { params: { lat, lng, radius } });
  return data.data.results;
}

export async function searchToilets(q: string): Promise<Toilet[]> {
  const { data } = await apiClient.get('/toilets/search', { params: { q } });
  return data.data.results;
}

export async function getInBoundsToilets(min_lat: number, min_lng: number, max_lat: number, max_lng: number) {
  const { data } = await apiClient.get('/toilets/in-bounds', { params: { min_lat, min_lng, max_lat, max_lng } });
  return data.data.results;
}

export async function getToiletReviews(toiletId: string): Promise<Review[]> {
  const { data } = await apiClient.get(`/toilets/${toiletId}/reviews`);
  return data.data.results;
}

export async function createReview(toiletId: string, rating: number, comment?: string): Promise<void> {
  await apiClient.post(`/toilets/${toiletId}/reviews`, { rating, comment });
}

export async function uploadToiletPhoto(toiletId: string, file: File): Promise<{ id: string; image_url: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post(`/toilets/${toiletId}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.data;
}
