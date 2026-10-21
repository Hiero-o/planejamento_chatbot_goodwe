
import { useState } from "react";
import {
  MessageCircle,
  LineChart,
  Plus,
  PanelLeftIcon,
} from "lucide-react";

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

type DashboardPage = "monitoramento" | "chat";

export default function Dashboard() {
  const [page, setPage] = useState<DashboardPage>("monitoramento");

  return (
    <SidebarProvider>
      <TooltipProvider>
        <div className="flex min-h-screen w-full items-stretch">
          <AppSidebar />

          {/* Barra de navegação por ícones */}
          <nav className="flex shrink-0 flex-col items-center justify-start border-r border-[#1f1f1f] p-[10px]">
            <SidebarCollapsedTrigger />
            <ButtonToggleSideBar />

            {/* Botão para abrir o mapa */}
            <Tooltip>
              <TooltipTrigger>
                <button
                  type="button"
                  onClick={() => setPage("monitoramento")}
                  aria-label="Voltar ao mapa"
                  aria-pressed={page === "monitoramento"}
                  title="Voltar ao mapa"
                  style={{
                    backgroundColor:
                      page === "monitoramento" ? "#1f1f1f" : "transparent",
                  }}
                  className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors hover:bg-[#1f1f1f]"
                >
                  <LineChart size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Voltar ao mapa</p>
              </TooltipContent>
            </Tooltip>

            {/* Botão para abrir o GurAI */}
            <Tooltip>
              <TooltipTrigger>
                <button
                  type="button"
                  onClick={() => setPage("chat")}
                  aria-label="Abrir GurAI"
                  aria-pressed={page === "chat"}
                  title="GurAI"
                  style={{
                    backgroundColor:
                      page === "chat" ? "#1f1f1f" : "transparent",
                  }}
                  className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors hover:bg-[#1f1f1f]"
                >
                  <MessageCircle size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>GurAI</p>
              </TooltipContent>
            </Tooltip>

            {/* Carteira */}
            <Tooltip>
              <TooltipTrigger>
                <WalletPage />
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Carteira</p>
              </TooltipContent>
            </Tooltip>

            {/* Nova conversa: a funcionalidade será implementada depois */}
            <Tooltip>
              <TooltipTrigger>
                <button
                  type="button"
                  title="Nova conversa"
                  aria-label="Nova conversa"
                  className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors hover:bg-[#1f1f1f]"
                >
                  <Plus size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Nova conversa</p>
              </TooltipContent>
            </Tooltip>
          </nav>

          {/* Conteúdo principal */}
          {page === "monitoramento" ? (
            <div className="min-w-0 flex-1">
              <MonitoringPage onOpenChat={() => setPage("chat")} />
            </div>
          ) : (
            <main className="flex min-w-0 flex-1 flex-col">
              <header className="border-b border-[#1f1f1f] p-4">
                <h1 className="text-sm font-medium">GurAI</h1>
                <p className="text-xs text-[#999]">
                  Assistente virtual
                </p>
              </header>

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
                      Converse com o GurAI sobre seus carregadores e sua
                      plataforma.
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
      className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors hover:bg-[#1f1f1f]"
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
          <img
            className="mb-[8px] cursor-pointer rounded-[8px]"
            height={35}
            width={35}
            src="/imageuser.jpg"
            alt="Perfil do usuário"
          />
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
