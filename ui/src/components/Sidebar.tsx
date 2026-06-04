/** Sidebar — repository management + quota status + session info + about. */

import { useEffect, useState } from "react";
import { RepositoryPanel } from "./RepositoryPanel";
import { getQuota } from "../api/quota";
import type { QuotaUsage } from "../api/quota";
import { useI18n } from "../i18n";

export function Sidebar() {
  const { t, toggleLang } = useI18n();
  const [quota, setQuota] = useState<QuotaUsage | null>(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getQuota();
        setQuota(data);
      } catch {
        // API not available
      }
    };
    fetch();
    const interval = setInterval(fetch, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const pct = (used: number, limit: number | null) => {
    if (limit === null || limit === 0) return null;
    return Math.round((used / limit) * 100);
  };

  const fmtNum = (n: number): string => {
    if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__brand-row">
          <h1>{t("app.title")}</h1>
          <button className="btn btn--lang" onClick={toggleLang}>
            {t("lang.switch")}
          </button>
        </div>
        <p className="text-muted small">{t("app.subtitle")}</p>
      </div>

      {quota && (
        <div className="sidebar__section sidebar__quota">
          <h3>API Usage</h3>
          <QuotaBar
            label={`Daily Tokens (${quota.daily_tokens.date})`}
            used={quota.daily_tokens.used}
            limit={quota.daily_tokens.limit}
            pct={pct(quota.daily_tokens.used, quota.daily_tokens.limit)}
            fmtNum={fmtNum}
          />
          <QuotaBar
            label="Chat calls"
            used={quota.chat_calls.used}
            limit={quota.chat_calls.limit}
            pct={pct(quota.chat_calls.used, quota.chat_calls.limit)}
          />
          <QuotaBar
            label="Embeddings"
            used={quota.embedding_calls.used}
            limit={quota.embedding_calls.limit}
            pct={pct(quota.embedding_calls.used, quota.embedding_calls.limit)}
          />
          {quota.daily_tokens.limit === null && (
            <p className="small text-muted">No limit set</p>
          )}
        </div>
      )}

      <RepositoryPanel />

      <div className="sidebar__section">
        <h3>{t("sidebar.tips")}</h3>
        <ul className="sidebar__tips">
          <li>{t("sidebar.tip1")}</li>
          <li>{t("sidebar.tip2")}</li>
          <li>{t("sidebar.tip3")}</li>
        </ul>
      </div>

      <div className="sidebar__footer">
        <a
          href="https://github.com/your-org/code-repository-qa-agent"
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted small"
        >
          {t("sidebar.github")}
        </a>
      </div>
    </aside>
  );
}

/** Small progress bar for a single quota metric. */
function QuotaBar({
  label,
  used,
  limit,
  pct,
  fmtNum,
}: {
  label: string;
  used: number;
  limit: number | null;
  pct: number | null;
  fmtNum?: (n: number) => string;
}) {
  if (limit === null || limit === 0) return null;
  const f = fmtNum ?? ((n: number) => String(n));
  const color = pct !== null && pct >= 90 ? "var(--color-error)" : pct !== null && pct >= 75 ? "var(--color-warning)" : "var(--color-primary)";
  const barWidth = pct !== null ? Math.min(pct, 100) : 0;

  return (
    <div className="quota-bar">
      <div className="quota-bar__label">
        <span className="small">{label}</span>
        <span className="small text-muted">
          {f(used)}/{f(limit)}
          {pct !== null && ` (${pct}%)`}
        </span>
      </div>
      <div className="quota-bar__track" style={{ "--bar-color": color } as React.CSSProperties}>
        <div
          className="quota-bar__fill"
          style={{ width: `${barWidth}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
