export type CitationPart = string | { type: 'citation'; reference: string };

export function parseCitations(content: string): CitationPart[] {
  const parts: CitationPart[] = [];
  const regex = /\[([^\]]+)\]/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(content)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }
    
    // Add citation object
    parts.push({
      type: 'citation',
      reference: match[1]  // Extract text inside brackets (no brackets)
    });
    
    lastIndex = regex.lastIndex;
  }

  // Add remaining text after last citation
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts;
}
