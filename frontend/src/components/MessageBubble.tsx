import { FC, memo } from "react";
import ReactMarkdown from "react-markdown";
import { Bot, User } from "lucide-react";
import type { Message } from "../types";

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: FC<MessageBubbleProps> = memo(({ message }) => {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 animate-slide-right">
        <div className="max-w-[75%]">
          <div className="bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-2xl rounded-br-md px-4 py-3 text-sm leading-relaxed shadow-lg shadow-blue-500/10">
            {message.content}
          </div>
        </div>
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center mt-1">
          <User size={14} className="text-blue-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3 animate-slide-left">
      <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gray-700/50 flex items-center justify-center mt-1">
        <Bot size={14} className="text-gray-400" />
      </div>
      <div className="max-w-[85%]">
        <div className="glass-card text-gray-100 rounded-2xl rounded-bl-md px-4 py-3 text-sm leading-relaxed">
          <ReactMarkdown
            components={{
              p: ({ children }) => (
                <p className="mb-2 last:mb-0">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="text-gray-200">{children}</li>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-white">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-gray-300">{children}</em>
              ),
              code: ({ children, className }) => {
                const isBlock = className?.startsWith("language-");
                if (isBlock) {
                  return (
                    <code className="block bg-gray-900/80 rounded-lg px-3 py-2.5 text-xs font-mono text-emerald-400 overflow-x-auto border border-white/5">
                      {children}
                    </code>
                  );
                }
                return (
                  <code className="bg-gray-900/80 rounded-md px-1.5 py-0.5 text-xs font-mono text-emerald-400">
                    {children}
                  </code>
                );
              },
              pre: ({ children }) => (
                <pre className="mb-2 overflow-x-auto">{children}</pre>
              ),
              h1: ({ children }) => (
                <h1 className="text-base font-bold text-white mb-2">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-sm font-bold text-white mb-1.5">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-gray-200 mb-1">{children}</h3>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-blue-500/50 pl-3 italic text-gray-400 mb-2">
                  {children}
                </blockquote>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
});

MessageBubble.displayName = "MessageBubble";
