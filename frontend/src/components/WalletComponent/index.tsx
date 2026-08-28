import {
    Drawer,
    DrawerClose,
    DrawerContent,
    DrawerDescription,
    DrawerFooter,
    DrawerHeader,
    DrawerTitle,
    DrawerTrigger,
} from "@/components/ui/drawer"
import { Wallet } from "lucide-react";
import { Button } from "@base-ui/react";
import CardInvoice from "../CardInvoice";

export default function WalletPage() {
    return (
        <Drawer swipeDirection="right">
            <DrawerTrigger render={
                <button className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition-[0.2s] cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger">
                    <Wallet size={16} />
                </button>
            }></DrawerTrigger>
            <DrawerContent className="bg-[#0a0a0a] rounded-l">
                <DrawerHeader className="gap-0">
                    <DrawerTitle className="mb-[0px] text-[15px]">Faturas</DrawerTitle>
                    <DrawerDescription className="mt-[0px] text-[12px]">Escolha a fatura que deseja pagar</DrawerDescription>
                </DrawerHeader>
                <div className="p-[15px]">
                    <CardInvoice
                        date="08/10/2026"
                        namePDFInvoice="invoice-27463872638742-gurgel"
                        linkPDFInvoice="random"
                        sizeArchivePDFInvoice="7.0kb"
                        idInvoice="375463986534"
                        price={15}
                    />
                    <CardInvoice
                        date="09/11/2026"
                        namePDFInvoice="invoice-54354338742-gurgel"
                        linkPDFInvoice="random"
                        sizeArchivePDFInvoice="4.8kb"
                        idInvoice="76563986534"
                        price={35}
                    />
                </div>
                <DrawerFooter className="gap-0">
                    <button className="mb-[8px] w-full rounded-[8px] py-[6px] px-[15px] text-[14px] bg-[#f0d941] text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f]">
                        Pagar tudo
                    </button>
                    <button className="w-full flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A]">
                        Fechar
                    </button>
                </DrawerFooter>
            </DrawerContent>
        </Drawer>
    )
}