import type { NextApiRequest, NextApiResponse } from "next";
import { getServerSession } from "next-auth/next";
import { FieldValue } from "firebase-admin/firestore";

import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";

type ChatMessage = {
    role: "user" | "assistant";
    content: string;
};

type ChatConversation = {
    id: string;
    title: string;
    lastMessage: string;
    updatedAt: number;
};

type RecentQuestion = {
    id: string;
    conversationId: string;
    conversationTitle: string;
    question: string;
    createdAtMs: number;
};

type ChatResponse = {
    response?: string;
    messages?: ChatMessage[];
    conversations?: ChatConversation[];
    questions?: RecentQuestion[];
    error?: string;
};

const conversationIdPattern = /^[a-zA-Z0-9_-]{1,100}$/;

function normalizeForSearch(value: string): string {
    return value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^\w\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function shouldLoadUserSessions(message: string): boolean {
    const text = normalizeForSearch(message);

    const topics =
        /\b(sessao|sessoes|recarga|recargas|carregamento|carregamentos|carreguei|carregando|energia|consumo|consumi)\b/;

    const personal =
        /\b(meu|minha|meus|minhas|eu|fiz|realizei|consumi|ultimos|ultimas|historico|quantas|quantos|quais|liste|listar)\b/;

    return topics.test(text) && personal.test(text);
}

function toNumber(value: unknown): number {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
}

function getSaoPauloMonthKey(timestamp: number): string {
    const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/Sao_Paulo",
        year: "numeric",
        month: "2-digit",
    }).formatToParts(new Date(timestamp));

    const year =
        parts.find((part) => part.type === "year")?.value ?? "";
    const month =
        parts.find((part) => part.type === "month")?.value ?? "";

    return `${year}-${month}`;
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse<ChatResponse>
) {
    if (req.method !== "GET" && req.method !== "POST") {
        res.setHeader("Allow", ["GET", "POST"]);

        return res.status(405).json({
            error: "Método não permitido.",
        });
    }

    try {
        const session = await getServerSession(req, res, authOptions);
        const email = session?.user?.email?.trim().toLowerCase();

        if (!email) {
            return res.status(401).json({
                error: "Você precisa estar autenticado para conversar com o GurAI.",
            });
        }

        // GET: recuperar mensagens de uma conversa.
        if (req.method === "GET") {
            const conversationId = req.query.conversationId;

            const conversationsRef = adminDb
                .collection("users")
                .doc(email)
                .collection("conversations");

            if (req.query.view === "questions") {
                const conversationsSnapshot = await adminDb
                    .collection("users")
                    .doc(email)
                    .collection("conversations")
                    .orderBy("updatedAt", "desc")
                    .limit(30)
                    .get();

                const questionGroups = await Promise.all(
                    conversationsSnapshot.docs.map(async (conversationDoc) => {
                        const conversationData = conversationDoc.data();

                        const messagesSnapshot = await conversationDoc.ref
                            .collection("messages")
                            .orderBy("createdAt", "desc")
                            .limit(20)
                            .get();

                        return messagesSnapshot.docs
                            .map((messageDoc) => {
                                const data = messageDoc.data();

                                if (
                                    data.role !== "user" ||
                                    typeof data.content !== "string"
                                ) {
                                    return null;
                                }

                                const timestamp =
                                    typeof data.createdAtMs === "number"
                                        ? data.createdAtMs
                                        : typeof data.createdAt?.toMillis === "function"
                                            ? data.createdAt.toMillis()
                                            : 0;

                                return {
                                    id: messageDoc.id,
                                    conversationId: conversationDoc.id,
                                    conversationTitle:
                                        typeof conversationData.title === "string"
                                            ? conversationData.title
                                            : "Nova conversa",
                                    question: data.content,
                                    createdAtMs: timestamp,
                                };
                            })
                            .filter((item) => item !== null);
                    })
                );

                const questions = questionGroups
                    .flat()
                    .sort((a, b) => b.createdAtMs - a.createdAtMs)
                    .slice(0, 3);

                return res.status(200).json({ questions });
            }

            // Sem ID: retornar as conversas do usuário autenticado.
            if (conversationId === undefined) {
                const snapshot = await conversationsRef
                    .orderBy("updatedAt", "desc")
                    .limit(30)
                    .get();

                const conversations: ChatConversation[] = snapshot.docs.map((doc) => {
                    const data = doc.data();

                    return {
                        id: doc.id,
                        title:
                            typeof data.title === "string"
                                ? data.title
                                : "Nova conversa",
                        lastMessage:
                            typeof data.lastMessage === "string"
                                ? data.lastMessage
                                : "",
                        updatedAt:
                            typeof data.updatedAt?.toMillis === "function"
                                ? data.updatedAt.toMillis()
                                : 0,
                    };
                });

                return res.status(200).json({ conversations });
            }

            // Com ID: retornar as mensagens daquela conversa.
            if (
                typeof conversationId !== "string" ||
                !conversationIdPattern.test(conversationId)
            ) {
                return res.status(400).json({
                    error: "Identificador de conversa inválido.",
                });
            }

            const conversationRef = conversationsRef.doc(conversationId);
            const conversation = await conversationRef.get();

            if (!conversation.exists) {
                return res.status(200).json({ messages: [] });
            }

            const snapshot = await conversationRef
                .collection("messages")
                .orderBy("createdAtMs", "desc")
                .limit(100)
                .get();

            const messages: ChatMessage[] = snapshot.docs
                .reverse()
                .map((doc) => doc.data())
                .filter(
                    (data) =>
                        (data.role === "user" || data.role === "assistant") &&
                        typeof data.content === "string"
                )
                .map((data) => ({
                    role: data.role as ChatMessage["role"],
                    content: data.content as string,
                }));

            return res.status(200).json({ messages });
        }

        // POST: validar a mensagem enviada.
        const { message, conversationId } = req.body ?? {};

        if (
            typeof message !== "string" ||
            !message.trim() ||
            message.length > 4000
        ) {
            return res.status(400).json({
                error: "Envie uma mensagem válida de até 4000 caracteres.",
            });
        }

        if (
            typeof conversationId !== "string" ||
            !conversationIdPattern.test(conversationId)
        ) {
            return res.status(400).json({
                error: "Identificador de conversa inválido.",
            });
        }

        const backendUrl = process.env.GURAI_BACKEND_URL;
        const apiKey = process.env.GURAI_BACKEND_API_KEY;

        if (!backendUrl || !apiKey) {
            return res.status(503).json({
                error: "O serviço do GurAI não está configurado.",
            });
        }

        const conversationRef = adminDb
            .collection("users")
            .doc(email)
            .collection("conversations")
            .doc(conversationId);

        const messagesRef = conversationRef.collection("messages");

        // Recupera o histórico anterior à mensagem atual.
        const [conversationSnapshot, historySnapshot] = await Promise.all([
            conversationRef.get(),
            messagesRef.orderBy("createdAtMs", "desc").limit(20).get(),
        ]);

        const history: ChatMessage[] = historySnapshot.docs
            .reverse()
            .map((document) => document.data())
            .filter(
                (data) =>
                    (data.role === "user" || data.role === "assistant") &&
                    typeof data.content === "string"
            )
            .map((data) => ({
                role: data.role as ChatMessage["role"],
                content: data.content as string,
            }));

        // O session_id é determinado no servidor, nunca pelo navegador.
        const sessionId = `${email}:${conversationId}`;

        let userSessions: Array<{
            id: string;
            charger_name: string;
            vehicle_brand: string;
            vehicle_model: string;
            establishment_name: string;
            started_at: string;
            started_at_ms: number;
            duration_minutes: number;
            energy_kwh: number;
        }> = [];

        let userSessionSummary: {
            total_sessions: number;
            total_energy_kwh: number;
            total_duration_minutes: number;
            current_month_key: string;
            current_month_sessions: number;
            current_month_energy_kwh: number;
            current_month_duration_minutes: number;
        } | null = null;

        // Só consulta os registros pessoais quando a mensagem pede
        // informações sobre sessões, recargas ou consumo do usuário.
        if (shouldLoadUserSessions(message.trim())) {
            const sessionSnapshot = await adminDb
                .collection("chargingSessions")
                .where("userId", "==", email)
                .get();

            const allUserSessions = sessionSnapshot.docs
                .map((document) => {
                    const data = document.data();

                    const storedTimestamp = Number(data.startedAtMs ?? 0);
                    const parsedTimestamp = Date.parse(
                        String(data.startedAt ?? "")
                    );

                    const startedAtMs =
                        Number.isFinite(storedTimestamp) && storedTimestamp > 0
                            ? storedTimestamp
                            : Number.isFinite(parsedTimestamp)
                                ? parsedTimestamp
                                : 0;

                    return {
                        id: document.id,
                        charger_name:
                            typeof data.chargerName === "string"
                                ? data.chargerName
                                : "",
                        vehicle_brand:
                            typeof data.vehicleBrand === "string"
                                ? data.vehicleBrand
                                : "",
                        vehicle_model:
                            typeof data.vehicleModel === "string"
                                ? data.vehicleModel
                                : "",
                        establishment_name:
                            typeof data.establishmentName === "string"
                                ? data.establishmentName
                                : "",
                        started_at:
                            typeof data.startedAt === "string"
                                ? data.startedAt
                                : "",
                        started_at_ms: startedAtMs,
                        duration_minutes: toNumber(data.durationMinutes),
                        energy_kwh: toNumber(data.energyKwh),
                    };
                })
                .sort((a, b) => b.started_at_ms - a.started_at_ms);

            const currentMonthKey = getSaoPauloMonthKey(Date.now());

            const currentMonthSessions = allUserSessions.filter(
                (item) =>
                    item.started_at_ms > 0 &&
                    getSaoPauloMonthKey(item.started_at_ms) === currentMonthKey
            );

            const sumEnergy = (
                sessions: typeof allUserSessions
            ) =>
                sessions.reduce(
                    (total, item) => total + item.energy_kwh,
                    0
                );

            const sumDuration = (
                sessions: typeof allUserSessions
            ) =>
                sessions.reduce(
                    (total, item) => total + item.duration_minutes,
                    0
                );

            userSessions = allUserSessions.slice(0, 20);

            userSessionSummary = {
                total_sessions: allUserSessions.length,
                total_energy_kwh: Number(
                    sumEnergy(allUserSessions).toFixed(2)
                ),
                total_duration_minutes: sumDuration(allUserSessions),
                current_month_key: currentMonthKey,
                current_month_sessions: currentMonthSessions.length,
                current_month_energy_kwh: Number(
                    sumEnergy(currentMonthSessions).toFixed(2)
                ),
                current_month_duration_minutes:
                    sumDuration(currentMonthSessions),
            };
        }

        const backendResponse = await fetch(
            `${backendUrl.replace(/\/+$/, "")}/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-GurAI-API-Key": apiKey,
                },
                body: JSON.stringify({
                    message: message.trim(),
                    session_id: sessionId,
                    history,
                    user_sessions: userSessions,
                    user_sessions_summary: userSessionSummary,
                }),
            }
        );

        const data = await backendResponse.json().catch(() => null);

        if (!backendResponse.ok || typeof data?.response !== "string") {
            console.error("[GurAI] Falha no backend:", {
                status: backendResponse.status,
                detalhe: data?.detail ?? data?.error ?? "Resposta inválida.",
            });

            return res.status(502).json({
                error: "Não foi possível obter uma resposta do GurAI.",
            });
        }

        // Salva as duas mensagens somente depois de receber a resposta.
        // A gravação em lote evita deixar um turno parcialmente salvo.
        const batch = adminDb.batch();

        batch.set(messagesRef.doc(), {
            role: "user",
            content: message.trim(),
            createdAt: FieldValue.serverTimestamp(),
            createdAtMs: Date.now(),
        });

        batch.set(messagesRef.doc(), {
            role: "assistant",
            content: data.response,
            createdAt: FieldValue.serverTimestamp(),
            createdAtMs: Date.now() + 1, // Garante que a resposta do assistente seja posterior à mensagem do usuário
        });

        batch.set(
            conversationRef,
            {
                ownerEmail: email,
                title:
                    conversationSnapshot.data()?.title ||
                    message.trim().slice(0, 80),
                lastMessage: data.response,
                updatedAt: FieldValue.serverTimestamp(),
                ...(conversationSnapshot.exists
                    ? {}
                    : { createdAt: FieldValue.serverTimestamp() }),
            },
            { merge: true }
        );

        await batch.commit();

        return res.status(200).json({
            response: data.response,
        });
    } catch (error) {
        console.error("[GurAI] Erro na API de chat:", error);

        return res.status(500).json({
            error: "Não foi possível concluir a operação do chat.",
        });
    }
}