import type { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}

export default function SectionCard({
  title,
  subtitle,
  children,
  action,
  className = "",
}: SectionCardProps) {
  return (
    <section className={`section-card ${className}`.trim()}>
      <div className="section-card__header">
        <div>
          <h3 className="section-card__title">{title}</h3>
          {subtitle ? <p className="section-card__subtitle">{subtitle}</p> : null}
        </div>
        {action ? <div>{action}</div> : null}
      </div>
      {children}
    </section>
  );
}
