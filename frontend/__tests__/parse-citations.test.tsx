import { describe, it, expect } from 'vitest';
import { parseCitations } from '@/lib/utils/parse-citations';

describe('parseCitations', () => {
  it('extracts simple Quran citation', () => {
    const result = parseCitations('Text [Bakara:153] more');
    expect(result).toEqual([
      'Text ',
      { type: 'citation', reference: 'Bakara:153' },
      ' more'
    ]);
  });

  it('handles multiple citations', () => {
    const result = parseCitations('See [Genesis 1:1] and [John 3:16].');
    expect(result.filter(p => typeof p !== 'string')).toHaveLength(2);
  });

  it('handles text without citations', () => {
    const result = parseCitations('Plain text without citations.');
    expect(result).toEqual(['Plain text without citations.']);
  });

  it('handles citations at start and end', () => {
    const result = parseCitations('[Start] middle [End]');
    expect(result).toHaveLength(3);
    expect(result[0]).toEqual({ type: 'citation', reference: 'Start' });
    expect(result[1]).toBe(' middle ');
    expect(result[2]).toEqual({ type: 'citation', reference: 'End' });
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
      expect(parsed[1]).toEqual({ type: 'citation', reference: expected });
    });
  });
});
