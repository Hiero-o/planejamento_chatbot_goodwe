import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
} from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent className="p-[0px] mt-[0px] flex items-start justify-start">
        <article className="flex items-center justify-start p-[10px] mb-[0px] border-b border-[#1f1f1f] w-full">
            <img className="rounded-full mr-[5px]" height={45} width={45} src="/imageuser.jpg" alt="" />
            <div>
                <h1 className="text-[17px] mb-[3px] leading-none">Nome</h1>
                <p className="text-[12px] text-[#b3b3b3] mt-[0px] leading-none">email@email.com</p>
            </div>
        </article>
      </SidebarContent>
      <SidebarFooter />
    </Sidebar>
  )
}