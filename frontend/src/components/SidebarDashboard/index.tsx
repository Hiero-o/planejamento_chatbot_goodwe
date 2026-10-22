import { Sidebar, SidebarContent } from "@/components/ui/sidebar";
import { useEffect, useState } from "react";
import { MdOutlineKeyboardArrowDown } from "react-icons/md";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import ContainerChat from "../ContainerChat";
import ContainerMonitoring from "../ContainerMonitoring";
import { Zap, BatteryCharging, Battery, Gauge } from "lucide-react";
import { useRouter } from "next/router";


interface DashboardSummary {
  totalPowerKw: number;
  occupiedChargers: number;
  availableChargers: number;
  accumulatedEnergyKwh: number;
}


export function AppSidebar() {
  const router = useRouter();

  const [summary, setSummary] =
  useState<DashboardSummary | null>(null);

  const [summaryLoading, setSummaryLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadSummary() {
      try {
        const response = await fetch("/api/dashboard/summary");

        if (!response.ok) {
          throw new Error("Falha ao consultar os indicadores.");
        }

        const data =
          (await response.json()) as DashboardSummary;

        if (active) {
          setSummary(data);
        }
      } catch (error) {
        console.error("Erro ao carregar indicadores:", error);

        if (active) {
          setSummary(null);
        }
      } finally {
        if (active) {
          setSummaryLoading(false);
        }
      }
    }

    void loadSummary();

    return () => {
      active = false;
    };
  }, []);

  return (
    
    <>
      <Sidebar>
        <SidebarContent className="p-[0px] mt-[0px] flex items-start justify-start bg-[#0a0a0a]">
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <article className="flex items-center justify-between p-[12px] mb-[0px] border-b border-[#1f1f1f] w-full hover:bg-[#3d3d3d77] cursor-pointer transition-[0.2s]">
                  <div className="flex items-center justify-start">
                    <img
                      className="rounded-full mr-[8px]"
                      height={40}
                      width={40}
                      src="/imageuser.jpg"
                      alt=""
                    />
                    <div>
                      <h1 className="text-[15px] mb-[3px] leading-none">
                        Nome
                      </h1>
                      <p className="text-[11px] text-[#b3b3b3] mt-[0px] leading-none">
                        email@email.com
                      </p>
                    </div>
                  </div>
                  <MdOutlineKeyboardArrowDown size={20} />
                </article>
              }
            />
            <DropdownMenuContent
              className="w-60 rounded-[8px] bg-[#0a0a0a]"
              align="center"
            >
              <DropdownMenuGroup>
                <DropdownMenuLabel>Usuário</DropdownMenuLabel>
                <DropdownMenuItem className="cursor-pointer"
                  onClick={() => router.push("/profile")}
                > 
                  Perfil
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  Configurações
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  Ajuda
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer" onClick={() => router.push("/vehicles")}>
                  Meus Veículos
                </DropdownMenuItem>

                <DropdownMenuItem className="cursor-pointer" onClick={() => router.push("/vehicles")}>
                  Adicionar veículo
                </DropdownMenuItem>

                <DropdownMenuItem className="cursor-pointer" onClick={() => router.push("/charging-sessions")}>
                  Registrar Carregamento
                </DropdownMenuItem>

              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem className="cursor-pointer">
                  Sair
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
          <main className="p-[5px] w-full">
            <p className="text-[#b3b3b3] text-[12px] px-[14px] mb-[5px] mt-[6px]">
              Conversas
            </p>
            <ContainerChat content="Carregador nao funciona" />
            <ContainerChat content="ID do meu carregador" />
            <ContainerChat content="Erro MODBUS 0x0001" />
            <ContainerChat content="Erro de tupla" />
          </main>
          <div className="w-full flex flex-col items-center justify-center">
            <ContainerMonitoring
              label="Potência total (kW)"
              value={
                summaryLoading
                  ? "…"
                  : summary
                    ? summary.totalPowerKw
                    : "—"
              }
              icon={<Zap size={20} />}
            />

            <ContainerMonitoring
              label="Carregadores em uso"
              value={
                summaryLoading
                  ? "…"
                  : summary
                    ? summary.occupiedChargers
                    : "—"
              }
              icon={<BatteryCharging size={20} />}
            />

            <ContainerMonitoring
              label="Carregadores livres"
              value={
                summaryLoading
                  ? "…"
                  : summary
                    ? summary.availableChargers
                    : "—"
              }
              icon={<Battery size={20} />}
            />

            <ContainerMonitoring
              label="Energia acumulada (kWh)"
              value={
                summaryLoading
                  ? "…"
                  : summary
                    ? summary.accumulatedEnergyKwh.toLocaleString(
                        "pt-BR",
                        { maximumFractionDigits: 2 }
                      )
                    : "—"
          }
              icon={<Gauge size={20} />}
            />
          </div>
        </SidebarContent>
      </Sidebar>
    </>
  );
}
