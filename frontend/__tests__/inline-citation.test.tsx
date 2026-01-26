import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { InlineCitation } from '@/components/compare/inline-citation';

describe('InlineCitation', () => {
  it('renders as button element', () => {
    render(<InlineCitation reference="Genesis 1:1" onClick={vi.fn()} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('displays reference text without brackets', () => {
    render(<InlineCitation reference="Genesis 1:1" onClick={vi.fn()} />);
    expect(screen.getByText('Genesis 1:1')).toBeInTheDocument();
  });

  it('has accessible aria-label', () => {
    render(<InlineCitation reference="Genesis 1:1" onClick={vi.fn()} />);
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Jump to Genesis 1:1 reference');
  });

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn();
    render(<InlineCitation reference="Genesis 1:1" onClick={handleClick} />);
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });

  it('handles Quran citation format', () => {
    render(<InlineCitation reference="Bakara:153" onClick={vi.fn()} />);
    expect(screen.getByText('Bakara:153')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Jump to Bakara:153 reference');
  });
});
