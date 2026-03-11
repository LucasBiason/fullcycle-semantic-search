import { FC, memo, useState, useRef, KeyboardEvent, useEffect } from "react";
import { SendHorizontal } from "lucide-react";

interface ChatInputProps {
  onSubmit: (value: string) => void;
  isLoading: boolean;
  initialValue?: string;
}

export const ChatInput: FC<ChatInputProps> = memo(
  ({ onSubmit, isLoading, initialValue }) => {
    const [value, setValue] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
      if (initialValue) {
        setValue(initialValue);
        textareaRef.current?.focus();
      }
    }, [initialValue]);

    function handleSubmit(): void {
      const trimmed = value.trim();
      if (!trimmed || isLoading) return;
      onSubmit(trimmed);
      setValue("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }

    function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>): void {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    }

    function handleInput(): void {
      const el = textareaRef.current;
      if (!el) return;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }

    return (
      <div className="border-t border-white/5 bg-gray-950/80 backdrop-blur-sm px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-3 glass-card rounded-xl px-4 py-3 input-glow focus-within:border-blue-500/50 transition-all duration-300">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onInput={handleInput}
              placeholder="Faca uma pergunta sobre o documento..."
              rows={1}
              disabled={isLoading}
              className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 resize-none outline-none leading-relaxed disabled:opacity-50 min-h-[24px] max-h-40 overflow-y-auto"
              aria-label="Campo de pergunta"
              aria-describedby="chat-input-hint"
            />
            <button
              onClick={handleSubmit}
              disabled={!value.trim() || isLoading}
              className="flex-shrink-0 p-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-500/20 cursor-pointer active:scale-95"
              aria-label="Enviar pergunta"
            >
              <SendHorizontal size={16} aria-hidden="true" />
            </button>
          </div>
          <p id="chat-input-hint" className="sr-only">
            Pressione Enter para enviar ou Shift+Enter para nova linha
          </p>
        </div>
      </div>
    );
  }
);

ChatInput.displayName = "ChatInput";
