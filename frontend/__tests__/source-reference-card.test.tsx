import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SourceReferenceCard } from '@/components/compare/source-reference-card';

describe('SourceReferenceCard', () => {
  const mockVerse = {
    text: 'In the beginning God created the heaven and the earth.',
    book_name: 'Genesis',
    chapter: 1,
    verse: 1,
    source: 'bible_ot',  // Backend format
    translation: 'King James Version with Apocrypha'
  };

  it('renders verse text', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />);
    expect(screen.getByText(/In the beginning/)).toBeInTheDocument();
  });

  it('renders source badge with mapped value', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />);
    expect(screen.getByText('Eski Ahit')).toBeInTheDocument();
  });

  it('renders book name and verse reference', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />);
    expect(screen.getByText('Genesis 1:1')).toBeInTheDocument();
  });

  it('renders translation info', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />);
    expect(screen.getByText('King James Version with Apocrypha')).toBeInTheDocument();
  });

  it('has data-verse-id for scroll targeting', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />);
    expect(screen.getByTestId('verse-card')).toHaveAttribute('data-verse-id', 'Genesis 1:1');
  });

  it('shows highlight ring when isHighlighted is true', () => {
    render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" isHighlighted={true} />);
    const card = screen.getByTestId('verse-card');
    expect(card).toHaveClass('ring-2');
  });

  it('maps quran_tr source to quran badge', () => {
    const quranVerse = { ...mockVerse, source: 'quran_tr', book_name: 'Bakara' };
    render(<SourceReferenceCard verse={quranVerse} reference="Bakara:153" />);
    expect(screen.getByText('Kuran')).toBeInTheDocument();
  });
});
