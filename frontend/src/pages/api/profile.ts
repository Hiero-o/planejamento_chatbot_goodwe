
import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "GET" && req.method !== "PUT") {
    res.setHeader("Allow", "GET, PUT");

    return res.status(405).json({
      error: "Método não permitido.",
    });
  }

  try {
    const session = await getServerSession(
      req,
      res,
      authOptions
    );

    const email = session?.user?.email
      ?.trim()
      .toLowerCase();

    if (!email) {
      return res.status(401).json({
        error: "Faça login para acessar seu perfil.",
      });
    }

    const userRef = adminDb.collection("users").doc(email);

    if (req.method === "GET") {
      let userDoc = await userRef.get();

      // Cria um perfil inicial para usuários autenticados
      // que ainda não possuem documento na coleção users.
      if (!userDoc.exists) {
        const sessionName = session?.user?.name ?? "";

        await userRef.set({
          email,
          username: sessionName,
          displayName: sessionName,
          createdAt: Date.now(),
        });

        userDoc = await userRef.get();
      }

      const userData = userDoc.data();

      return res.status(200).json({
        email,
        username:
          userData?.username ??
          userData?.displayName ??
          "",
        phone: userData?.phone ?? "",
      });
    }

    // Atualização do perfil
    const username =
      typeof req.body?.username === "string"
        ? req.body.username.trim()
        : "";

    const phone =
      typeof req.body?.phone === "string"
        ? req.body.phone.trim()
        : "";

    if (username.length < 2 || username.length > 60) {
      return res.status(400).json({
        error: "O nome deve ter entre 2 e 60 caracteres.",
      });
    }

    if (phone.length > 30) {
      return res.status(400).json({
        error: "O telefone deve ter no máximo 30 caracteres.",
      });
    }

    await userRef.set(
      {
        email,
        username,
        displayName: username,
        phone,
        updatedAt: Date.now(),
      },
      { merge: true }
    );

    return res.status(200).json({
      message: "Perfil atualizado com sucesso.",
    });
  } catch (error) {
    console.error("Erro na API de perfil:", error);

    return res.status(500).json({
      error: "Não foi possível processar o perfil.",
    });
  }
}
