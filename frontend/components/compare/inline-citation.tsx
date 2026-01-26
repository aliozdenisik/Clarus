interface InlineCitationProps {
  reference: string;
  onClick: () => void;
}

export function InlineCitation({ reference, onClick }: InlineCitationProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Jump to ${reference} reference`}
      className="text-[var(--color-accent-primary)] hover:text-[var(--color-accent-hover)] underline underline-offset-2 decoration-dotted cursor-pointer font-medium"
    >
      [{reference}]
    </button>
  );
}
