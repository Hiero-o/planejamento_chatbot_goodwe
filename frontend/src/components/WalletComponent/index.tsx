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
import { Wallet, Check, CreditCard, Landmark, QrCode } from "lucide-react";
import { Button } from "@base-ui/react";
import CardInvoice from "../CardInvoice";
import { ReactNode, useState } from "react";
import { FaCheck } from "react-icons/fa";
import { FaPix } from "react-icons/fa6";

interface CardPayOptionsProps {
    icon: ReactNode,
    label: string,
    selected: boolean,
    onSelect: () => void
}

export default function WalletPage() {
    const [step, setStep] = useState('step1')

    return (
        <Drawer swipeDirection="right">
            <DrawerTrigger render={
                <button className="mb-[8px] rounded-[8px] flex items-center justify-center h-[35px] w-[35px] border border-[#1f1f1f] hover:bg-[#1f1f1f] transition-[0.2s] cursor-pointer" data-sidebar="trigger" data-slot="sidebar-trigger">
                    <Wallet size={16} />
                </button>
            }></DrawerTrigger>
            <DrawerContent className="bg-[#0a0a0a] rounded-l">
                {step === 'step1' && (
                    <>
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
                                onClick={() => setStep("375463986534")}
                            />
                            <CardInvoice
                                date="09/11/2026"
                                namePDFInvoice="invoice-54354338742-gurgel"
                                linkPDFInvoice="random"
                                sizeArchivePDFInvoice="4.8kb"
                                idInvoice="76563986534"
                                price={35}
                                onClick={() => setStep("76563986534")}
                            />
                        </div>
                    </>
                )}
                {step !== 'step1' && (
                    <SummaryPay />
                )}
                <DrawerFooter className="gap-0">
                    {step !== 'step1' && (
                        <>
                            <button className="mb-[8px] w-full rounded-[8px] py-[6px] px-[15px] text-[14px] bg-[#f0d941] text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f]">
                                Pagar
                            </button>
                            <button onClick={() => setStep('step1')} className="mb-[8px] w-full flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A]">
                                Voltar
                            </button>
                        </>
                    )}
                    {step === 'step1' && (
                        <button className="mb-[8px] w-full rounded-[8px] py-[6px] px-[15px] text-[14px] bg-[#f0d941] text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f]">
                            Pagar tudo
                        </button>
                    )}
                    <DrawerClose render={
                        <button className="w-full flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A]">
                            Fechar
                        </button>
                    } />
                </DrawerFooter>
            </DrawerContent>
        </Drawer>
    )
}

function SummaryPay() {
    const [paymentMethod, setPaymentMethod] = useState('credito')

    return (
        <>
            <DrawerHeader className="gap-0">
                <DrawerTitle className="mb-[0px] text-[15px]">Fatura - 08/10/2026</DrawerTitle>
            </DrawerHeader>
            <div className="p-[15px]">
                <h1 className="text-[22px] mb-[15px] font-semibold">Resumo do pagamento</h1>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[#cecece]">Serviço</h2>
                    <p className="text-[#cecece]">R$35,00</p>
                </div>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[#cecece]">PIS</h2>
                    <p className="text-[#cecece]">R$5,00 <span className="text-[12px] text-[#b3b3b3]">(3%)</span></p>
                </div>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[#cecece]">COFINS</h2>
                    <p className="text-[#cecece]">R$3,45 <span className="text-[12px] text-[#b3b3b3]">(2.5%)</span></p>
                </div>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[#cecece]">ICMS</h2>
                    <p className="text-[#cecece]">R$6,25 <span className="text-[12px] text-[#b3b3b3]">(1.9%)</span></p>
                </div>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[#cecece]">Tarifa</h2>
                    <p className="text-[#cecece]">R$21,43 <span className="text-[12px] text-[#b3b3b3]">(10%)</span></p>
                </div>
                <div className="flex items-center justify-between flex-row gap-[5px] mb-[15px]">
                    <input type="text" placeholder="Inserir código do cupom" className="w-full outline-none font-normal rounded-[8px] h-[35px] py-[6px] px-[6px] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] transition-[0.3s] focus:border-[#47474b]" />
                    <button className="flex items-center justify-center shrink-0 h-[35px] w-[35px] rounded-[8px] bg-[#070707] border border-[#27272A] font-semibold cursor-pointer transition-[0.2s] hover:border-[#47474b]"><FaCheck size={12} /></button>
                </div>
                <div className="w-full p-[0.5px] h-[0.5px] bg-[#1f1f1f] mb-[15px]"></div>
                <div className="flex items-center justify-between flex-row mb-[15px]">
                    <h2 className="text-[18px] font-semibold">Total</h2>
                    <p className="text-[18px] font-semibold">R$35,00</p>
                </div>
                <CardPayOptions
                    icon={<CreditCard size={18} />}
                    label="Pagar com cartão de crédito"
                    selected={paymentMethod === 'credito'}
                    onSelect={() => setPaymentMethod('credito')}
                />
                <CardPayOptions
                    icon={<CreditCard size={18} />}
                    label="Pagar com cartão de débito"
                    selected={paymentMethod === 'debito'}
                    onSelect={() => setPaymentMethod('debito')}
                />
                <CardPayOptions
                    icon={<FaPix size={18} />}
                    label="Pagar com PIX"
                    selected={paymentMethod === 'pix'}
                    onSelect={() => setPaymentMethod('pix')}
                />
                <CardPayOptions
                    icon={<Wallet size={18} />}
                    label="Pagar com saldo existente"
                    selected={paymentMethod === 'saldo'}
                    onSelect={() => setPaymentMethod('saldo')}
                />
            </div>
        </>
    )
}

function CardPayOptions({ icon, label, selected, onSelect }: CardPayOptionsProps) {
    return (
        <article onClick={onSelect} className={`text-[#b3b3b3] flex items-center justify-between p-[8px] mb-[5px] rounded-[8px] border flex-row cursor-pointer transition-[0.2s] ${selected ? 'border-[#47474b] bg-[#1f1f1f] text-[#fff]' : 'border-[#1f1f1f] bg-transparent'}`}>
            <div className="flex items-center justify-center flex-row">
                {icon}
                <p className="ml-[10px]">{label}</p>
            </div>
        </article>
    )
}