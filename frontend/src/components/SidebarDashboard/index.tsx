import {
    Sidebar,
    SidebarContent,
} from "@/components/ui/sidebar"
import { MdOutlineKeyboardArrowDown } from "react-icons/md";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import ContainerChat from "../ContainerChat";
import ContainerMonitoring from "../ContainerMonitoring"

export function AppSidebar() {
    return (
        <>
            <Sidebar>
                <SidebarContent className="p-[0px] mt-[0px] flex items-start justify-start">
                    <DropdownMenu>
                        <DropdownMenuTrigger render={
                            <article className="flex items-center justify-between p-[12px] mb-[0px] border-b border-[#1f1f1f] w-full hover:bg-[#3d3d3d77] cursor-pointer transition-[0.2s]">
                                <div className="flex items-center justify-start">
                                    <img className="rounded-full mr-[5px]" height={42} width={42} src="/imageuser.jpg" alt="" />
                                    <div>
                                        <h1 className="text-[17px] mb-[3px] leading-none">Nome</h1>
                                        <p className="text-[12px] text-[#b3b3b3] mt-[0px] leading-none">email@email.com</p>
                                    </div>
                                </div>
                                <MdOutlineKeyboardArrowDown size={20} />
                            </article>
                        } />
                        <DropdownMenuContent className="w-60 rounded-[8px]" align="center">
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
                    <main className="p-[5px] w-full border-b border-[#1f1f1f]">
                        <p className="text-[#b3b3b3] text-[12px] px-[14px] mb-[5px]">Conversas</p>
                        <ContainerChat content="Carregador nao funciona"/>
                        <ContainerChat content="ID do meu carregador"/>
                        <ContainerChat content="Erro MODBUS 0x0001"/>
                        <ContainerChat content="Erro de tupla"/>
                    </main>
                </SidebarContent>
            </Sidebar>
        </>
    )
}