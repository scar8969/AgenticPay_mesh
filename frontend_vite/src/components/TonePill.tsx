interface TonePillProps {
  children: string;
  tone?: "neutral" | "accent" | "warning";
}

export default function TonePill({
  children,
  tone = "neutral",
}: TonePillProps) {
  return <span className={`tone-pill tone-pill--${tone}`}>{children}</span>;
}
