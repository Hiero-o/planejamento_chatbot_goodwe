import { ReactNode } from "react";
import { LuDot } from "react-icons/lu";

interface CardHeroProps {
  numbering: number;
  title: string;
  icon: ReactNode;
  subtitle: string;
  desc: string;
  img: string;
  content: ReactNode;
}

export default function CardHero({
  icon,
  title,
  desc,
  numbering,
  subtitle,
  content,
}: CardHeroProps) {
  return (
    <article className="relative isolate z-0 flex h-[45vh] w-full flex-col items-center justify-between rounded-lg border border-border bg-card p-5 text-card-foreground">
      <div className="w-full">
        <header className="mb-[30px] flex w-full flex-row items-center justify-between">
          <p className="flex items-center justify-center text-[13px] leading-none text-muted-foreground">
            {numbering}
            <LuDot />
            {title}
          </p>

          <div className="text-[20px] text-muted-foreground">
            {icon}
          </div>
        </header>

        <div className="flex w-full flex-col items-start justify-center">
          <h1 className="mb-2 text-[28px] font-semibold leading-[1.2] text-card-foreground">
            {subtitle}
          </h1>

          <p className="text-[15px] text-muted-foreground">
            {desc}
          </p>
        </div>
      </div>

      <div className="w-full text-card-foreground">
        {content}
      </div>
    </article>
  );
}