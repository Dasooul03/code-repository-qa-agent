/** Root application component. */

import { ChatWindow } from "./components/ChatWindow";
import { Sidebar } from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import { I18nProvider } from "./i18n";

export default function App() {
  const { messages, isStreaming, error, sessionId, sendMessage, clearMessages } =
    useChat({ repoRoot: "." });

  return (
    <I18nProvider>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            error={error}
            sessionId={sessionId}
            onSend={sendMessage}
            onClear={clearMessages}
          />
        </main>
      </div>
    </I18nProvider>
  );
}
