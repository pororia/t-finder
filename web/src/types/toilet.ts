export interface Location {
  lat: number;
  lng: number;
}

export interface Photo {
  id: string;
  image_url: string;
  display_order: number;
}

export type ToiletType = '간이' | '개방' | '공중' | '이동';

export interface Toilet {
  id: string;
  toilet_type: ToiletType | null;
  location: Location;
  address: string;
  address_jibun: string | null;
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
  male_seat_count: number;
  male_urinal_count: number;
  male_disabled_seat_count: number;
  male_disabled_urinal_count: number;
  male_children_seat_count: number;
  male_children_urinal_count: number;
  female_seat_count: number;
  female_disabled_seat_count: number;
  female_children_seat_count: number;
  open_hours: string | null;
  has_emergency_bell: boolean;
  emergency_bell_location: string | null;
  has_entrance_cctv: boolean;
  has_diaper_table: boolean;
  diaper_table_location: string | null;
  remodeling_date: string | null;
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
