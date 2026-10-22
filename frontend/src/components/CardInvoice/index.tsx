import { File } from "lucide-react";

interface CardInvoiceProps {
  date: string;
  namePDFInvoice: string;
  linkPDFInvoice: string;
  sizeArchivePDFInvoice: string;
  idInvoice: string;
  price: number;
  onClick?: () => void;
}

export default function CardInvoice({
  date,
  namePDFInvoice,
  linkPDFInvoice,
  sizeArchivePDFInvoice,
  idInvoice,
  price,
  onClick = () => {},
}: CardInvoiceProps) {
  return (
    <article
      onClick={onClick}
      className="mb-2 flex w-full cursor-pointer flex-col items-start justify-center rounded-lg border border-border p-[10px] transition-colors hover:bg-muted"
    >
      <h1 className="mb-[10px]">Fatura - {date}</h1>

      <div className="mb-[10px] flex w-full flex-row items-center justify-start rounded-lg border border-border bg-card p-[10px] text-card-foreground">
        <File size={40} className="mr-[10px] shrink-0" />

        <div className="flex w-full min-w-0 flex-col items-start justify-center">
          <a
            href={linkPDFInvoice}
            target="_blank"
            rel="noreferrer"
            onClick={(event) => event.stopPropagation()}
            className="break-all text-[12px] text-[#1978d1] hover:underline"
          >
            {namePDFInvoice}
          </a>

          <p className="text-[12px] text-muted-foreground">
            {sizeArchivePDFInvoice}
          </p>
        </div>
      </div>

      <footer className="flex w-full flex-row items-center justify-between">
        <p className="text-[12px] text-muted-foreground">
          ID: {idInvoice}
        </p>

        <p className="text-[12px] text-muted-foreground">
          R${price}
        </p>
      </footer>
    </article>
  );
}