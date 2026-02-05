import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { SlidingTabs, SearchSource } from '@/components/ui/sliding-tabs';
import { SearchResultCard } from '@/components/search/search-result-card';
import { AIInterpretation } from '@/components/search/ai-interpretation';

// Mock SourceBadge component
vi.mock('@/components/compare/source-badge', () => ({
  SourceBadge: ({ source }: { source: string }) => (
    <span data-testid="source-badge">{source}</span>
  ),
}));

// Mock InlineCitation component
vi.mock('@/components/compare/inline-citation', () => ({
  InlineCitation: ({ reference, onNavigate }: { reference: string; onNavigate?: (ref: string) => void }) => (
    <button data-testid="citation" onClick={() => onNavigate?.(reference)}>
      {reference}
    </button>
  ),
}));

// Mock Framer Motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
}));

describe('SlidingTabs Component', () => {
  const mockOnTabChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all 4 tabs with correct labels', () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    expect(screen.getByText('Quran')).toBeInTheDocument();
    expect(screen.getByText('Old Testament')).toBeInTheDocument();
    expect(screen.getByText('New Testament')).toBeInTheDocument();
    expect(screen.getByText('Apocrypha')).toBeInTheDocument();
  });

  it('shows indicator on active tab', () => {
    const { container } = render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const indicator = container.querySelector('[data-slot="sliding-indicator"]');
    expect(indicator).toBeInTheDocument();
  });

  it('calls onTabChange when tab is clicked', async () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    await userEvent.click(screen.getByText('Old Testament'));
    expect(mockOnTabChange).toHaveBeenCalledWith('ot');
  });

  it('has correct ARIA attributes', () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    // Check tablist role
    expect(screen.getByRole('tablist')).toBeInTheDocument();
    
    // Check tab roles
    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(4);
    
    // Check aria-selected on active tab
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    expect(quranTab).toHaveAttribute('aria-selected', 'true');
    
    // Check aria-selected on inactive tabs
    const otTab = screen.getByRole('tab', { name: /Old Testament/i });
    expect(otTab).toHaveAttribute('aria-selected', 'false');
  });

  it('supports keyboard navigation with ArrowLeft', async () => {
    render(<SlidingTabs activeTab="ot" onTabChange={mockOnTabChange} />);
    
    const otTab = screen.getByRole('tab', { name: /Old Testament/i });
    otTab.focus();
    
    fireEvent.keyDown(otTab, { key: 'ArrowLeft' });
    
    // Should focus on Quran tab (previous)
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    expect(quranTab).toHaveFocus();
  });

  it('supports keyboard navigation with ArrowRight', async () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    quranTab.focus();
    
    fireEvent.keyDown(quranTab, { key: 'ArrowRight' });
    
    // Should focus on Old Testament tab (next)
    const otTab = screen.getByRole('tab', { name: /Old Testament/i });
    expect(otTab).toHaveFocus();
  });

  it('wraps around when navigating left from first tab', async () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    quranTab.focus();
    
    fireEvent.keyDown(quranTab, { key: 'ArrowLeft' });
    
    // Should wrap to Apocrypha tab (last)
    const apocryphaTab = screen.getByRole('tab', { name: /Apocrypha/i });
    expect(apocryphaTab).toHaveFocus();
  });

  it('wraps around when navigating right from last tab', async () => {
    render(<SlidingTabs activeTab="apocrypha" onTabChange={mockOnTabChange} />);
    
    const apocryphaTab = screen.getByRole('tab', { name: /Apocrypha/i });
    apocryphaTab.focus();
    
    fireEvent.keyDown(apocryphaTab, { key: 'ArrowRight' });
    
    // Should wrap to Quran tab (first)
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    expect(quranTab).toHaveFocus();
  });

  it('supports Tab key navigation', () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    expect(quranTab).toHaveAttribute('tabIndex', '0');
    
    // Inactive tabs should have tabIndex -1
    const otTab = screen.getByRole('tab', { name: /Old Testament/i });
    expect(otTab).toHaveAttribute('tabIndex', '-1');
  });

  it('applies active styles to selected tab', () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const quranTab = screen.getByRole('tab', { name: /Quran/i });
    expect(quranTab).toHaveClass('text-white', 'font-semibold');
  });

  it('applies inactive styles to non-selected tabs', () => {
    render(<SlidingTabs activeTab="quran" onTabChange={mockOnTabChange} />);
    
    const otTab = screen.getByRole('tab', { name: /Old Testament/i });
    expect(otTab).toHaveClass('text-zinc-500');
  });
});

describe('SearchResultCard Component', () => {
  const mockSearchResult = {
    source: 'quran',
    reference: 'Bakara:255',
    text: 'Allah! There is no deity but Him, the Ever-Living, the Sustainer of existence. Neither drowsiness overtakes Him nor sleep.',
    score: 0.95,
  };

  const mockOnClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders verse reference correctly', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    expect(screen.getByText('Bakara:255')).toBeInTheDocument();
  });

  it('displays source badge with correct source', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    const badge = screen.getByTestId('source-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('quran');
  });

  it('shows score as percentage', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    expect(screen.getByText('95%')).toBeInTheDocument();
  });

  it('displays verse text', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    expect(screen.getByText(/Allah! There is no deity but Him/)).toBeInTheDocument();
  });

  it('truncates long text with line-clamp', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    const textElement = screen.getByText(/Allah! There is no deity but Him/);
    expect(textElement).toHaveClass('line-clamp-3');
  });

  it('calls onClick when card is clicked', async () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    const card = screen.getByText('Bakara:255').closest('div');
    await userEvent.click(card!);
    
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders external link icon', () => {
    render(<SearchResultCard {...mockSearchResult} onClick={mockOnClick} />);
    
    // ExternalLink icon is rendered (check by class or test-id if added)
    const icon = screen.getByText('95%').parentElement?.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('handles different source types - Old Testament', () => {
    render(
      <SearchResultCard
        source="ot"
        reference="Genesis 1:1"
        text="In the beginning God created the heaven and the earth."
        score={0.88}
        onClick={mockOnClick}
      />
    );
    
    expect(screen.getByText('Genesis 1:1')).toBeInTheDocument();
    expect(screen.getByText('88%')).toBeInTheDocument();
    const badge = screen.getByTestId('source-badge');
    expect(badge).toHaveTextContent('old_testament');
  });

  it('handles different source types - New Testament', () => {
    render(
      <SearchResultCard
        source="nt"
        reference="John 3:16"
        text="For God so loved the world, that he gave his only begotten Son..."
        score={0.92}
        onClick={mockOnClick}
      />
    );
    
    expect(screen.getByText('John 3:16')).toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
    const badge = screen.getByTestId('source-badge');
    expect(badge).toHaveTextContent('new_testament');
  });

  it('handles different source types - Apocrypha', () => {
    render(
      <SearchResultCard
        source="apocrypha"
        reference="Wisdom 1:1"
        text="Love righteousness, ye that be judges of the earth..."
        score={0.85}
        onClick={mockOnClick}
      />
    );
    
    expect(screen.getByText('Wisdom 1:1')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
    const badge = screen.getByTestId('source-badge');
    expect(badge).toHaveTextContent('apocrypha');
  });

  it('rounds score to nearest integer', () => {
    render(
      <SearchResultCard
        {...mockSearchResult}
        score={0.876}
        onClick={mockOnClick}
      />
    );
    
    expect(screen.getByText('88%')).toBeInTheDocument();
  });

  it('handles score of 1.0 correctly', () => {
    render(
      <SearchResultCard
        {...mockSearchResult}
        score={1.0}
        onClick={mockOnClick}
      />
    );
    
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('applies custom className when provided', () => {
    const { container } = render(
      <SearchResultCard
        {...mockSearchResult}
        onClick={mockOnClick}
        className="custom-class"
      />
    );
    
    const card = container.querySelector('.custom-class');
    expect(card).toBeInTheDocument();
  });
});

describe('AIInterpretation Component', () => {
  const mockVerseDetails = {
    'Bakara:255': {
      text: 'Allah! There is no deity but Him...',
      source: 'quran',
      surah_name: 'Bakara',
      verse_id: 255,
    },
    'John 3:16': {
      text: 'For God so loved the world...',
      source: 'new_testament',
      book_name: 'John',
      chapter: 3,
      verse: 16,
    },
  };

  const mockOnNavigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders interpretation text correctly', () => {
    const text = 'This verse emphasizes the concept of divine unity.';
    render(<AIInterpretation text={text} />);
    
    expect(screen.getByText(text)).toBeInTheDocument();
  });

  it('applies serif font class', () => {
    const text = 'This verse emphasizes the concept of divine unity.';
    const { container } = render(<AIInterpretation text={text} />);
    
    // The font-serif class is on the parent div containing the text
    const serifContainer = container.querySelector('.font-serif');
    expect(serifContainer).toBeInTheDocument();
    expect(serifContainer).toHaveTextContent(text);
  });

  it('parses and renders citation links', () => {
    const text = 'The verse [Bakara:255] speaks of divine attributes.';
    render(
      <AIInterpretation
        text={text}
        verseDetails={mockVerseDetails}
        onNavigate={mockOnNavigate}
      />
    );
    
    const citation = screen.getByTestId('citation');
    expect(citation).toBeInTheDocument();
    expect(citation).toHaveTextContent('Bakara:255');
  });

  it('calls onNavigate when citation is clicked', async () => {
    const text = 'The verse [Bakara:255] speaks of divine attributes.';
    render(
      <AIInterpretation
        text={text}
        verseDetails={mockVerseDetails}
        onNavigate={mockOnNavigate}
      />
    );
    
    const citation = screen.getByTestId('citation');
    await userEvent.click(citation);
    
    expect(mockOnNavigate).toHaveBeenCalledWith('Bakara:255');
  });

  it('renders multiple citations correctly', () => {
    const text = 'Compare [Bakara:255] with [John 3:16] for insights.';
    render(
      <AIInterpretation
        text={text}
        verseDetails={mockVerseDetails}
        onNavigate={mockOnNavigate}
      />
    );
    
    const citations = screen.getAllByTestId('citation');
    expect(citations).toHaveLength(2);
    expect(citations[0]).toHaveTextContent('Bakara:255');
    expect(citations[1]).toHaveTextContent('John 3:16');
  });

  it('renders header label', () => {
    const text = 'This verse emphasizes the concept of divine unity.';
    render(<AIInterpretation text={text} />);
    
    expect(screen.getByText('AI Interpretation')).toBeInTheDocument();
  });

  it('renders Sparkles icon in header', () => {
    const text = 'This verse emphasizes the concept of divine unity.';
    const { container } = render(<AIInterpretation text={text} />);
    
    // Check for Sparkles icon (lucide-react renders as svg)
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('handles text without citations', () => {
    const text = 'This is a plain interpretation without any citations.';
    render(<AIInterpretation text={text} onNavigate={mockOnNavigate} />);
    
    expect(screen.getByText(text)).toBeInTheDocument();
    expect(screen.queryByTestId('citation')).not.toBeInTheDocument();
  });

  it('updates when text prop changes (streaming support)', () => {
    const { rerender } = render(
      <AIInterpretation text="Initial text" onNavigate={mockOnNavigate} />
    );
    
    expect(screen.getByText('Initial text')).toBeInTheDocument();
    
    rerender(
      <AIInterpretation text="Updated text with more content" onNavigate={mockOnNavigate} />
    );
    
    expect(screen.getByText('Updated text with more content')).toBeInTheDocument();
    expect(screen.queryByText('Initial text')).not.toBeInTheDocument();
  });

  it('handles empty text gracefully', () => {
    render(<AIInterpretation text="" onNavigate={mockOnNavigate} />);
    
    expect(screen.getByText('AI Interpretation')).toBeInTheDocument();
  });

  it('applies custom className when provided', () => {
    const { container } = render(
      <AIInterpretation
        text="Test text"
        onNavigate={mockOnNavigate}
        className="custom-interpretation"
      />
    );
    
    const element = container.querySelector('.custom-interpretation');
    expect(element).toBeInTheDocument();
  });

  it('handles citations with range references', () => {
    const text = 'See verses [Bakara:1-3] for context.';
    const extendedVerseDetails = {
      ...mockVerseDetails,
      'Bakara:1': { text: 'Verse 1', source: 'quran', surah_name: 'Bakara', verse_id: 1 },
      'Bakara:2': { text: 'Verse 2', source: 'quran', surah_name: 'Bakara', verse_id: 2 },
      'Bakara:3': { text: 'Verse 3', source: 'quran', surah_name: 'Bakara', verse_id: 3 },
    };
    
    render(
      <AIInterpretation
        text={text}
        verseDetails={extendedVerseDetails}
        onNavigate={mockOnNavigate}
      />
    );
    
    // parseCitations should expand range to individual citations
    const citations = screen.getAllByTestId('citation');
    expect(citations.length).toBeGreaterThanOrEqual(1);
  });

  it('provides default empty onNavigate if not provided', () => {
    const text = 'The verse [Bakara:255] speaks of divine attributes.';
    
    // Should not throw error when onNavigate is not provided
    expect(() => {
      render(
        <AIInterpretation
          text={text}
          verseDetails={mockVerseDetails}
        />
      );
    }).not.toThrow();
  });
});
