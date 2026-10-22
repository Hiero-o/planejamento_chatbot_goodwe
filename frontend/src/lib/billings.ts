import type { Charger } from "@/data/mockChargers";

const ANEEL_RESOURCE_ID =
  "0591b8f6-fe54-437b-b72b-1aa2efd46e42";

export const ANEEL_SOURCE_URL =
  "https://dadosabertos.aneel.gov.br/dataset/bandeiras-tarifarias/resource/0591b8f6-fe54-437b-b72b-1aa2efd46e42";

const ANEEL_API_URL =
  "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search";

type AneelRecord = {
  DatCompetencia?: string;
  NomBandeiraAcionada?: string;
  VlrAdicionalBandeira?: string | number | null;
};

type AneelResponse = {
  success?: boolean;
  result?: {
    records?: AneelRecord[];
  };
};

export interface EnergyFlagSnapshot {
  name: string;
  month: string;
  additionalPerKwh: number;
  status: "official" | "unavailable";
  sourceUrl: string;
  checkedAt: number;
}

interface SessionForBilling {
  startedAt: string;
  durationMinutes: number;
  energyKwh: number;
  chargerId: string;
  chargerName: string;

  vehicleBrand?: string;
  vehicleModel?: string;

  // Dados do estabelecimento registrados na sessão.
  establishmentId?: string;
  establishmentName?: string;
  establishmentAddress?: string;

  // Snapshot das regras tarifárias.
  establishmentTarifaPercent?: number;
  basePricePerKwh?: number;
  passThroughEnergyFlag?: boolean;
}

export interface InvoiceDocument {
  invoiceNumber: string;
  userEmail: string;
  sessionId: string;

  chargerId: string;
  chargerName: string;
  vehicleBrand: string;
  vehicleModel: string;

  establishmentId: string;
  establishmentName: string;
  establishmentAddress: string;

  chargeDate: string;
  chargeDateMs: number;
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
  energyFlagCheckedAt: number;

  establishmentTariffPercent: number;
  establishmentFeeAmount: number;

  totalAmount: number;

  calculationStatus: "calculated" | "review_required";
  tariffSnapshotSource: "session_snapshot" | "demo_config_backfill";

  status: "pending" | "paid_demo";
  demoOnly: true;
  createdAt: number;
  demoPaidAt?: unknown;
}

let aneelCache:
  | { records: AneelRecord[]; expiresAt: number }
  | undefined;

function roundCurrency(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function getMonth(value: string): string {
  const match = value.match(/^(\d{4}-\d{2})/);

  if (match) {
    return match[1];
  }

  const brDate = value.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);

  if (brDate) {
    return `${brDate[3]}-${brDate[2]}`;
  }

  return "";
}

function parseAneelNumber(value: string | number | null | undefined): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : NaN;
  }

  if (typeof value !== "string" || !value.trim()) {
    return NaN;
  }

  const normalized = value.trim().includes(",")
    ? value.trim().replace(/\./g, "").replace(",", ".")
    : value.trim();

  const parsed = Number(normalized);

  return Number.isFinite(parsed) ? parsed : NaN;
}

async function loadAneelRecords(): Promise<AneelRecord[]> {
  if (aneelCache && aneelCache.expiresAt > Date.now()) {
    return aneelCache.records;
  }

  const url = new URL(ANEEL_API_URL);
  url.searchParams.set("resource_id", ANEEL_RESOURCE_ID);
  url.searchParams.set("limit", "1000");
  url.searchParams.set("sort", "DatCompetencia desc");

  try {
    const response = await fetch(url.toString(), {
      cache: "no-store",
      signal: AbortSignal.timeout(7000),
    });

    if (!response.ok) {
      throw new Error(`ANEEL respondeu com HTTP ${response.status}.`);
    }

    const payload = (await response.json()) as AneelResponse;

    if (!payload.success || !Array.isArray(payload.result?.records)) {
      throw new Error("Resposta inesperada do conjunto de dados da ANEEL.");
    }

    const records = payload.result.records;

    aneelCache = {
      records,
      expiresAt: Date.now() + 60 * 60 * 1000,
    };

    return records;
  } catch (error) {
    console.error("Não foi possível consultar a ANEEL:", error);

    // Evita repetir uma chamada externa demorada para cada fatura
    // enquanto o serviço estiver indisponível.
    aneelCache = {
        records: [],
        expiresAt: Date.now() + 60_000,
    };

    return [];
    }
}

export async function getEnergyFlagForDate(
  date: string
): Promise<EnergyFlagSnapshot> {
  const month = getMonth(date);
  const checkedAt = Date.now();
  const records = await loadAneelRecords();

  const record = records.find(
    (item) =>
      typeof item.DatCompetencia === "string" &&
      getMonth(item.DatCompetencia) === month
  );

  if (!record || !month) {
    return {
      name: "Não disponível",
      month,
      additionalPerKwh: 0,
      status: "unavailable",
      sourceUrl: ANEEL_SOURCE_URL,
      checkedAt,
    };
  }

  const name = record.NomBandeiraAcionada?.trim();

  if (!name) {
    return {
      name: "Não disponível",
      month,
      additionalPerKwh: 0,
      status: "unavailable",
      sourceUrl: ANEEL_SOURCE_URL,
      checkedAt,
    };
  }

  const rawValue =
    parseAneelNumber(record.VlrAdicionalBandeira);

  const isGreen = name.toLowerCase().includes("verde");

  // O conjunto de acionamento usualmente informa o adicional por 100 kWh.
  // A proteção também aceita um valor que já esteja expresso por kWh.
  let additionalPerKwh = 0;

  if (!isGreen) {
    if (!Number.isFinite(rawValue) || rawValue < 0) {
      return {
        name,
        month,
        additionalPerKwh: 0,
        status: "unavailable",
        sourceUrl: ANEEL_SOURCE_URL,
        checkedAt,
      };
    }

    additionalPerKwh =
      rawValue > 0.1 ? rawValue / 100 : rawValue;
  }

  return {
    name,
    month,
    additionalPerKwh: Math.round((additionalPerKwh + Number.EPSILON) * 100000) / 100000,
    status: "official",
    sourceUrl: ANEEL_SOURCE_URL,
    checkedAt,
  };
}

function parseTariffPercent(value: string): number {
  const parsed = Number(value.replace("%", "").replace(",", ".").trim());

  if (!Number.isFinite(parsed) || parsed < 0 || parsed > 100) {
    throw new Error("Percentual de tarifa do estabelecimento inválido.");
  }

  return parsed;
}

export async function buildInvoiceSnapshot(args: {
  sessionId: string;
  userEmail: string;
  session: SessionForBilling;
  charger: Charger;
}): Promise<InvoiceDocument> {
  const { sessionId, userEmail, session, charger } = args;

  const hasSessionSnapshot =
    typeof session.basePricePerKwh === "number" &&
    typeof session.establishmentTarifaPercent === "number" &&
    typeof session.passThroughEnergyFlag === "boolean";

  const basePricePerKwh = hasSessionSnapshot
    ? session.basePricePerKwh!
    : charger.establishment.basePricePerKwh;

  const tariffPercent = hasSessionSnapshot
    ? session.establishmentTarifaPercent!
    : parseTariffPercent(charger.establishment.tarifa);

  const passThroughEnergyFlag = hasSessionSnapshot
    ? session.passThroughEnergyFlag!
    : charger.establishment.passThroughEnergyFlag;

  if (!Number.isFinite(basePricePerKwh) || basePricePerKwh <= 0) {
    throw new Error("Preço-base por kWh não configurado.");
  }

  const energyKwh = Number(session.energyKwh);

  if (!Number.isFinite(energyKwh) || energyKwh <= 0) {
    throw new Error("Energia consumida inválida para faturamento.");
  }

  const flag = await getEnergyFlagForDate(session.startedAt);

  const energySubtotal = roundCurrency(
    energyKwh * basePricePerKwh
  );

  const energyFlagAmount =
    flag.status === "official" && passThroughEnergyFlag
      ? roundCurrency(energyKwh * flag.additionalPerKwh)
      : 0;

  const establishmentFeeAmount = roundCurrency(
    (energySubtotal + energyFlagAmount) * tariffPercent / 100
  );

  const totalAmount = roundCurrency(
    energySubtotal + energyFlagAmount + establishmentFeeAmount
  );

  const chargeDateMs = Date.parse(session.startedAt);

  return {
    invoiceNumber: `FAT-${sessionId.slice(0, 8).toUpperCase()}`,
    userEmail,
    sessionId,

    chargerId: charger.id,
    chargerName: charger.name,
    vehicleBrand: session.vehicleBrand ?? "",
    vehicleModel: session.vehicleModel ?? "",

    establishmentId:
      session.establishmentId ?? charger.establishment.id,
    establishmentName:
      session.establishmentName ?? charger.establishment.name,
    establishmentAddress: session.establishmentAddress ?? charger.establishment.address,
    

    chargeDate: session.startedAt,
    chargeDateMs: Number.isFinite(chargeDateMs)
      ? chargeDateMs
      : 0,
    energyKwh,
    durationMinutes: Number(session.durationMinutes),

    basePricePerKwh,
    energySubtotal,

    energyFlagName: flag.name,
    energyFlagMonth: flag.month,
    energyFlagAdditionalPerKwh: flag.additionalPerKwh,
    energyFlagAmount,
    energyFlagRepassed:
      flag.status === "official" && passThroughEnergyFlag,
    energyFlagStatus: flag.status,
    energyFlagSourceUrl: flag.sourceUrl,
    energyFlagCheckedAt: flag.checkedAt,

    establishmentTariffPercent: tariffPercent,
    establishmentFeeAmount,

    totalAmount,

    calculationStatus:
      flag.status === "official" ? "calculated" : "review_required",

    tariffSnapshotSource: hasSessionSnapshot
      ? "session_snapshot"
      : "demo_config_backfill",

    status: "pending",
    demoOnly: true,
    createdAt: Date.now(),
  };
}