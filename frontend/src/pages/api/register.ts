import type { NextApiRequest, NextApiResponse } from "next";
import { adminDb } from "@/services/firebaseAdmin";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({
      error: "Método não permitido.",
    });
  }

  const username =
    typeof req.body?.username === "string"
      ? req.body.username.trim()
      : "";

  const email =
    typeof req.body?.email === "string"
      ? req.body.email.trim().toLowerCase()
      : "";

  if (username.length < 2 || username.length > 60) {
    return res.status(400).json({
      error: "O nome deve ter entre 2 e 60 caracteres.",
    });
  }

  if (
    email.length > 254 ||
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  ) {
    return res.status(400).json({
      error: "Informe um e-mail válido.",
    });
  }

  try {
    const userRef = adminDb.collection("users").doc(email);

    await adminDb.runTransaction(async (transaction) => {
      const userDoc = await transaction.get(userRef);

      if (userDoc.exists) {
        throw new Error("EMAIL_ALREADY_EXISTS");
      }

      transaction.create(userRef, {
        email,
        username,
        displayName: username,
        createdAt: Date.now(),
      });
    });

    return res.status(201).json({
      message: "Cadastro realizado com sucesso.",
    });
  } catch (error) {
    if (
      error instanceof Error &&
      error.message === "EMAIL_ALREADY_EXISTS"
    ) {
      return res.status(409).json({
        error: "Este e-mail já possui cadastro.",
      });
    }

    console.error("Erro ao cadastrar usuário:", error);

    return res.status(500).json({
      error: "Não foi possível realizar o cadastro.",
    });
  }
}