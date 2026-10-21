import { ReactNode } from "react";

interface ContainerMonitoringProps {
  label: string
  value: number
  icon: ReactNode
}

export default function ContainerMonitoring({ label, value, icon }: ContainerMonitoringProps) {
  return (
    <article className="flex items-start justify-center flex-col border-b border-[#1f1f1f] w-full p-[18px] first:border-t first:border-[#1f1f1f]">
      <header className="flex items-center justify-between flex-row w-full">
        <p className="text-[14px] text-[#b3b3b3] mb-[15px] leading-[1.0]">{label}</p>
        <p className="text-[#bebebe] font-extralight">{icon}</p>
      </header>
      <h1 className="text-[35px] text-[#fff] leading-[1.0] font-semibold">{value}</h1>
    </article>
  );
}
