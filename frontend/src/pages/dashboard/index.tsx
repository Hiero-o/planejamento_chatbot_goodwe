import { AppSidebar } from "@/components/SidebarDashboard"
import { SidebarTrigger } from "@/components/ui/sidebar"

export default function Dashboard() {
    return(
        <main className="flex items-start justify-center flex-row">
            <AppSidebar />
            <div className="flex items-start justify-center border-r border-[#1f1f1f] h-full p-[10px]">
                <SidebarTrigger />
            </div>
        </main>
    )
}