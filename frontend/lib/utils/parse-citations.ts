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
    
    const rawReference = match[1];
    
    // Check if this is a multi-citation (contains comma)
    if (rawReference.includes(',')) {
      // Split by comma and trim whitespace
      const citations = rawReference.split(',').map(c => c.trim());
      
      // Add opening bracket
      parts.push('[');
      
      // Add each citation as separate clickable reference
      citations.forEach((citation, idx) => {
        parts.push({
          type: 'citation',
          reference: citation
        });
        
        // Add comma separator between citations (not after last)
        if (idx < citations.length - 1) {
          parts.push(', ');
        }
      });
      
      // Add closing bracket
      parts.push(']');
    } else {
      // Single citation - wrap with brackets
      parts.push('[');
      parts.push({
        type: 'citation',
        reference: rawReference
      });
      parts.push(']');
    }
    
    lastIndex = regex.lastIndex;
  }

  // Add remaining text after last citation
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts;
}
