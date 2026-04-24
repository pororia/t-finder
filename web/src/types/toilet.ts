export interface Location {
  lat: number;
  lng: number;
}

export interface Photo {
  id: string;
  image_url: string;
  display_order: number;
}

export interface Toilet {
  id: string;
  location: Location;
  address: string;
  address_detail: string | null;
  name: string | null;
  cleanliness: number;
  description: string | null;
  has_password: boolean;
  password_value: string | null;
  is_unisex: boolean;
  is_accessible: boolean;
  seat_count: number;
  urinal_count: number;
  payment_type: 'FREE' | 'PAID';
  cost: number | null;
  photos: Photo[];
  avg_rating: number | null;
  review_count: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ToiletNearby {
  id: string;
  address: string;
  location: Location;
  cleanliness: number;
  is_unisex: boolean;
  is_accessible: boolean;
  payment_type: 'FREE' | 'PAID';
  cost: number | null;
  has_password: boolean;
  thumbnail_url: string | null;
  distance_m: number;
}

export interface ToiletHistory {
  id: string;
  toilet_id: string;
  snapshot: Record<string, unknown>;
  changed_fields: string[] | null;
  change_type: 'CREATE' | 'UPDATE' | 'DELETE';
  changed_by: string;
  changed_at: string;
}

export interface Review {
  id: string;
  toilet_id: string;
  user_id: string;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}
