import { useState, useEffect, useCallback } from "react";
import type { Conversation, Message } from "../types";

const STORAGE_KEY = "semantic-search-conversations";
const ACTIVE_KEY = "semantic-search-active-id";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function loadFromStorage(): Conversation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Conversation[];
  } catch {
    return [];
  }
}

function saveToStorage(conversations: Conversation[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

function loadActiveId(): string | null {
  return localStorage.getItem(ACTIVE_KEY);
}

function saveActiveId(id: string | null): void {
  if (id) {
    localStorage.setItem(ACTIVE_KEY, id);
  } else {
    localStorage.removeItem(ACTIVE_KEY);
  }
}

interface UseConversationsReturn {
  conversations: Conversation[];
  activeId: string | null;
  activeConversation: Conversation | null;
  createConversation: () => string;
  deleteConversation: (id: string) => void;
  setActive: (id: string) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateConversationTitle: (id: string, title: string) => void;
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<Conversation[]>(loadFromStorage);
  const [activeId, setActiveId] = useState<string | null>(loadActiveId);

  useEffect(() => {
    saveToStorage(conversations);
  }, [conversations]);

  useEffect(() => {
    saveActiveId(activeId);
  }, [activeId]);

  const activeConversation =
    conversations.find((c) => c.id === activeId) ?? null;

  const createConversation = useCallback((): string => {
    const id = generateId();
    const newConversation: Conversation = {
      id,
      title: "Nova conversa",
      messages: [],
      createdAt: Date.now(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveId(id);
    return id;
  }, []);

  const deleteConversation = useCallback(
    (id: string): void => {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      setActiveId((prev) => {
        if (prev === id) {
          const remaining = conversations.filter((c) => c.id !== id);
          return remaining.length > 0 ? remaining[0].id : null;
        }
        return prev;
      });
    },
    [conversations]
  );

  const setActive = useCallback((id: string): void => {
    setActiveId(id);
  }, []);

  const addMessage = useCallback(
    (conversationId: string, message: Message): void => {
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== conversationId) return c;
          return { ...c, messages: [...c.messages, message] };
        })
      );
    },
    []
  );

  const updateConversationTitle = useCallback(
    (id: string, title: string): void => {
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== id) return c;
          return { ...c, title };
        })
      );
    },
    []
  );

  return {
    conversations,
    activeId,
    activeConversation,
    createConversation,
    deleteConversation,
    setActive,
    addMessage,
    updateConversationTitle,
  };
}
