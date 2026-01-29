import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { InlineCitation } from '@/components/compare/inline-citation';

const mockVerseDetail = {
  text: "In the beginning God created the heaven and the earth.",
  book_name: "Genesis",
  chapter: 1,
  verse: 1,
  source: "bible_ot",
  translation: "King James Version with Apocrypha",
  book_nr: 1
};

describe('InlineCitation', () => {
  describe('with verseDetail (HoverCard mode)', () => {
    it('renders as button element', () => {
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()} 
        />
      );
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('displays reference text without brackets', () => {
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()} 
        />
      );
      expect(screen.getByText('Genesis 1:1')).toBeInTheDocument();
    });

    it('has accessible aria-label', () => {
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()} 
        />
      );
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'View Genesis 1:1');
    });

    it('renders HoverCard trigger button', () => {
      const handleNavigate = vi.fn();
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          verseDetail={mockVerseDetail}
          onNavigate={handleNavigate} 
        />
      );
      
      // Verify trigger button exists
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Genesis 1:1');
    });

    it('handles Quran citation format', () => {
      const quranVerse = {
        text: "الحمد لله رب العالمين",
        book_name: "Fatiha",
        chapter: 1,
        verse: 2,
        source: "quran_tr",
        translation: "Diyanet İşleri Başkanlığı Meali",
        surah_id: 1,
        verse_id: 2
      };
      
      render(
        <InlineCitation 
          reference="Bakara:153" 
          verseDetail={quranVerse}
          onNavigate={vi.fn()} 
        />
      );
      expect(screen.getByText('Bakara:153')).toBeInTheDocument();
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'View Bakara:153');
    });
  });

  describe('without verseDetail (fallback mode)', () => {
    it('renders as muted text span', () => {
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          onNavigate={vi.fn()} 
        />
      );
      
      const element = screen.getByText('Genesis 1:1');
      expect(element.tagName).toBe('SPAN');
      expect(element).toHaveClass('text-[var(--color-text-muted)]');
    });

    it('does not render as button when no verseDetail', () => {
      render(
        <InlineCitation 
          reference="Genesis 1:1" 
          onNavigate={vi.fn()} 
        />
      );
      
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });
});
