'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: 'tr' | 'en' | 'ar';
  default_search_source: 'quran' | 'bible' | 'all';
  default_bible_testament: 'ot' | 'nt' | 'apocrypha' | 'all';
  results_per_page: number;
  enable_streaming: boolean;
  enable_multi_agent: boolean;
}

interface PreferencesState extends UserPreferences {
  isLoading: boolean;
  error: string | null;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setLanguage: (language: 'tr' | 'en' | 'ar') => void;
  setDefaultSearchSource: (source: 'quran' | 'bible' | 'all') => void;
  setDefaultBibleTestament: (testament: 'ot' | 'nt' | 'apocrypha' | 'all') => void;
  setResultsPerPage: (count: number) => void;
  setEnableStreaming: (enabled: boolean) => void;
  setEnableMultiAgent: (enabled: boolean) => void;
  fetchPreferences: () => Promise<void>;
  savePreferences: () => Promise<void>;
  reset: () => void;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'system',
  language: 'en',
  default_search_source: 'all',
  default_bible_testament: 'all',
  results_per_page: 10,
  enable_streaming: true,
  enable_multi_agent: false,
};

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set, get) => ({
      ...DEFAULT_PREFERENCES,
      isLoading: false,
      error: null,

      setTheme: (theme) => {
        set({ theme });
      },

      setLanguage: (language) => {
        set({ language });
      },

      setDefaultSearchSource: (source) => {
        set({ default_search_source: source });
      },

      setDefaultBibleTestament: (testament) => {
        set({ default_bible_testament: testament });
      },

      setResultsPerPage: (count) => {
        if (count < 5 || count > 50) {
          set({ error: 'Results per page must be between 5 and 50' });
          return;
        }
        set({ results_per_page: count, error: null });
      },

      setEnableStreaming: (enabled) => {
        set({ enable_streaming: enabled });
      },

      setEnableMultiAgent: (enabled) => {
        set({ enable_multi_agent: enabled });
      },

      fetchPreferences: async () => {
        set({ isLoading: true, error: null });
        try {
          const token = localStorage.getItem('access_token');
          if (!token) {
            set({ isLoading: false });
            return;
          }

          const response = await fetch('http://localhost:8000/api/preferences', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Failed to fetch preferences');
          }

          const data: UserPreferences = await response.json();
          set({ ...data, isLoading: false, error: null });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          set({ isLoading: false, error: errorMessage });
        }
      },

      savePreferences: async () => {
        set({ isLoading: true, error: null });
        try {
          const token = localStorage.getItem('access_token');
          if (!token) {
            throw new Error('Not authenticated');
          }

          const state = get();
          const preferences: UserPreferences = {
            theme: state.theme,
            language: state.language,
            default_search_source: state.default_search_source,
            default_bible_testament: state.default_bible_testament,
            results_per_page: state.results_per_page,
            enable_streaming: state.enable_streaming,
            enable_multi_agent: state.enable_multi_agent,
          };

          const response = await fetch('http://localhost:8000/api/preferences', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(preferences),
          });

          if (!response.ok) {
            throw new Error('Failed to save preferences');
          }

          const data: UserPreferences = await response.json();
          set({ ...data, isLoading: false, error: null });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          set({ isLoading: false, error: errorMessage });
        }
      },

      reset: () => {
        set({ ...DEFAULT_PREFERENCES, error: null });
      },
    }),
    {
      name: 'preferences-storage',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        default_search_source: state.default_search_source,
        default_bible_testament: state.default_bible_testament,
        results_per_page: state.results_per_page,
        enable_streaming: state.enable_streaming,
        enable_multi_agent: state.enable_multi_agent,
      }),
    }
  )
);
