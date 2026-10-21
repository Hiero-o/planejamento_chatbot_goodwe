import { File } from "lucide-react";

interface CardInvoiceProps {
    date: string,
    namePDFInvoice: string,
    linkPDFInvoice: string,
    sizeArchivePDFInvoice: string,
    idInvoice: string,
    price: number,
    onClick?: () => void
}

export default function CardInvoice({ date, namePDFInvoice, linkPDFInvoice, sizeArchivePDFInvoice, idInvoice, price, onClick = () => {} }: CardInvoiceProps) {
    return(
        <article onClick={onClick} className="rounded-[8px] p-[10px] border border-[#1f1f1f] flex items-start justify-center flex-col w-full mb-[8px] cursor-pointer hover:bg-[#1f1f1f77] transition-[0.2s]">
            <h1 className="mb-[10px]">Fatura - {date}</h1>
            <div className="rounded-[8px] border border-[#1f1f1f] bg-[#1f1f1f] flex items-center justify-start flex-row w-full p-[10px] mb-[10px]">
                <File size={40} className="mr-[10px]"/>
                <div className="flex items-start justify-center flex-col w-full">
                    <a href={linkPDFInvoice} target="_blank" className="text-[#1978d1] text-[12px]">{namePDFInvoice}</a>
                    <p className="text-[12px] text-[#b3b3b3]">{sizeArchivePDFInvoice}</p>
                </div>
            </div>
            <footer className="flex flex-col items-center justify-between w-full flex-row">
                <p className="text-[12px] text-[#b3b3b3]">ID: {idInvoice}</p>
                <p className="text-[12px] text-[#b3b3b3]">R${price}</p>
            </footer>
        </article>
    )
}