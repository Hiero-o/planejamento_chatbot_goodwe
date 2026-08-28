import { AppSidebar } from "@/components/SidebarDashboard";
import { SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Plus, Wallet } from "lucide-react";
import { MessageCircle, LineChart, ReceiptText, ToggleRightIcon } from "lucide-react";
import { PanelLeftIcon } from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { TooltipProvider } from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarProvider } from "@/components/ui/sidebar";
import { GetServerSideProps } from "next";
import { getSession } from "next-auth/react";
import ContainerMonitoring from "@/components/ContainerMonitoring";
import { useState } from "react";
import WalletPage from "@/components/WalletComponent";
import MonitoringPage from "@/components/MonitoringPage";

export default function Dashboard() {
  const [page, setPage] = useState('monitoramento')

  return (
    <SidebarProvider>
      <TooltipProvider>
        <main className="flex items-start justify-center flex-row w-full">
          <AppSidebar />
          <div className="flex items-center justify-start border-r border-[#1f1f1f] h-full p-[10px] flex-col">
            <SidebarCollapsedTrigger />
            <ButtonToggleSideBar />
            <Tooltip>
              <TooltipTrigger>
                <button onClick={() => setPage('monitoramento')} style={{ backgroundColor: page === 'monitoramento' ? '#1f1f1f' : 'transparent' }} className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition-[0.2s] cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger">
                  <LineChart size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Monitoramento</p>
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger>
                <button className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition-[0.2s] cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger">
                  <MessageCircle size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>GurAI</p>
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger>
                <WalletPage />
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Carteira</p>
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger>
                <button className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition-[0.2s] cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger">
                  <Plus size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Nova conversa</p>
              </TooltipContent>
            </Tooltip>
          </div>
          {page === 'monitoramento' && (
            <MonitoringPage />
          )}
        </main>
      </TooltipProvider>
    </SidebarProvider>
  );
}

function ButtonToggleSideBar() {
  const { toggleSidebar } = useSidebar();

  return (
    <button
      onClick={toggleSidebar}
      className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition cursor-pointer"
    >
      <PanelLeftIcon size={16} />
    </button>
  )
}

function SidebarCollapsedTrigger() {
  const { state } = useSidebar();

  if (state !== "collapsed") return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <img
            className="rounded-[8px] mb-[8px] cursor-pointer"
            height={35}
            width={35}
            src="/imageuser.jpg"
            alt=""
          />
        }
      />
      <DropdownMenuContent
        className="w-60 rounded-[8px] bg-[#0a0a0a]"
        align="start"
      >
        <DropdownMenuGroup>
          <DropdownMenuLabel>Usuário</DropdownMenuLabel>
          <DropdownMenuItem className="cursor-pointer">Perfil</DropdownMenuItem>
          <DropdownMenuItem className="cursor-pointer">
            Configurações
          </DropdownMenuItem>
          <DropdownMenuItem className="cursor-pointer">Ajuda</DropdownMenuItem>
          <DropdownMenuItem className="cursor-pointer">
            Adicionar veículo
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem className="cursor-pointer">Sair</DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

{/**export const getServerSideProps: GetServerSideProps = async ({ req }) => {
    const session = await getSession({ req })

    if (!session?.user) {
        return {
            redirect: {
                destination: '/auth/login',
                permanent: false
            }
        }
    }

    return {
        props: {
            user: {
                email: session?.user?.email
            }
        }
    }
} */}
