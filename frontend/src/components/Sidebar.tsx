import { FC, memo } from "react";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import type { Conversation } from "../types";

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  isOnline: boolean;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const ConversationItem: FC<ConversationItemProps> = memo(
  ({ conversation, isActive, onSelect, onDelete }) => {
    return (
      <li className="group relative">
        <button
          onClick={onSelect}
          className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all duration-200 cursor-pointer flex items-center gap-2.5 ${
            isActive
              ? "bg-white/10 text-white shadow-sm shadow-blue-500/5 border border-white/10"
              : "text-gray-400 hover:bg-white/5 hover:text-gray-200 border border-transparent"
          }`}
          aria-current={isActive ? "page" : undefined}
        >
          <MessageSquare
            size={14}
            className={`flex-shrink-0 ${isActive ? "text-blue-400" : "text-gray-600"}`}
            aria-hidden="true"
          />
          <span className="block truncate pr-5">{conversation.title}</span>
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-md text-gray-600 hover:text-red-400 hover:bg-red-400/10 opacity-0 group-hover:opacity-100 transition-all duration-200"
          aria-label={`Deletar conversa: ${conversation.title}`}
        >
          <Trash2 size={13} />
        </button>
      </li>
    );
  }
);

ConversationItem.displayName = "ConversationItem";

export const Sidebar: FC<SidebarProps> = memo(
  ({
    conversations,
    activeId,
    isOnline,
    onNewChat,
    onSelectConversation,
    onDeleteConversation,
  }) => {
    const sorted = [...conversations].sort((a, b) => b.createdAt - a.createdAt);

    return (
      <aside
        className="sidebar-gradient w-[280px] flex-shrink-0 border-r border-white/5 flex flex-col"
        aria-label="Painel lateral"
      >
        {/* Branding */}
        <div className="flex items-center gap-3 px-5 pt-6 pb-2">
          <div className="relative">
            <div className="absolute inset-0 bg-blue-500/20 blur-lg rounded-full" />
            <img
              src="/logo.svg"
              alt="Semantic Search logo"
              width={32}
              height={32}
              className="relative"
            />
          </div>
          <div>
            <h1 className="text-sm font-bold gradient-text leading-tight tracking-tight">
              Semantic Search
            </h1>
            <p className="text-[11px] text-gray-500 leading-tight mt-0.5">
              Busca inteligente em documentos
            </p>
          </div>
        </div>

        {/* New chat button */}
        <div className="px-4 py-4">
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-medium transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 cursor-pointer active:scale-[0.98]"
            aria-label="Criar nova conversa"
          >
            <Plus size={16} aria-hidden="true" />
            Nova conversa
          </button>
        </div>

        {/* Conversations label */}
        <div className="px-5 pb-2">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">
            Conversas
          </span>
        </div>

        {/* Conversation list */}
        <nav className="flex-1 overflow-y-auto px-3 pb-3" aria-label="Conversas">
          {sorted.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 px-4">
              <MessageSquare size={24} className="text-gray-700 mb-2" />
              <p className="text-xs text-gray-600 text-center">
                Nenhuma conversa ainda
              </p>
            </div>
          ) : (
            <ul className="space-y-0.5" role="list">
              {sorted.map((conversation) => (
                <ConversationItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === activeId}
                  onSelect={() => onSelectConversation(conversation.id)}
                  onDelete={() => onDeleteConversation(conversation.id)}
                />
              ))}
            </ul>
          )}
        </nav>

        {/* Backend status */}
        <div
          className="px-4 py-3 border-t border-white/5"
          aria-live="polite"
          aria-label="Status do backend"
        >
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span
                className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isOnline ? "bg-emerald-400 animate-ping" : "bg-red-400"
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isOnline ? "bg-emerald-400" : "bg-red-500"
                }`}
              />
            </span>
            <span className="text-[11px] text-gray-500">
              {isOnline ? "Backend conectado" : "Backend offline"}
            </span>
          </div>
        </div>
      </aside>
    );
  }
);

Sidebar.displayName = "Sidebar";
