import { AppSidebar } from "@/components/SidebarDashboard"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default function Dashboard() {
    return (
        <main className="flex items-start justify-center flex-row">
            <AppSidebar />
            <div className="flex items-center justify-start border-r border-[#1f1f1f] h-full p-[10px] flex-col">
                <SidebarTrigger className="cursor-pointer"/>
                <Button className="cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger" variant="ghost" size="icon-sm" > <Plus /> </Button>
            </div>
        </main>
    )
}