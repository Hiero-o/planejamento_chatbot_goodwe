import type { NextApiRequest, NextApiResponse } from "next";
import { randomInt } from "node:crypto";
import nodemailer from "nodemailer";
import { adminDb } from "@/services/firebaseAdmin";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Método não permitido." });
  }

  const email =
    typeof req.body?.email === "string"
      ? req.body.email.trim().toLowerCase()
      : "";

  if (
    !email ||
    email.length > 254 ||
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  ) {
    return res.status(400).json({ error: "E-mail inválido." });
  }

  const emailUser = process.env.EMAIL_USER;
  const emailPass = process.env.EMAIL_PASS;

  if (!emailUser || !emailPass) {
    console.error("Credenciais de envio de e-mail ausentes.");
    return res.status(500).json({ error: "Serviço de e-mail indisponível." });
  }

  try {
    const userRef = adminDb.collection("users").doc(email);
    const userDoc = await userRef.get();

    if (!userDoc.exists) {
      return res.status(404).json({ error: "E-mail não cadastrado." });
    }

    const codeRef = adminDb.collection("authCodes").doc(email);
    const previousCode = await codeRef.get();
    const createdAt = Number(previousCode.data()?.createdAt ?? 0);

    // Limita novas solicitações para o mesmo e-mail a uma por minuto.
    if (
      previousCode.exists &&
      Number.isFinite(createdAt) &&
      Date.now() >= createdAt &&
      Date.now() - createdAt < 60_000
    ) {
      return res.status(429).json({
        error: "Aguarde um minuto antes de solicitar outro código.",
      });
    }

    // Mantemos quatro dígitos para compatibilidade com a tela atual.
    const code = String(randomInt(1000, 10_000));

    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: emailUser,
        pass: emailPass,
      },
    });

    await transporter.sendMail({
      from: emailUser,
      to: email,
      subject: "Seu código de acesso ao GurAI",
      text: `Seu código de acesso é ${code}. Ele expira em cinco minutos.`,
      html: `<p>Seu código de acesso ao GurAI é:</p>
             <h2>${code}</h2>
             <p>Ele expira em cinco minutos.</p>`,
    });

    await codeRef.set({
      code,
      createdAt: Date.now(),
    });

    return res.status(200).json({
      message: "Código enviado com sucesso.",
    });
  } catch (error) {
    console.error("Erro ao enviar código de acesso:", error);

    return res.status(500).json({
      error: "Não foi possível enviar o código.",
    });
  }
}