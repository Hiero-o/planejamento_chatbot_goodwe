import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";

import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";
import { mockChargers } from "@/data/mockChargers";
import { buildInvoiceSnapshot } from "@/lib/billings";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "GET" && req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({
      error: "Método não permitido.",
    });
  }

  try {
    const session = await getServerSession(req, res, authOptions);
    const email = session?.user?.email?.trim().toLowerCase();

    if (!email) {
      return res.status(401).json({
        error: "Faça login para acessar as sessões.",
      });
    }

    const sessionsRef = adminDb.collection("chargingSessions");

    if (req.method === "GET") {
      const snapshot = await sessionsRef
        .where("userId", "==", email)
        .get();

      const sessions = snapshot.docs
        .map((document) => {
          const data = document.data();

          return {
            ...data,
            id: document.id,
            startedAtMs: Number(data.startedAtMs ?? 0),
          };
        })
        .sort((a, b) => b.startedAtMs - a.startedAtMs);

      return res.status(200).json({ sessions });
    }

    const vehicleId =
      typeof req.body?.vehicleId === "string"
        ? req.body.vehicleId.trim()
        : "";

    const chargerId =
      typeof req.body?.chargerId === "string"
        ? req.body.chargerId.trim()
        : "";

    const startedAt =
      typeof req.body?.startedAt === "string"
        ? req.body.startedAt
        : "";

    const durationMinutes = Number(req.body?.durationMinutes);
    const energyKwh = Number(req.body?.energyKwh);
    const startedAtMs = Date.parse(startedAt);

    if (
      !vehicleId ||
      !chargerId ||
      !startedAt ||
      !Number.isFinite(startedAtMs)
    ) {
      return res.status(400).json({
        error: "Informe o veículo, o carregador e a data inicial.",
      });
    }

    if (
      !Number.isInteger(durationMinutes) ||
      durationMinutes <= 0 ||
      durationMinutes > 10080
    ) {
      return res.status(400).json({
        error: "A duração deve ser de 1 a 10080 minutos.",
      });
    }

    if (
      !Number.isFinite(energyKwh) ||
      energyKwh <= 0 ||
      energyKwh > 10000
    ) {
      return res.status(400).json({
        error: "Informe uma quantidade válida de energia em kWh.",
      });
    }

    const charger = mockChargers.find(
      (item) => item.id === chargerId
    );

    if (!charger) {
      return res.status(400).json({
        error: "Carregador não encontrado.",
      });
    }

    if (charger.status !== "available") {
      return res.status(409).json({
        error: `O carregador ${charger.name} está indisponível no momento: ${
          charger.status === "occupied"
            ? "está em uso"
            : "está offline"
        }. Escolha um carregador livre ou volte em outro momento!`,
      });
    }

    const vehicleRef = adminDb
      .collection("users")
      .doc(email)
      .collection("vehicles")
      .doc(vehicleId);

    const vehicleDoc = await vehicleRef.get();

    if (!vehicleDoc.exists) {
      return res.status(404).json({
        error: "Veículo não encontrado na sua conta.",
      });
    }

    const vehicle = vehicleDoc.data()!;
    const endedAtMs =
      startedAtMs + durationMinutes * 60 * 1000;

    const tariffPercent = Number(
      charger.establishment.tarifa.replace("%", "").replace(",", ".")
    );

    // Snapshot de regras: mudanças futuras no preço não alteram
    // esta sessão ou sua fatura.
    const sessionData = {
      userId: email,
      vehicleId,
      vehicleBrand: vehicle.brand ?? "",
      vehicleModel: vehicle.model ?? "",
      vehicleYear: vehicle.year ?? null,

      chargerId: charger.id,
      chargerName: charger.name,

      establishmentId: charger.establishment.id,
      establishmentName: charger.establishment.name,
      establishmentAddress: charger.establishment.address,

      establishmentTarifaPercent: tariffPercent,
      basePricePerKwh: charger.establishment.basePricePerKwh,
      passThroughEnergyFlag:
        charger.establishment.passThroughEnergyFlag,

      startedAt: new Date(startedAtMs).toISOString(),
      startedAtMs,
      endedAt: new Date(endedAtMs).toISOString(),
      endedAtMs,

      durationMinutes,
      energyKwh,

      source: "manual",
      createdAt: Date.now(),
    };

    // Gera os identificadores antes do lote. A fatura usa o ID
    // da sessão como chave para impedir duas faturas para a mesma sessão.
    const sessionRef = sessionsRef.doc();
    const invoiceRef = adminDb
      .collection("invoices")
      .doc(sessionRef.id);

    const invoiceData = await buildInvoiceSnapshot({
      sessionId: sessionRef.id,
      userEmail: email,
      session: {
        ...sessionData,
        chargerId: charger.id,
        chargerName: charger.name,
      },
      charger,
    });

    const batch = adminDb.batch();

    batch.set(sessionRef, sessionData);
    batch.set(invoiceRef, invoiceData);

    await batch.commit();

    return res.status(201).json({
      session: {
        id: sessionRef.id,
        ...sessionData,
      },
      invoice: {
        id: invoiceRef.id,
        ...invoiceData,
      },
    });
  } catch (error) {
    console.error(
      "Erro ao registrar o carregamento e gerar a fatura:",
      error
    );

    return res.status(500).json({
      error: "Não foi possível registrar o carregamento e gerar a fatura.",
    });
  }
}
