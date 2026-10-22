
import { useState } from "react";
import {
  MessageCircle,
  LineChart,
  Plus,
  PanelLeftIcon,
  BatteryCharging,
} from "lucide-react";

import Header from "@/components/Header";

import { AppSidebar } from "@/components/SidebarDashboard";
import {
  useSidebar,
  SidebarProvider,
} from "@/components/ui/sidebar";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import WalletPage from "@/components/WalletComponent";
import MonitoringPage from "@/components/MonitoringPage";

import { useRouter } from "next/router";

type DashboardPage = "monitoramento" | "chat";

export default function Dashboard() {
  const [page, setPage] =
    useState<DashboardPage>("monitoramento");

    const router = useRouter();

  return (
    <SidebarProvider>
      <TooltipProvider>
        <div className="flex min-h-screen w-full items-stretch">
          <AppSidebar />

          {/* Barra de navegação por ícones */}
          <nav className="flex shrink-0 flex-col items-center justify-start border-r border-[#1f1f1f] p-[10px]">
            <SidebarCollapsedTrigger />
            <ButtonToggleSideBar />

            {/* Botão de monitoramento */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => setPage("monitoramento")}
                aria-label="Voltar ao mapa"
                aria-pressed={page === "monitoramento"}
                title="Voltar ao mapa"
                
                className={`mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707] ${
                  page === "monitoramento" ? "bg-[#1f1f1f]" : "bg-transparent"
                }`}
              >
                <LineChart size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Monitoramento
              </TooltipContent>
            </Tooltip>

            {/* Botão do GurAI */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => setPage("chat")}
                aria-label="Abrir GurAI"
                aria-pressed={page === "chat"}
                title="GurAI"
                
                className={`mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707] ${
                  page === "chat" ? "bg-[#1f1f1f]" : "bg-transparent"
                }`}
              >
                <MessageCircle size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                GurAI
              </TooltipContent>
            </Tooltip>

            {/* Carteira
                O componente é renderizado diretamente para evitar
                um possível botão dentro do TooltipTrigger. */}
            <div className="mb-[8px]">
              <WalletPage />
            </div>

            {/* Registrar nova sessão de carregamento */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => void router.push("/charging-sessions")}
                aria-label="Registrar carregamento"
                title="Registrar carregamento"
                className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
              >
                <BatteryCharging size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Adicionar sessão de carregamento
              </TooltipContent>
            </Tooltip>

            {/* Nova conversa */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => setPage("chat")}
                title="Nova conversa"
                aria-label="Nova conversa"
                className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
              >
                <Plus size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Nova conversa
              </TooltipContent>
            </Tooltip>
          </nav>

          {/* Conteúdo principal */}
          <div className="flex min-h-screen min-w-0 flex-1 flex-col">
            {/* Barra superior compartilhada */}
            <div className="flex h-[50px] shrink-0 items-center justify-between gap-3 border-b border-border px-3">
              <div className="min-w-0">
                <h1 className="text-sm font-medium">
                  {page === "monitoramento" ? "Monitoramento" : "GurAI"}
                </h1>

                {page === "chat" && (
                  <p className="text-xs text-muted-foreground">
                    Assistente virtual
                  </p>
                )}
              </div>

              <Header variant="dashboard" />
            </div>

            {/* Conteúdo da página selecionada */}
            {page === "monitoramento" ? (
              <div className="min-h-0 min-w-0 flex-1">
                <MonitoringPage
                  onOpenChat={() => setPage("chat")}
                />
              </div>
            ) : (
              <main className="flex min-h-0 min-w-0 flex-1 flex-col">
                <section className="flex flex-1 flex-col items-center justify-center p-6">
                  <div className="w-full max-w-3xl">
                    <div className="mb-6 text-center">
                      <MessageCircle
                        size={36}
                        className="mx-auto mb-3 text-[#999]"
                      />

                      <h2 className="text-xl font-semibold">
                        Como posso ajudar?
                      </h2>

                      <p className="mt-2 text-sm text-[#999]">
                        Converse com o GurAI sobre seus carregadores
                        e sua plataforma.
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <input
                        type="text"
                        disabled
                        placeholder="O envio de mensagens será implementado depois..."
                        aria-label="Mensagem para o GurAI"
                        className="min-w-0 flex-1 rounded-lg border border-[#333] bg-[#151515] px-4 py-3 text-sm outline-none disabled:cursor-not-allowed disabled:opacity-60"
                      />

                      <button
                        type="button"
                        disabled
                        title="Integração com o backend ainda não implementada"
                        className="rounded-lg bg-white px-4 text-black opacity-50"
                      >
                        Enviar
                      </button>
                    </div>
                  </div>
                </section>
              </main>
            )}
          </div>
        </div>
      </TooltipProvider>
    </SidebarProvider>
  );
}

function ButtonToggleSideBar() {
  const { toggleSidebar } = useSidebar();

  return (
    <button
      type="button"
      onClick={toggleSidebar}
      aria-label="Expandir ou recolher a barra lateral"
      title="Expandir ou recolher a barra lateral"
      className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
    >
      <PanelLeftIcon size={16} />
    </button>
  );
}

function SidebarCollapsedTrigger() {
  const { state } = useSidebar();

  if (state !== "collapsed") return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <button
            type="button"
            aria-label="Abrir menu do usuário"
            title="Menu do usuário"
            className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f]"
          >
            <img
              height={35}
              width={35}
              src="/imageuser.jpg"
              alt=""
              className="rounded-[8px]"
            />
          </button>
        }
      />

      <DropdownMenuContent
        className="w-60 rounded-[8px] bg-[#0a0a0a]"
        align="start"
      >
        <DropdownMenuGroup>
          <DropdownMenuLabel>Usuário</DropdownMenuLabel>

          <DropdownMenuItem className="cursor-pointer">
            Perfil
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Configurações
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Ajuda
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Adicionar veículo
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
  );
}
