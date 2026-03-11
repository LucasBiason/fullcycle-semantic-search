import { FC, memo } from "react";
import { Search, FileText, Lightbulb } from "lucide-react";

interface EmptyStateProps {
  onSelectExample?: (question: string) => void;
}

const EXAMPLE_QUESTIONS = [
  {
    icon: FileText,
    text: "Quais sao os principais topicos abordados no documento?",
  },
  {
    icon: Search,
    text: "Resuma os pontos mais importantes do conteudo.",
  },
  {
    icon: Lightbulb,
    text: "Quais sao as conclusoes apresentadas?",
  },
];

export const EmptyState: FC<EmptyStateProps> = memo(({ onSelectExample }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-8 px-8 text-center">
      {/* Hero */}
      <div className="flex flex-col items-center gap-5">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/15 blur-2xl rounded-full scale-150" />
          <div className="relative p-4 rounded-2xl glass-card">
            <img
              src="/logo.svg"
              alt="Semantic Search logo"
              width={48}
              height={48}
            />
          </div>
        </div>
        <div>
          <h2 className="text-2xl font-bold gradient-text mb-2">
            Semantic Search
          </h2>
          <p className="text-sm text-gray-400 max-w-sm">
            Busca semantica inteligente sobre documentos PDF.
            Faca sua pergunta e receba respostas contextualizadas.
          </p>
        </div>
      </div>

      {/* Example questions */}
      {onSelectExample && (
        <div className="w-full max-w-lg">
          <p className="text-[11px] font-medium text-gray-500 uppercase tracking-wider mb-3">
            Sugestoes para comecar
          </p>
          <div className="grid gap-2">
            {EXAMPLE_QUESTIONS.map(({ icon: Icon, text }) => (
              <button
                key={text}
                onClick={() => onSelectExample(text)}
                className="flex items-center gap-3 text-left px-4 py-3.5 rounded-xl glass-card hover:bg-white/10 text-sm text-gray-300 hover:text-white transition-all duration-200 cursor-pointer group"
              >
                <div className="flex-shrink-0 p-1.5 rounded-lg bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                  <Icon size={15} />
                </div>
                <span>{text}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

EmptyState.displayName = "EmptyState";
