import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Wallet,
  FileText,
  ArrowLeft,
  RefreshCw,
  ExternalLink,
} from "lucide-react";

import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface Invoice {
  id: string;
  invoiceNumber: string;
  sessionId: string;

  chargerName: string;
  vehicleBrand: string;
  vehicleModel: string;

  establishmentId: string;
  establishmentName: string;

  chargeDate: string;
  energyKwh: number;
  durationMinutes: number;

  basePricePerKwh: number;
  energySubtotal: number;

  energyFlagName: string;
  energyFlagMonth: string;
  energyFlagAdditionalPerKwh: number;
  energyFlagAmount: number;
  energyFlagRepassed: boolean;
  energyFlagStatus: "official" | "unavailable";
  energyFlagSourceUrl: string;

  establishmentTariffPercent: number;
  establishmentFeeAmount: number;
  totalAmount: number;

  calculationStatus: "calculated" | "review_required";
  tariffSnapshotSource: "session_snapshot" | "demo_config_backfill";

  status: "pending" | "paid_demo";
}

interface EnergyFlag {
  name: string;
  month: string;
  additionalPerKwh: number;
  status: "official" | "unavailable";
  sourceUrl: string;
}

interface InvoiceResponse {
  invoices: Invoice[];
  pendingTotal: number;
  currentEnergyFlag: EnergyFlag;
}

function currency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

function formatDate(value: string): string {
  const date = new Date(value);

  if (!Number.isFinite(date.getTime())) {
    return "Data não disponível";
  }

  return date.toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function formatMonth(value: string): string {
  if (!value) return "Mês não disponível";

  const [year, month] = value.split("-").map(Number);

  if (!year || !month) return value;

  return new Date(year, month - 1, 1).toLocaleDateString("pt-BR", {
    month: "long",
    year: "numeric",
  });
}

function durationLabel(minutes: number): string {
  const total = Math.max(0, Math.floor(minutes || 0));
  const hours = Math.floor(total / 60);
  const remaining = total % 60;

  return `${hours}h ${String(remaining).padStart(2, "0")}min`;
}

export default function WalletPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [currentEnergyFlag, setCurrentEnergyFlag] =
    useState<EnergyFlag | null>(null);

  const [selectedInvoiceId, setSelectedInvoiceId] =
    useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [processingPayment, setProcessingPayment] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/invoices");
      const data = (await response.json()) as InvoiceResponse & {
        error?: string;
      };

      if (!response.ok) {
        throw new Error(data.error || "Não foi possível carregar as faturas.");
      }

      setInvoices(Array.isArray(data.invoices) ? data.invoices : []);
      setCurrentEnergyFlag(data.currentEnergyFlag ?? null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro ao carregar as faturas."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadInvoices();
  }, [loadInvoices]);

  const selectedInvoice = invoices.find(
    (invoice) => invoice.id === selectedInvoiceId
  );

  const pendingInvoices = invoices.filter(
    (invoice) => invoice.status === "pending"
  );

  const pendingTotal = useMemo(
    () =>
      Math.round(
        pendingInvoices.reduce(
          (total, invoice) => total + Number(invoice.totalAmount || 0),
          0
        ) * 100
      ) / 100,
    [pendingInvoices]
  );

  const establishmentTotals = useMemo(() => {
    const grouped = new Map<
      string,
      { id: string; name: string; total: number; count: number }
    >();

    for (const invoice of pendingInvoices) {
      const current = grouped.get(invoice.establishmentId) ?? {
        id: invoice.establishmentId,
        name: invoice.establishmentName,
        total: 0,
        count: 0,
      };

      current.total += Number(invoice.totalAmount || 0);
      current.count += 1;

      grouped.set(invoice.establishmentId, current);
    }

    return [...grouped.values()]
      .map((item) => ({
        ...item,
        total: Math.round(item.total * 100) / 100,
      }))
      .sort((a, b) => b.total - a.total);
  }, [pendingInvoices]);

  async function simulatePayment(invoiceIds: string[]) {
    const ids = [...new Set(invoiceIds)];

    if (ids.length === 0) return;

    setProcessingPayment(true);
    setError("");
    setMessage("");

    try {
      // Divide solicitações grandes para respeitar os limites da API.
      let totalSimulated = 0;

      for (let i = 0; i < ids.length; i += 400) {
        const response = await fetch("/api/invoices", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            invoiceIds: ids.slice(i, i + 400),
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Não foi possível simular o pagamento.");
        }

        totalSimulated += Number(data.simulatedCount || 0);
      }

      setMessage(
        `${totalSimulated} fatura(s) marcada(s) como paga(s) em modo demonstrativo. Nenhum pagamento real foi realizado.`
      );

      await loadInvoices();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro ao simular pagamento."
      );
    } finally {
      setProcessingPayment(false);
    }
  }

  return (
    <Drawer swipeDirection="right">
      <Tooltip>
        <TooltipTrigger
          render={
            <DrawerTrigger
              render={
                <button
                  type="button"
                  className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
                  data-sidebar="trigger"
                  data-slot="sidebar-trigger"
                  aria-label="Abrir carteira"
                >
                  <Wallet size={16} />
                </button>
              }
            />
          }
        />

        <TooltipContent side="right">
          Carteira
        </TooltipContent>
      </Tooltip>

      <DrawerContent className="w-full border-l border-border bg-background text-foreground sm:max-w-[32rem]">
        {selectedInvoice ? (
          <>
            <DrawerHeader>
              <button
                type="button"
                onClick={() => {
                  setSelectedInvoiceId(null);
                  setMessage("");
                  setError("");
                }}
                className="mb-2 flex w-fit items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft size={16} />
                Voltar às faturas
              </button>

              <DrawerTitle>
                {selectedInvoice.invoiceNumber}
              </DrawerTitle>

              <DrawerDescription>
                Detalhamento do carregamento e composição do valor.
              </DrawerDescription>
            </DrawerHeader>

            <div className="flex-1 space-y-4 overflow-y-auto p-4">
              <section className="rounded-xl border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground">
                  Estabelecimento
                </p>

                <h3 className="mt-1 font-semibold">
                  {selectedInvoice.establishmentName}
                </h3>

                <p className="mt-3 text-sm text-muted-foreground">
                  Carregador
                </p>

                <p>{selectedInvoice.chargerName}</p>

                <p className="mt-3 text-sm text-muted-foreground">
                  Data do carregamento
                </p>

                <p>{formatDate(selectedInvoice.chargeDate)}</p>

                <p className="mt-3 text-sm text-muted-foreground">
                  Veículo
                </p>

                <p>
                  {[selectedInvoice.vehicleBrand, selectedInvoice.vehicleModel]
                    .filter(Boolean)
                    .join(" ") || "Não informado"}
                </p>

                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-4">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Energia utilizada
                    </p>
                    <p className="font-semibold">
                      {selectedInvoice.energyKwh.toLocaleString("pt-BR")} kWh
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-muted-foreground">
                      Duração
                    </p>
                    <p className="font-semibold">
                      {durationLabel(selectedInvoice.durationMinutes)}
                    </p>
                  </div>
                </div>
              </section>

              <section className="rounded-xl border border-border bg-card p-4">
                <h3 className="mb-4 font-semibold">
                  Composição do valor
                </h3>

                <div className="space-y-3 text-sm">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p>Energia consumida</p>
                      <p className="text-xs text-muted-foreground">
                        {selectedInvoice.energyKwh.toLocaleString("pt-BR")} kWh ×{" "}
                        {currency(selectedInvoice.basePricePerKwh)}/kWh
                      </p>
                    </div>

                    <p className="shrink-0">
                      {currency(selectedInvoice.energySubtotal)}
                    </p>
                  </div>

                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p>
                        Bandeira ANEEL — {selectedInvoice.energyFlagName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Referência: {formatMonth(selectedInvoice.energyFlagMonth)}
                      </p>

                      {selectedInvoice.energyFlagStatus === "official" ? (
                        <a
                          href={selectedInvoice.energyFlagSourceUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1 inline-flex items-center gap-1 text-blue-600 hover:underline"
                        >
                          Fonte oficial <ExternalLink size={12} />
                        </a>
                      ) : (
                        <p className="mt-1 text-xs text-amber-600">
                          Fonte indisponível; valor pendente de validação.
                        </p>
                      )}
                    </div>

                    <p className="shrink-0">
                      {selectedInvoice.energyFlagStatus === "official"
                        ? currency(selectedInvoice.energyFlagAmount)
                        : "A validar"}
                    </p>
                  </div>

                  {selectedInvoice.energyFlagStatus === "official" &&
                    !selectedInvoice.energyFlagRepassed && (
                      <p className="text-xs text-muted-foreground">
                        O adicional da bandeira foi informado, mas não foi
                        repassado ao cliente nessa configuração.
                      </p>
                    )}

                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p>
                        Tarifa do estabelecimento (
                        {selectedInvoice.establishmentTariffPercent}%)
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Percentual aplicado à energia e ao adicional repassado.
                      </p>
                    </div>

                    <p className="shrink-0">
                      {currency(selectedInvoice.establishmentFeeAmount)}
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
                  <p className="font-semibold">Total demonstrativo</p>
                  <p className="text-xl font-bold">
                    {currency(selectedInvoice.totalAmount)}
                  </p>
                </div>
              </section>

              {selectedInvoice.calculationStatus === "review_required" && (
                <p className="rounded-lg border border-amber-500/40 p-3 text-sm text-amber-700">
                  A consulta à bandeira para o mês do carregamento não foi
                  confirmada. Esta fatura está marcada para revisão tarifária.
                </p>
              )}

              {selectedInvoice.tariffSnapshotSource ===
                "demo_config_backfill" && (
                <p className="rounded-lg border border-amber-500/40 p-3 text-sm text-amber-700">
                  Fatura histórica reconstruída com a configuração demonstrativa
                  atual. A sessão original não registrava o preço-base e o
                  percentual da época.
                </p>
              )}

              <p className="text-xs text-muted-foreground">
                Documento demonstrativo, não fiscal. Nenhum pagamento real
                está sendo processado.
              </p>
            </div>

            <DrawerFooter>
              {selectedInvoice.status === "pending" ? (
                <button
                  type="button"
                  onClick={() => void simulatePayment([selectedInvoice.id])}
                  disabled={processingPayment}
                  className="w-full rounded-lg bg-[#f0d941] px-4 py-3 font-semibold text-[#070707] transition-colors hover:bg-[#a3921f] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {processingPayment
                    ? "Processando simulação..."
                    : "Simular pagamento"}
                </button>
              ) : (
                <p className="rounded-lg border border-green-600/30 p-3 text-center text-sm text-green-700">
                  Pagamento marcado como simulado.
                </p>
              )}

              <DrawerClose
                render={
                  <button
                    type="button"
                    className="w-full rounded-lg border border-border px-4 py-2 text-sm hover:bg-muted"
                  >
                    Fechar
                  </button>
                }
              />
            </DrawerFooter>
          </>
        ) : (
          <>
            <DrawerHeader>
              <DrawerTitle>Faturas</DrawerTitle>
              <DrawerDescription>
                Histórico de carregamentos e demonstrativos de cobrança.
              </DrawerDescription>
            </DrawerHeader>

            <div className="flex-1 space-y-4 overflow-y-auto p-4">
              <section className="rounded-xl border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground">
                  Total pendente do cliente
                </p>

                <p className="mt-1 text-3xl font-bold">
                  {currency(pendingTotal)}
                </p>

                <p className="mt-1 text-xs text-muted-foreground">
                  {pendingInvoices.length} fatura(s) demonstrativa(s) pendente(s)
                </p>
              </section>

              <section className="rounded-xl border border-border bg-card p-4">
                <div className="flex items-center gap-2">
                  <FileText size={17} />
                  <h3 className="font-semibold">
                    Subtotais por estabelecimento
                  </h3>
                </div>

                {establishmentTotals.length > 0 ? (
                  <div className="mt-3 space-y-3">
                    {establishmentTotals.map((establishment) => (
                      <div
                        key={establishment.id}
                        className="flex items-start justify-between gap-4 text-sm"
                      >
                        <div>
                          <p className="font-medium">
                            {establishment.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {establishment.count} fatura(s) pendente(s)
                          </p>
                        </div>

                        <p className="shrink-0 font-medium">
                          {currency(establishment.total)}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-muted-foreground">
                    Nenhum subtotal pendente.
                  </p>
                )}
              </section>

              {currentEnergyFlag && (
                <section className="rounded-xl border border-border p-4">
                  <p className="text-sm font-semibold">
                    Bandeira energética vigente
                  </p>

                  <p className="mt-1">
                    {currentEnergyFlag.status === "official"
                      ? currentEnergyFlag.name
                      : "Consulta oficial indisponível"}
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    {currentEnergyFlag.month
                      ? `Referência: ${formatMonth(currentEnergyFlag.month)}.`
                      : "Não foi possível verificar a referência."}{" "}
                    A bandeira de cada fatura corresponde ao mês do carregamento,
                    não necessariamente ao mês atual.
                  </p>
                </section>
              )}

              {loading && (
                <p className="text-sm text-muted-foreground">
                  Carregando faturas...
                </p>
              )}

              {error && (
                <p className="rounded-lg border border-red-500/30 p-3 text-sm text-red-600">
                  {error}
                </p>
              )}

              {message && (
                <p className="rounded-lg border border-green-600/30 p-3 text-sm text-green-700">
                  {message}
                </p>
              )}

              <button
                type="button"
                onClick={() => void loadInvoices()}
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-border px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
              >
                <RefreshCw size={15} />
                Atualizar faturas
              </button>

              {!loading && !error && invoices.length === 0 && (
                <div className="rounded-xl border border-dashed border-border p-6 text-center">
                  <FileText className="mx-auto mb-3 text-muted-foreground" />

                  <p className="font-medium">
                    Nenhuma fatura ainda
                  </p>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Registre um carregamento para gerar o primeiro demonstrativo.
                  </p>
                </div>
              )}

              <section className="space-y-3">
                <h3 className="font-semibold">
                  Histórico de faturas por carregamento
                </h3>

                {invoices.map((invoice) => (
                  <button
                    key={invoice.id}
                    type="button"
                    onClick={() => {
                      setSelectedInvoiceId(invoice.id);
                      setMessage("");
                      setError("");
                    }}
                    className="w-full rounded-xl border border-border bg-card p-4 text-left transition-colors hover:bg-muted"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-semibold">
                          {invoice.invoiceNumber}
                        </p>

                        <p className="mt-1 text-sm text-muted-foreground">
                          {invoice.establishmentName}
                        </p>

                        <p className="mt-1 text-xs text-muted-foreground">
                          {formatDate(invoice.chargeDate)}
                        </p>
                      </div>

                      <p className="shrink-0 font-semibold">
                        {currency(invoice.totalAmount)}
                      </p>
                    </div>

                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                      <span className="rounded-md border border-border px-2 py-1">
                        {invoice.energyKwh.toLocaleString("pt-BR")} kWh
                      </span>

                      <span className="rounded-md border border-border px-2 py-1">
                        {invoice.status === "pending"
                          ? "Pendente"
                          : "Pagamento simulado"}
                      </span>

                      {invoice.calculationStatus === "review_required" && (
                        <span className="rounded-md border border-amber-500/40 px-2 py-1 text-amber-700">
                          Revisão tarifária
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </section>
            </div>

            <DrawerFooter>
              <button
                type="button"
                disabled={
                  processingPayment ||
                  pendingInvoices.length === 0
                }
                onClick={() =>
                  void simulatePayment(
                    pendingInvoices.map((invoice) => invoice.id)
                  )
                }
                className="w-full rounded-lg bg-[#f0d941] px-4 py-3 font-semibold text-[#070707] transition-colors hover:bg-[#a3921f] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {processingPayment
                  ? "Processando simulação..."
                  : "Simular pagamento de todas"}
              </button>

              <p className="text-center text-xs text-muted-foreground">
                Simulação apenas. Nenhum valor será cobrado.
              </p>

              <DrawerClose
                render={
                  <button
                    type="button"
                    className="w-full rounded-lg border border-border px-4 py-2 text-sm hover:bg-muted"
                  >
                    Fechar
                  </button>
                }
              />
            </DrawerFooter>
          </>
        )}
      </DrawerContent>
    </Drawer>
  );
}