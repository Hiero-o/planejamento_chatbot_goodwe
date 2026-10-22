
import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "DELETE") {
    res.setHeader("Allow", "DELETE");
    return res.status(405).json({
      error: "Método não permitido.",
    });
  }

  try {
    const session = await getServerSession(req, res, authOptions);
    const email = session?.user?.email?.trim().toLowerCase();

    if (!email) {
      return res.status(401).json({
        error: "Faça login para excluir veículos.",
      });
    }

    const id = req.query.id;

    if (typeof id !== "string" || !id.trim()) {
      return res.status(400).json({
        error: "Identificador do veículo inválido.",
      });
    }

    // A consulta é limitada à subcoleção do usuário da sessão.
    const vehicleRef = adminDb
      .collection("users")
      .doc(email)
      .collection("vehicles")
      .doc(id);

    const vehicleDoc = await vehicleRef.get();

    if (!vehicleDoc.exists) {
      return res.status(404).json({
        error: "Veículo não encontrado.",
      });
    }

    await vehicleRef.delete();

    return res.status(200).json({
      message: "Veículo excluído com sucesso.",
    });
  } catch (error) {
    console.error("Erro ao excluir veículo:", error);

    return res.status(500).json({
      error: "Não foi possível excluir o veículo.",
    });
  }
}
