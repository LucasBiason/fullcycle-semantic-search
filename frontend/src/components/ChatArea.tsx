import { FC, memo, useRef, useEffect, useState } from "react";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { EmptyState } from "./EmptyState";
import { sendQuestion } from "../api";
import type { Conversation, Message } from "../types";

interface ChatAreaProps {
  activeConversation: Conversation | null;
  onAddMessage: (conversationId: string, message: Message) => void;
  onUpdateTitle: (id: string, title: string) => void;
  onCreateConversation: () => string;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

const TypingIndicator: FC = () => (
  <div className="flex justify-start gap-3 animate-fade-in-up">
    <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gray-700/50 flex items-center justify-center mt-1">
      <div className="w-3 h-3 rounded-full bg-gray-500 animate-pulse" />
    </div>
    <div className="glass-card rounded-2xl rounded-bl-md px-5 py-3.5">
      <div className="flex items-center gap-1.5" aria-label="Aguardando resposta">
        <span className="block w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="block w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="block w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" />
      </div>
    </div>
  </div>
);

export const ChatArea: FC<ChatAreaProps> = memo(
  ({ activeConversation, onAddMessage, onUpdateTitle, onCreateConversation }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [pendingExample, setPendingExample] = useState<string | undefined>(undefined);

    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [activeConversation?.messages, isLoading]);

    async function handleSubmit(question: string): Promise<void> {
      setPendingExample(undefined);

      let conversationId = activeConversation?.id;
      if (!conversationId) {
        conversationId = onCreateConversation();
      }

      const isFirstMessage =
        !activeConversation || activeConversation.messages.length === 0;

      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content: question,
      };
      onAddMessage(conversationId, userMessage);

      if (isFirstMessage) {
        onUpdateTitle(conversationId, question.slice(0, 50));
      }

      setIsLoading(true);
      try {
        const data = await sendQuestion(question);
        const answer: string =
          typeof data.answer === "string"
            ? data.answer
            : JSON.stringify(data);

        const assistantMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: answer,
        };
        onAddMessage(conversationId, assistantMessage);
      } catch (err) {
        const errorContent =
          err instanceof Error ? err.message : "Erro ao obter resposta";
        const errorMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: `Erro: ${errorContent}. Verifique se o backend esta em execucao.`,
        };
        onAddMessage(conversationId, errorMessage);
      } finally {
        setIsLoading(false);
      }
    }

    function handleSelectExample(question: string): void {
      if (!activeConversation) {
        onCreateConversation();
      }
      setPendingExample(question);
    }

    const hasMessages =
      activeConversation && activeConversation.messages.length > 0;

    return (
      <div className="flex flex-col h-full bg-gray-950">
        {/* Header */}
        {activeConversation && hasMessages && (
          <header className="flex-shrink-0 px-6 py-3.5 border-b border-white/5 bg-gray-950/80 backdrop-blur-sm">
            <h2 className="text-sm font-medium text-gray-400 truncate">
              {activeConversation.title}
            </h2>
          </header>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {!hasMessages ? (
            <EmptyState onSelectExample={handleSelectExample} />
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
              {activeConversation.messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          initialValue={pendingExample}
        />
      </div>
    );
  }
);

ChatArea.displayName = "ChatArea";
