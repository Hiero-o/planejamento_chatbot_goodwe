import { ReactNode } from "react";
import { LuDot } from "react-icons/lu";

interface CardHeroProps {
    numbering: number,
    title: string,
    icon: ReactNode,
    subtitle: string,
    desc: string,
    img: string,
    content: ReactNode
}

export default function CardHero({ icon, title, desc, numbering, subtitle, img, content }: CardHeroProps) {
    return (
        <article className="relative flex items-center justify-between flex-col rounded-[8px] border border-[#27272A] p-[20px] w-[100%] h-[45vh] bg-[#070707] z-[999]">
            <div>
                <header className="w-full flex items-center justify-between flex-row mb-[30px]">
                    <p className="flex items-center justify-center leading-[0] text-[13px] text-[#b3b3b3]">{numbering} <LuDot /> {title}</p>
                    <p className="text-[#b3b3b3] text-[20px]">{icon}</p>
                </header>
                <div className="flex items-start justify-center flex-col w-full">
                    <h1 className="text-[28px] font-semibold mb-[8px] leading-[1.2]">{subtitle}</h1>
                    <p className="text-[15px] text-[#b3b3b3]">{desc}</p>
                </div>
            </div>
            {content}
        </article>
    )
}