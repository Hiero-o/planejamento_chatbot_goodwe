import type { ReactNode } from "react";

interface ContainerMonitoringProps {
  label: string;
  value: number | string;
  icon: ReactNode;
}

export default function ContainerMonitoring({
  label,
  value,
  icon,
}: ContainerMonitoringProps) {
  return (
    <article className="flex w-full flex-col items-start justify-center border-b border-[#1f1f1f] p-[18px] first:border-t first:border-[#1f1f1f]">
      <header className="flex w-full flex-row items-center justify-between">
        <p className="mb-[15px] text-[14px] leading-[1.0] text-[#b3b3b3]">
          {label}
        </p>

        <p className="font-extralight text-[#bebebe]">
          {icon}
        </p>
      </header>

      <h2 className="text-[35px] font-semibold leading-[1.0] text-white">
        {value}
      </h2>
    </article>
  );
}