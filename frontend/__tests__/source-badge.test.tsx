import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SourceBadge } from '@/components/compare/source-badge';

describe('SourceBadge', () => {
  it('renders Kuran label for quran source', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByText('Kuran')).toBeInTheDocument();
  });

  it('renders Eski Ahit label for old_testament source', () => {
    render(<SourceBadge source="old_testament" />);
    expect(screen.getByText('Eski Ahit')).toBeInTheDocument();
  });

  it('renders Yeni Ahit label for new_testament source', () => {
    render(<SourceBadge source="new_testament" />);
    expect(screen.getByText('Yeni Ahit')).toBeInTheDocument();
  });

  it('renders Apokrifa label for apocrypha source', () => {
    render(<SourceBadge source="apocrypha" />);
    expect(screen.getByText('Apokrifa')).toBeInTheDocument();
  });

  it('applies emerald background for quran source', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByText('Kuran')).toHaveClass('bg-emerald-500');
  });

  it('applies blue background for old_testament source', () => {
    render(<SourceBadge source="old_testament" />);
    expect(screen.getByText('Eski Ahit')).toHaveClass('bg-blue-500');
  });

  it('applies amber background for new_testament source', () => {
    render(<SourceBadge source="new_testament" />);
    expect(screen.getByText('Yeni Ahit')).toHaveClass('bg-amber-500');
  });

  it('applies purple background for apocrypha source', () => {
    render(<SourceBadge source="apocrypha" />);
    expect(screen.getByText('Apokrifa')).toHaveClass('bg-purple-500');
  });

  it('has accessible role', () => {
    render(<SourceBadge source="quran" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
