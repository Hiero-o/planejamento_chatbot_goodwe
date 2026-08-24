import { AppSidebar } from "@/components/SidebarDashboard";
import { SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { LineChart } from "lucide-react";
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

export default function Dashboard() {
  return (
    <SidebarProvider>
      <TooltipProvider>
        <main className="flex items-start justify-center flex-row w-full">
          <AppSidebar />
          <div className="flex items-center justify-start border-r border-[#1f1f1f] h-full p-[10px] flex-col">
            <SidebarCollapsedTrigger />
            <SidebarTrigger className="cursor-pointer" />
            <Tooltip>
              <TooltipTrigger>
                <Button
                  className="cursor-pointer"
                  data-sidebar="trigger"
                  data-slot="sidebar-trigger"
                  variant="ghost"
                  size="icon-sm"
                >
                  {" "}
                  <LineChart />{" "}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Monitoramento</p>
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger>
                <Button
                  className="cursor-pointer"
                  data-sidebar="trigger"
                  data-slot="sidebar-trigger"
                  variant="ghost"
                  size="icon-sm"
                >
                  {" "}
                  <Plus />{" "}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Nova conversa</p>
              </TooltipContent>
            </Tooltip>
          </div>
          <header className="p-[12px] border-b border-[#1f1f1f] w-full">
            <h1 className="text-[14px]">Monitoramento</h1>
          </header>
        </main>
      </TooltipProvider>
    </SidebarProvider>
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
            className="rounded-[8px] mb-[5px] cursor-pointer"
            height={25}
            width={25}
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
