import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { FieldValue } from "firebase-admin/firestore";
import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";

const allowedCategories = [
  "Dúvida geral",
  "Problema na conta",
  "Alterar senha ou acesso",
  "Excluir conta",
  "Outro",
];

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido." });
  }

  try {
    const session = await getServerSession(req, res, authOptions);
    const email = session?.user?.email;

    if (!email) {
      return res.status(401).json({
        error: "Faça login para enviar uma solicitação.",
      });
    }

    const category =
      typeof req.body?.category === "string" ? req.body.category : "";
    const message =
      typeof req.body?.message === "string" ? req.body.message.trim() : "";

    if (!allowedCategories.includes(category)) {
      return res.status(400).json({ error: "Assunto inválido." });
    }

    if (message.length < 10 || message.length > 3000) {
      return res.status(400).json({
        error: "A mensagem deve ter entre 10 e 3.000 caracteres.",
      });
    }

    const ticket = await adminDb.collection("supportTickets").add({
      userEmail: email,
      category,
      message,
      status: "open",
      createdAt: FieldValue.serverTimestamp(),
    });

    return res.status(201).json({
      ok: true,
      ticketId: ticket.id,
    });
  } catch (error) {
    console.error("Erro ao registrar solicitação de suporte:", error);
    return res.status(500).json({
      error: "Erro interno ao registrar a solicitação.",
    });
  }
}