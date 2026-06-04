/** Repository management panel — register repo and check indexing status. */

import { useState, useCallback } from "react";
import { registerRepository, getRepoStatus } from "../api/repositories";
import { useI18n } from "../i18n";

type RepoStatus = "idle" | "queued" | "indexing" | "ready" | "error";

export function RepositoryPanel() {
  const { t } = useI18n();
  const [repoPath, setRepoPath] = useState("");
  const [status, setStatus] = useState<RepoStatus>("idle");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = useCallback(async () => {
    const path = repoPath.trim();
    if (!path) return;

    setLoading(true);
    setMessage("");

    try {
      const res = await registerRepository(path);
      setStatus(res.status as RepoStatus);
      setMessage(`${t("repo.registered")}${res.status}`);
      if (res.status !== "ready") {
        pollStatus(path);
      }
    } catch (err: unknown) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : t("repo.failed"));
    } finally {
      setLoading(false);
    }
  }, [repoPath, t]);

  const pollStatus = useCallback(async (path: string) => {
    const poll = async () => {
      try {
        const res = await getRepoStatus(path);
        setStatus(res.status as RepoStatus);
        setMessage(`${t("repo.status")}${res.status}`);
        if (res.status === "ready" || res.status.startsWith("error")) {
          return;
        }
        setTimeout(poll, 2000);
      } catch {
        setTimeout(poll, 2000);
      }
    };
    setTimeout(poll, 2000);
  }, [t]);

  return (
    <div className="repository-panel">
      <h3>{t("repo.title")}</h3>

      <div className="repository-panel__form">
        <input
          className="input"
          type="text"
          value={repoPath}
          onChange={(e) => setRepoPath(e.target.value)}
          placeholder={t("repo.placeholder")}
          disabled={loading}
        />
        <button
          className="btn btn--primary btn--small"
          onClick={handleRegister}
          disabled={!repoPath.trim() || loading}
        >
          {loading ? t("repo.registering") : t("repo.register")}
        </button>
      </div>

      {message && (
        <div className={`repository-panel__status repository-panel__status--${status}`}>
          {status === "indexing" && <span className="spinner" />}
          {message}
        </div>
      )}

      <div className="repository-panel__info">
        <p className="text-muted small">{t("repo.info")}</p>
      </div>
    </div>
  );
}
