interface StatCardProps {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "accent" | "warning";
}

export default function StatCard({
  label,
  value,
  detail,
  tone = "default",
}: StatCardProps) {
  return (
    <article className={`stat-card stat-card--${tone}`}>
      <p className="stat-card__label">{label}</p>
      <p className="stat-card__value">{value}</p>
      <p className="stat-card__detail">{detail}</p>
    </article>
  );
}
