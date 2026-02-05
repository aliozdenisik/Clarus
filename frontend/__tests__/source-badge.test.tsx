import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SourceBadge } from '@/components/compare/source-badge';

describe('SourceBadge', () => {
  it('renders Quran label for quran source', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByText('Quran')).toBeInTheDocument();
  });

  it('renders Old Testament label for old_testament source', () => {
    render(<SourceBadge source="old_testament" />);
    expect(screen.getByText('Old Testament')).toBeInTheDocument();
  });

  it('renders New Testament label for new_testament source', () => {
    render(<SourceBadge source="new_testament" />);
    expect(screen.getByText('New Testament')).toBeInTheDocument();
  });

  it('renders Apocrypha label for apocrypha source', () => {
    render(<SourceBadge source="apocrypha" />);
    expect(screen.getByText('Apocrypha')).toBeInTheDocument();
  });

  it('applies emerald background for quran source', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByText('Quran')).toHaveClass('bg-emerald-500');
  });

  it('applies blue background for old_testament source', () => {
    render(<SourceBadge source="old_testament" />);
    expect(screen.getByText('Old Testament')).toHaveClass('bg-blue-500');
  });

  it('applies amber background for new_testament source', () => {
    render(<SourceBadge source="new_testament" />);
    expect(screen.getByText('New Testament')).toHaveClass('bg-amber-500');
  });

  it('applies purple background for apocrypha source', () => {
    render(<SourceBadge source="apocrypha" />);
    expect(screen.getByText('Apocrypha')).toHaveClass('bg-purple-500');
  });

  it('has accessible role', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
