/** Lightweight i18n module with React context. */

import React, { createContext, useContext, useState, useCallback } from "react";

export type Lang = "zh" | "en";

const MESSAGES: Record<Lang, Record<string, string>> = {
  zh: {
    "app.title": "代码仓库问答助手",
    "app.subtitle": "对您的代码库提问，获取带引用的答案",
    "chat.header": "代码问答",
    "chat.empty": "向您的代码库提问",
    "chat.example": '例如："索引管线是怎么工作的？"',
    "chat.thinking": "思考中",
    "chat.placeholder": "输入你的问题...",
    "chat.send": "发送",
    "chat.clear": "清空",
    "chat.you": "你",
    "chat.assistant": "助手",
    "sidebar.tips": "使用技巧",
    "sidebar.tip1": "询问函数行为、架构或依赖关系",
    "sidebar.tip2": "答案会标注文件：行号引用",
    "sidebar.tip3": "注册一次仓库，之后即可畅聊",
    "sidebar.github": "GitHub",
    "repo.title": "仓库",
    "repo.placeholder": "输入仓库绝对路径",
    "repo.register": "注册",
    "repo.registering": "注册中...",
    "repo.info": "输入本地代码仓库的绝对路径，代理将为其建立索引以便问答。",
    "repo.registered": "仓库已注册 — 状态：",
    "repo.status": "索引状态：",
    "repo.failed": "注册仓库失败",
    "lang.switch": "English",
  },
  en: {
    "app.title": "Code QA Agent",
    "app.subtitle": "Ask questions about your codebase",
    "chat.header": "Code Q&A Chat",
    "chat.empty": "Ask a question about your codebase.",
    "chat.example": 'Example: "How does the indexing pipeline work?"',
    "chat.thinking": "Thinking",
    "chat.placeholder": "Ask about your codebase...",
    "chat.send": "Send",
    "chat.clear": "Clear",
    "chat.you": "You",
    "chat.assistant": "Assistant",
    "sidebar.tips": "Tips",
    "sidebar.tip1": "Ask about function behavior, architecture, or dependencies",
    "sidebar.tip2": "Answers include file:line citations",
    "sidebar.tip3": "Register a repo once, then chat about it",
    "sidebar.github": "GitHub",
    "repo.title": "Repository",
    "repo.placeholder": "/absolute/path/to/repo",
    "repo.register": "Register",
    "repo.registering": "...",
    "repo.info": "Enter the absolute path to a local code repository. The agent will index it for Q&A.",
    "repo.registered": "Repository registered — status: ",
    "repo.status": "Indexing status: ",
    "repo.failed": "Failed to register repository",
    "lang.switch": "中文",
  },
};

interface I18nCtx {
  lang: Lang;
  t: (key: string) => string;
  toggleLang: () => void;
}

const I18nContext = createContext<I18nCtx>({
  lang: "zh",
  t: (k: string) => MESSAGES["zh"][k] ?? k,
  toggleLang: () => {},
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("zh");

  const toggleLang = useCallback(() => {
    setLang((prev) => (prev === "zh" ? "en" : "zh"));
  }, []);

  const t = useCallback(
    (key: string): string => MESSAGES[lang][key] ?? key,
    [lang],
  );

  return (
    <I18nContext.Provider value={{ lang, t, toggleLang }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nCtx {
  return useContext(I18nContext);
}
