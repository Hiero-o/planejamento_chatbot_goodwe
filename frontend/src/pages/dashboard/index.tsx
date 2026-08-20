import { AppSidebar } from "@/components/SidebarDashboard"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { LineChart } from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { TooltipProvider } from "@/components/ui/tooltip"

export default function Dashboard() {
    return (
        <TooltipProvider>
            <main className="flex items-start justify-center flex-row">
                <AppSidebar />
                <div className="flex items-center justify-start border-r border-[#1f1f1f] h-full p-[10px] flex-col">
                    <SidebarTrigger className="cursor-pointer"/>
                    <Tooltip>
                        <TooltipTrigger>
                            <Button className="cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger" variant="ghost" size="icon-sm" > <LineChart /> </Button>
                        </TooltipTrigger>
                        <TooltipContent side="right">
                            <p>Monitoramento</p>
                        </TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger>
                            <Button className="cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger" variant="ghost" size="icon-sm" > <Plus /> </Button>
                        </TooltipTrigger>
                        <TooltipContent side="right">
                            <p>Nova conversa</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
                da
            </main>
        </TooltipProvider>
    )
}