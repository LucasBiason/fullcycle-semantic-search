import { FC } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatArea } from "./components/ChatArea";
import { useConversations } from "./hooks/useConversations";
import { useHealth } from "./hooks/useHealth";

const App: FC = () => {
  const conversationsState = useConversations();
  const { isOnline } = useHealth();

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      <Sidebar
        conversations={conversationsState.conversations}
        activeId={conversationsState.activeId}
        isOnline={isOnline}
        onNewChat={conversationsState.createConversation}
        onSelectConversation={conversationsState.setActive}
        onDeleteConversation={conversationsState.deleteConversation}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <ChatArea
          activeConversation={conversationsState.activeConversation}
          onAddMessage={conversationsState.addMessage}
          onUpdateTitle={conversationsState.updateConversationTitle}
          onCreateConversation={conversationsState.createConversation}
        />
      </main>
    </div>
  );
};

export default App;
