import { create } from 'zustand';

interface LocationState {
  location: { lat: number; lng: number } | null;
  setLocation: (location: { lat: number; lng: number } | null) => void;
}

export const useLocationStore = create<LocationState>((set) => ({
  location: null,
  setLocation: (location) => set({ location }),
}));
