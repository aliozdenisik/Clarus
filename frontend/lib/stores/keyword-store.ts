'use client';

import { create } from 'zustand';

export interface KeywordSuggestion {
  text: string;
  language: string;
  confidence: number;
  selected: boolean;
  source: string;
}

interface KeywordStore {
  advancedMode: boolean;
  keywords: KeywordSuggestion[];
  selectedKeywords: KeywordSuggestion[];
  isLoading: boolean;
  setAdvancedMode: (mode: boolean) => void;
  setKeywords: (keywords: KeywordSuggestion[]) => void;
  toggleKeyword: (keyword: KeywordSuggestion) => void;
  selectAll: () => void;
  deselectAll: () => void;
  reset: () => void;
}

export const useKeywordStore = create<KeywordStore>((set, get) => ({
  advancedMode: false,
  keywords: [],
  selectedKeywords: [],
  isLoading: false,

  setAdvancedMode: (mode) => {
    set({ advancedMode: mode });
  },

  setKeywords: (keywords) => {
    const selected = keywords.filter((k) => k.selected);
    set({ keywords, selectedKeywords: selected, isLoading: false });
  },

  toggleKeyword: (keyword) => {
    const { keywords, selectedKeywords } = get();
    const isSelected = selectedKeywords.some((k) => k.text === keyword.text);

    if (isSelected) {
      // Deselect
      const newSelected = selectedKeywords.filter((k) => k.text !== keyword.text);
      const newKeywords = keywords.map((k) =>
        k.text === keyword.text ? { ...k, selected: false } : k
      );
      set({ selectedKeywords: newSelected, keywords: newKeywords });
    } else {
      // Select
      const newSelected = [...selectedKeywords, { ...keyword, selected: true }];
      const newKeywords = keywords.map((k) =>
        k.text === keyword.text ? { ...k, selected: true } : k
      );
      set({ selectedKeywords: newSelected, keywords: newKeywords });
    }
  },

  selectAll: () => {
    const { keywords } = get();
    const allSelected = keywords.map((k) => ({ ...k, selected: true }));
    set({ keywords: allSelected, selectedKeywords: allSelected });
  },

  deselectAll: () => {
    const { keywords } = get();
    const allDeselected = keywords.map((k) => ({ ...k, selected: false }));
    set({ keywords: allDeselected, selectedKeywords: [] });
  },

  reset: () => {
    set({
      advancedMode: false,
      keywords: [],
      selectedKeywords: [],
      isLoading: false,
    });
  },
}));
