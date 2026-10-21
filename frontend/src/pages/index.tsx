import { useEffect, useState } from "react";
import { MdArrowOutward } from "react-icons/md";
import type { IconType } from "react-icons";
import { IoShieldCheckmark } from "react-icons/io5";
import { TbConnection } from "react-icons/tb";
import { GrResources } from "react-icons/gr";
import CardHero from "@/components/CardHero";
import { ReactNode } from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { type CarouselApi } from "@/components/ui/carousel";
import { MdKeyboardArrowRight, MdKeyboardArrowLeft } from "react-icons/md";
import { IoIosArrowForward } from "react-icons/io";
import { LuDot } from "react-icons/lu";
import { MdElectricBolt } from "react-icons/md";
import Header from '@/components/Header'

interface Notification {
  numbering: number;
  title: string;
  subtitle: string;
  desc: string;
  content: ReactNode;
  img: string;
  icon: IconType;
}

type Item = Notification & { id: number };

const mockMessages: Notification[] = [
  {
    numbering: 1,
    title: "MONITORAMENTO",
    subtitle: "Cada carregador sob controle",
    desc: "O GurAI consulta status, potência e energia consumida de cada carregador em tempo real.",
    content: (
      <div className="w-full flex items-center justify-between flex-row">
        <p className="text-[12px]">Carregador</p>
        <div className="flex items-center justify-center flex-row">
          <div className="h-[0.5px] p-[0.5px] w-[200px] bg-[#8a8a8a]"></div>
          <IoIosArrowForward color="#8a8a8a" />
        </div>
        <p className="text-[12px]">Status</p>
      </div>
    ),
    img: "/image1.png",
    icon: MdElectricBolt,
  },
  {
    numbering: 2,
    title: "INTELIGÊNCIA",
    subtitle: "Respostas confiáveis, sem alucinar",
    desc: "Com RAG e validação documental, o GurAI interpreta manuais GoodWe e o protocolo MODBUS com precisão.",
    content: (
      <div className="w-full flex items-center justify-between flex-row">
        <p className="text-[12px]">Manuais</p>
        <LuDot />
        <p className="text-[12px]">MODBUS</p>
        <LuDot />
        <p className="text-[12px]">RAG</p>
      </div>
    ),
    img: "/image2.png",
    icon: IoShieldCheckmark,
  },
  {
    numbering: 3,
    title: "OPERAÇÃO",
    subtitle: "Toda a planta, em um só lugar.",
    desc: "Uma interface única reúne potência total, energia consumida e disponibilidade dos carregadores.",
    content: (
      <div className="w-full flex items-center justify-between flex-row">
        <div className="flex items-start justify-center flex-col">
          <p className="text-[12px]">Potência</p>
          <p className="text-[12px]">Energia</p>
        </div>
        <div className="flex items-start justify-center flex-col">
          <p className="text-[12px]">Disponíveis</p>
          <p className="text-[12px]">Em uso</p>
        </div>
        <div className="flex items-start justify-center flex-col">
          <p className="text-[12px]">Tarifação</p>
          <p className="text-[12px]">Suporte</p>
        </div>
      </div>
    ),
    img: "/image4.png",
    icon: GrResources,
  },
];

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [api, setApi] = useState<CarouselApi>();

  useEffect(() => {
    let idCounter = 0;

    const addItem = () => {
      const random =
        mockMessages[Math.floor(Math.random() * mockMessages.length)];

      const newItem: Item = {
        id: idCounter++,
        ...random,
      };

      setItems((prev) => [newItem, ...prev].slice(0, 1));
    };

    addItem();

    const interval = setInterval(addItem, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Header />
      <main className="flex items-center justify-center flex-row min-h-[calc(70vh-80px)]">
        <div className="flex items-center justify-between w-[90%] max-w-[1000px] flex-col 2xl:flex-row ">
          <div className="flex items-start justify-center flex-col w-[100%] md:w-[55%]">
            <h1 className="text-[50px] font-bold leading-[1.20] mb-[20px]">
              Assistente inteligente para gerenciamento operacional de eletropostos.
            </h1>
            <p className="mb-[20px] text-[#B3B3B3]">
              Eletropostos públicos e semi-públicos enfrentam novos desafios com a mobilidade elétrica: energia, autenticação, tarifação dinâmica e suporte.
            </p>
            <div className="flex items-center justify-center gap-[10px] flex-row">
              <button className="rounded-[8px] py-[6px] px-[15px] text-[14px] bg-[#f0d941] text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f]">
                Experimentar
              </button>
              <button className="flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A]">
                Saiba mais <MdArrowOutward className="ml-[5px]" size={18} />
              </button>
            </div>
          </div>
          <div className="flex items-center justify-center w-[100%] flex-col md:w-[40%]">
            <Carousel setApi={setApi} className="w-full">
              <CarouselContent>
                {mockMessages.map((item) => {
                  const Icon = item.icon;
                  return (
                    <CarouselItem>
                      <CardHero
                        img={item.img}
                        content={item.content}
                        subtitle={item.subtitle}
                        numbering={item.numbering}
                        desc={item.desc}
                        title={item.title}
                        icon={<Icon />}
                      />
                    </CarouselItem>
                  );
                })}
              </CarouselContent>
              <CarouselPrevious className="hidden" />
              <CarouselNext className="hidden" />
            </Carousel>
            <div className="flex items-center justify-end w-full flex-row mt-[10px] gap-[10px]">
              <button
                className="p-[5px] border border-[#27272A] rounded-[8px] cursor-pointer transition-[0.2s] hover:bg-[#27272A]"
                onClick={() => api?.scrollPrev()}
              >
                <MdKeyboardArrowLeft size={22} color="#b3b3b3" />
              </button>
              <button
                className="p-[5px] border border-[#27272A] rounded-[8px] cursor-pointer transition-[0.2s] hover:bg-[#27272A]"
                onClick={() => api?.scrollNext()}
              >
                <MdKeyboardArrowRight size={22} color="#b3b3b3" />
              </button>
            </div>
          </div>
        </div>
      </main>
      <main className="flex items-center justify-center flex-col min-h-[75vh]">
        <div className="flex items-start justify-between w-[90%] max-w-[1000px] flex-col">
          <div className=" rounded-[8px] border drop-shadow-[0px_0px_200px_rgba(177,177,177,0.055)]">
            <img
              className="rounded-[8px]"
              src="/img.png"
              alt="Image Dashboard"
            />
          </div>
          <span className="text-[13px] text-[#f0d941] mt-[15px]">
            Plataforma
          </span>
          <h1 className="text-[35px] font-semibold mb-[4px]">
            Sua operação, do seu jeito
          </h1>
          <p className="text-[15px] text-[#b3b3b3] w-[70%]">
            Um ambiente intuitivo para configurar, acompanhar e expandir sua
            operação. Tudo permanece conectado, organizado e sob o seu controle.
          </p>
        </div>
      </main>
    </>
  );
}
