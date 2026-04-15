import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

interface AppShellProps {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  actions?: ReactNode;
}

const navItems = [
  { to: "/", label: "Overview", end: true },
  { to: "/demo", label: "Demo Run" },
  { to: "/transactions", label: "Ledger" },
];

export default function AppShell({
  eyebrow,
  title,
  description,
  children,
  actions,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <div className="app-shell__ambient" aria-hidden="true" />
      <header className="topbar">
        <div className="topbar__inner">
          <div className="brand-lockup">
            <div className="brand-mark">
              <span />
            </div>
            <div>
              <p className="brand-kicker">AgentPay Mesh</p>
              <h1 className="brand-title">Fintech orchestration demo</h1>
            </div>
          </div>

          <nav className="topnav" aria-label="Primary">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `topnav__link${isActive ? " topnav__link--active" : ""}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="page-frame">
        <section className="hero-panel">
          <div>
            <p className="hero-panel__eyebrow">{eyebrow}</p>
            <h2 className="hero-panel__title">{title}</h2>
            <p className="hero-panel__description">{description}</p>
          </div>
          {actions ? <div className="hero-panel__actions">{actions}</div> : null}
        </section>

        {children}
      </main>
    </div>
  );
}
