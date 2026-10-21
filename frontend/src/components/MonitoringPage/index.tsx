
import { MessageCircle } from "lucide-react";
import ChargerMap from "@/components/ChargerMap";

interface MonitoringPageProps {
  onOpenChat: () => void;
}

export default function MonitoringPage({
  onOpenChat,
}: MonitoringPageProps) {
  return (
    <main className="flex h-screen w-full min-w-0 flex-col">
      <header className="w-full border-b border-[#1f1f1f] p-[12px]">
        <h1 className="text-[14px]">Monitoramento</h1>
      </header>

      <div className="flex min-h-0 w-full min-w-0 flex-1 flex-col p-[10px]">
        {/* O mapa ocupa toda a largura disponível */}
        <div className="w-full min-w-0">
          <ChargerMap />
        </div>

        {/* Somente o botão é centralizado */}
        <div className="flex flex-1 items-center justify-center">
          <button
            type="button"
            onClick={onOpenChat}
            className="flex items-center justify-center gap-2 rounded-[8px] border border-[#333] bg-[#151515] px-6 py-3 text-sm text-white transition-colors hover:bg-[#222]"
          >
            <MessageCircle size={18} />
            Conversar com o GurAI
          </button>
        </div>
      </div>
    </main>
  );
}
