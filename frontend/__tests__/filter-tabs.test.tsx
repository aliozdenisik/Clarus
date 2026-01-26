import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { FilterTabs } from '@/components/compare/filter-tabs';

describe('FilterTabs', () => {
  it('renders all 5 filter options', () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />);
    expect(screen.getByText('Tumu')).toBeInTheDocument();
    expect(screen.getByText('Kuran')).toBeInTheDocument();
    expect(screen.getByText('Eski Ahit')).toBeInTheDocument();
    expect(screen.getByText('Yeni Ahit')).toBeInTheDocument();
    expect(screen.getByText('Apokrifa')).toBeInTheDocument();
  });

  it('highlights active tab with aria-selected', () => {
    render(<FilterTabs activeFilter="quran" onFilterChange={vi.fn()} counts={{}} />);
    expect(screen.getByRole('tab', { name: /Kuran/ })).toHaveAttribute('aria-selected', 'true');
  });

  it('has tablist role on container', () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />);
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  it('displays count badges when counts > 0', () => {
    render(
      <FilterTabs 
        activeFilter="all" 
        onFilterChange={vi.fn()} 
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }} 
      />
    );
    expect(screen.getByText('(15)')).toBeInTheDocument();
    expect(screen.getByText('(5)')).toBeInTheDocument();
    expect(screen.getByText('(10)')).toBeInTheDocument();
  });

  it('does not show badge when count is 0', () => {
    render(
      <FilterTabs 
        activeFilter="all" 
        onFilterChange={vi.fn()} 
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }} 
      />
    );
    expect(screen.queryByText('(0)')).not.toBeInTheDocument();
  });

  it('calls onFilterChange when tab clicked', async () => {
    const handleChange = vi.fn();
    render(<FilterTabs activeFilter="all" onFilterChange={handleChange} counts={{}} />);
    await userEvent.click(screen.getByText('Kuran'));
    expect(handleChange).toHaveBeenCalledWith('quran');
  });
});
