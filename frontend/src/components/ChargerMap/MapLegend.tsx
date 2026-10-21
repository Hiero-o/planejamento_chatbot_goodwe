import { Circle, CircleDashed, CircleOff } from 'lucide-react'

export default function MapLegend() {
  return (
    <div className="absolute bottom-4 left-4 z-[1000] rounded-lg border border-[#1f1f1f] bg-[#0a0a0a]/95 px-4 py-3 shadow-lg">
      <p className="mb-2 text-xs font-medium text-white">
        Status dos carregadores
      </p>

      <div className="space-y-1.5 text-xs text-[#b3b3b3]">
        <div className="flex items-center gap-2">
          <Circle size={15} color="#2dcf3d"/>
          <span>Disponível</span>
        </div>

        <div className="flex items-center gap-2">
          <CircleDashed size={15} color="#f0d941"/>
          <span>Em uso</span>
        </div>

        <div className="flex items-center gap-2">
          <CircleOff size={15} color="#e01f53"/>
          <span>Offline</span>
        </div>
      </div>
    </div>
  );
}