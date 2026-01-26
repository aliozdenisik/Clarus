import { describe, it, expect } from 'vitest';
import { parseCitations } from '@/lib/utils/parse-citations';

describe('parseCitations', () => {
  it('extracts simple Quran citation', () => {
    const result = parseCitations('Text [Bakara:153] more');
    expect(result).toEqual([
      'Text ',
      '[',
      { type: 'citation', reference: 'Bakara:153' },
      ']',
      ' more'
    ]);
  });

  it('handles multiple citations', () => {
    const result = parseCitations('See [Genesis 1:1] and [John 3:16].');
    expect(result.filter(p => typeof p !== 'string' && p.type === 'citation')).toHaveLength(2);
  });

  it('handles text without citations', () => {
    const result = parseCitations('Plain text without citations.');
    expect(result).toEqual(['Plain text without citations.']);
  });

  it('handles citations at start and end', () => {
    const result = parseCitations('[Start] middle [End]');
    expect(result).toHaveLength(7);
    expect(result[0]).toEqual('[');
    expect(result[1]).toEqual({ type: 'citation', reference: 'Start' });
    expect(result[2]).toEqual(']');
    expect(result[3]).toBe(' middle ');
    expect(result[4]).toEqual('[');
    expect(result[5]).toEqual({ type: 'citation', reference: 'End' });
    expect(result[6]).toEqual(']');
  });

  // Edge case tests
  const edgeCases = [
    { input: "Text [1 Corinthians 13:4] more", expected: "1 Corinthians 13:4" },
    { input: "Text [Fâtiha:1] more", expected: "Fâtiha:1" },
    { input: "Text [2 Maccabees 7:9] more", expected: "2 Maccabees 7:9" },
    { input: "Text [Meâric:5] more", expected: "Meâric:5" },
  ];

  edgeCases.forEach(({ input, expected }) => {
    it(`handles edge case: ${expected}`, () => {
      const parsed = parseCitations(input);
      // Brackets are at index 1 and 3, citation is at index 2
      expect(parsed[2]).toEqual({ type: 'citation', reference: expected });
    });
  });

  it('handles multi-citation brackets (comma-separated)', () => {
    const result = parseCitations('Text [Genesis 1:21, Genesis 1:25] more');
    // Should have: 'Text ', '[', {citation: 'Genesis 1:21'}, ', ', {citation: 'Genesis 1:25'}, ']', ' more'
    const citations = result.filter(p => typeof p !== 'string' && p.type === 'citation');
    expect(citations).toHaveLength(2);
    expect(citations[0]).toEqual({ type: 'citation', reference: 'Genesis 1:21' });
    expect(citations[1]).toEqual({ type: 'citation', reference: 'Genesis 1:25' });
  });

  it('handles multi-citation with three references', () => {
    const result = parseCitations('See [Isaiah 43:7, Psalms 104:30, Genesis 2:7] here');
    const citations = result.filter(p => typeof p !== 'string' && p.type === 'citation');
    expect(citations).toHaveLength(3);
    expect(citations[0]).toEqual({ type: 'citation', reference: 'Isaiah 43:7' });
    expect(citations[1]).toEqual({ type: 'citation', reference: 'Psalms 104:30' });
    expect(citations[2]).toEqual({ type: 'citation', reference: 'Genesis 2:7' });
  });
});
