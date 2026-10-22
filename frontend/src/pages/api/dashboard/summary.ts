
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

    const totals = snapshot.docs.reduce(
      (result, document) => {
        const data = document.data();

        const energy = Number(data.energyKwh ?? 0);
        const duration = Number(data.durationMinutes ?? 0);

        if (Number.isFinite(energy) && energy > 0) {
          result.accumulatedEnergyKwh += energy;
        }

        // Para calcular a potência média, precisamos de
        // energia e duração válidas na mesma sessão.
        if (
          Number.isFinite(energy) &&
          energy > 0 &&
          Number.isFinite(duration) &&
          duration > 0
        ) {
          result.energyForAverageKwh += energy;
          result.durationForAverageMinutes += duration;
        }

        return result;
      },
      {
        accumulatedEnergyKwh: 0,
        energyForAverageKwh: 0,
        durationForAverageMinutes: 0,
      }
    );

    const averagePowerKw =
      totals.durationForAverageMinutes > 0
        ? totals.energyForAverageKwh /
          (totals.durationForAverageMinutes / 60)
        : 0;

    // Estes dois indicadores ainda usam carregadores simulados.
    const totalInstalledPowerKw = mockChargers.reduce(
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
      averagePowerKw: Number(averagePowerKw.toFixed(2)),
      accumulatedEnergyKwh: Number(
        totals.accumulatedEnergyKwh.toFixed(2)
      ),
      totalDurationMinutes: totals.durationForAverageMinutes,
      totalInstalledPowerKw,
      occupiedChargers,
      availableChargers,
    });
  } catch (error) {
    console.error("Erro ao calcular indicadores:", error);

    return res.status(500).json({
      error: "Não foi possível carregar os indicadores.",
    });
  }
}
