import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";
import { mockChargers } from "@/data/mockChargers";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).json({
      error: "Método não permitido.",
    });
  }

  try {
    const session = await getServerSession(req, res, authOptions);
    const email = session?.user?.email?.trim().toLowerCase();

    if (!email) {
      return res.status(401).json({
        error: "Faça login para consultar os indicadores.",
      });
    }

    const snapshot = await adminDb
      .collection("chargingSessions")
      .where("userId", "==", email)
      .get();

    const accumulatedEnergyKwh = snapshot.docs.reduce(
      (total, document) => {
        const energy = Number(document.data().energyKwh ?? 0);

        return total +
          (Number.isFinite(energy) && energy > 0 ? energy : 0);
      },
      0
    );

    const totalPowerKw = mockChargers.reduce(
      (total, charger) => total + Number(charger.power || 0),
      0
    );

    const occupiedChargers = mockChargers.filter(
      (charger) => charger.status === "occupied"
    ).length;

    const availableChargers = mockChargers.filter(
      (charger) => charger.status === "available"
    ).length;

    return res.status(200).json({
      totalPowerKw,
      occupiedChargers,
      availableChargers,
      accumulatedEnergyKwh,
    });
  } catch (error) {
    console.error("Erro ao calcular indicadores:", error);

    return res.status(500).json({
      error: "Não foi possível carregar os indicadores.",
    });
  }
}