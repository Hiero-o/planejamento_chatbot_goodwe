import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";

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
        error: "Faça login para acessar seus veículos.",
      });
    }

    const userRef = adminDb.collection("users").doc(email);
    const userDoc = await userRef.get();

    // Inicializa o documento caso seja um usuário autenticado
    // pelo Google que ainda não tenha perfil no Firestore.
    if (!userDoc.exists) {
      const name = session?.user?.name ?? "";

      await userRef.set({
        email,
        username: name,
        displayName: name,
        createdAt: Date.now(),
      });
    }

    const vehiclesRef = userRef.collection("vehicles");

    if (req.method === "GET") {
      const snapshot = await vehiclesRef
        .orderBy("createdAt", "desc")
        .get();

      const vehicles = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));

      return res.status(200).json({ vehicles });
    }

    const brand =
      typeof req.body?.brand === "string"
        ? req.body.brand.trim()
        : "";

    const model =
      typeof req.body?.model === "string"
        ? req.body.model.trim()
        : "";

    const year = Number(req.body?.year);

    const plate =
      typeof req.body?.plate === "string"
        ? req.body.plate.trim().toUpperCase()
        : "";

    const currentYear = new Date().getFullYear();

    if (brand.length < 2 || brand.length > 50) {
      return res.status(400).json({
        error: "A marca deve ter entre 2 e 50 caracteres.",
      });
    }

    if (model.length < 1 || model.length > 60) {
      return res.status(400).json({
        error: "O modelo deve ter entre 1 e 60 caracteres.",
      });
    }

    if (
      !Number.isInteger(year) ||
      year < 1886 ||
      year > currentYear + 2
    ) {
      return res.status(400).json({
        error: "Informe um ano válido para o veículo.",
      });
    }

    if (plate.length > 10) {
      return res.status(400).json({
        error: "A placa deve ter no máximo 10 caracteres.",
      });
    }

    const vehicleData = {
      brand,
      model,
      year,
      plate: plate || null,
      createdAt: Date.now(),
    };

    const vehicleRef = await vehiclesRef.add(vehicleData);

    return res.status(201).json({
      vehicle: {
        id: vehicleRef.id,
        ...vehicleData,
      },
    });
  } catch (error) {
    console.error("Erro na API de veículos:", error);

    return res.status(500).json({
      error: "Não foi possível processar os veículos.",
    });
  }
}
