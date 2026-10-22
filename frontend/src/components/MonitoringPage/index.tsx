import { MessageCircle } from "lucide-react";
import ChargerMap from "@/components/ChargerMap";

interface MonitoringPageProps {
  onOpenChat: () => void;
}

export default function MonitoringPage({
  onOpenChat,
}: MonitoringPageProps) {
  return (
    <main className="flex h-[calc(100vh-50px)] min-h-0 min-w-0 flex-col">
      <div className="flex min-h-0 w-full min-w-0 flex-1 flex-col p-[10px]">
        {/* Mapa de carregadores */}
        <div className="w-full min-w-0">
          <ChargerMap />
        </div>

        {/* Acesso ao GurAI */}
        <div className="flex flex-1 items-center justify-center">
          <button
            type="button"
            onClick={onOpenChat}
            className="flex items-center justify-center gap-2 rounded-lg border border-border bg-card px-6 py-3 text-sm text-card-foreground transition-colors duration-200 hover:bg-[#f0d941] hover:border-[#f0d941] hover:text-[#070707]"
          >
            <MessageCircle size={18} />
            Conversar com o GurAI
          </button>
        </div>
      </div>
    </main>
  );
}