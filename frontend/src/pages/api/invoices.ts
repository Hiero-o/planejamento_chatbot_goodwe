import type { NextApiRequest, NextApiResponse } from "next";
import { FieldValue } from "firebase-admin/firestore";
import { getServerSession } from "next-auth/next";

import { authOptions } from "@/services/authOptions";
import { adminDb } from "@/services/firebaseAdmin";
import { mockChargers } from "@/data/mockChargers";
import {
    buildInvoiceSnapshot,
    getEnergyFlagForDate,
    type InvoiceDocument,
} from "@/lib/billings";

const BATCH_LIMIT = 400;

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
                error: "Faça login para acessar as faturas.",
            });
        }

        const invoicesRef = adminDb.collection("invoices");

        if (req.method === "GET") {
            const sessionsSnapshot = await adminDb
                .collection("chargingSessions")
                .where("userId", "==", email)
                .get();

            const existingInvoicesSnapshot = await invoicesRef
                .where("userEmail", "==", email)
                .get();

            const existingSessionIds = new Set(
                existingInvoicesSnapshot.docs.map(
                    (document) => document.id
                )
            );

            const missingInvoices: Array<{
                id: string;
                data: Awaited<ReturnType<typeof buildInvoiceSnapshot>>;
            }> = [];

            for (const sessionDoc of sessionsSnapshot.docs) {
                if (existingSessionIds.has(sessionDoc.id)) {
                    continue;
                }

                const sessionData = sessionDoc.data();

                const charger = mockChargers.find(
                    (item) => item.id === sessionData.chargerId
                );

                if (!charger) {
                    console.warn(
                        `Não foi possível reconstruir a fatura da sessão ${sessionDoc.id}: carregador não encontrado.`
                    );
                    continue;
                }

                const invoiceData = await buildInvoiceSnapshot({
                    sessionId: sessionDoc.id,
                    userEmail: email,
                    session: sessionData as Parameters<
                        typeof buildInvoiceSnapshot
                    >[0]["session"],
                    charger,
                });

                missingInvoices.push({
                    id: sessionDoc.id,
                    data: invoiceData,
                });
            }

            // Em lotes menores que o limite máximo do Firestore.
            for (
                let start = 0;
                start < missingInvoices.length;
                start += BATCH_LIMIT
            ) {
                const batch = adminDb.batch();
                const chunk = missingInvoices.slice(
                    start,
                    start + BATCH_LIMIT
                );

                for (const invoice of chunk) {
                    batch.set(
                        invoicesRef.doc(invoice.id),
                        invoice.data
                    );
                }

                await batch.commit();
            }
            const currentEnergyFlag = await getEnergyFlagForDate(
                new Date().toISOString()
            );

            const invoicesSnapshot = await invoicesRef
                .where("userEmail", "==", email)
                .get();

            const invoices: Array<InvoiceDocument & { id: string }> =
                invoicesSnapshot.docs
                    .map((document) => ({
                        id: document.id,
                        ...(document.data() as InvoiceDocument),
                    }))
                    .sort(
                        (a, b) =>
                            Number(b.chargeDateMs ?? 0) -
                            Number(a.chargeDateMs ?? 0)
                    );

            const pendingTotal = invoices
                .filter((invoice) => invoice.status === "pending")
                .reduce(
                    (total, invoice) =>
                        total + Number(invoice.totalAmount ?? 0),
                    0
                );

            return res.status(200).json({
                invoices,
                pendingTotal: Math.round(
                    (pendingTotal + Number.EPSILON) * 100
                ) / 100,
                currentEnergyFlag,
            });
        }

        // POST: simula pagamento. Não processa dinheiro de verdade.
        const rawIds = req.body?.invoiceIds;

        if (
            !Array.isArray(rawIds) ||
            rawIds.length === 0 ||
            rawIds.length > 1000 ||
            rawIds.some(
                (id) => typeof id !== "string" || id.trim().length === 0
            )
        ) {
            return res.status(400).json({
                error: "Informe as faturas que deseja simular como pagas.",
            });
        }

        const invoiceIds = [...new Set(
            rawIds.map((id: string) => id.trim())
        )];

        // A consulta limita a operação às faturas do usuário autenticado.
        const ownedInvoicesSnapshot = await invoicesRef
            .where("userEmail", "==", email)
            .get();

        const ownedInvoices = new Map(
            ownedInvoicesSnapshot.docs.map((document) => [
                document.id,
                document,
            ])
        );

        const requestedDocuments = invoiceIds.map(
            (id) => ownedInvoices.get(id)
        );

        if (requestedDocuments.some((document) => !document)) {
            return res.status(404).json({
                error: "Uma ou mais faturas não foram encontradas na sua conta.",
            });
        }

        const toUpdate = requestedDocuments.filter(
            (document) => document!.data().status === "pending"
        );

        for (let start = 0; start < toUpdate.length; start += BATCH_LIMIT) {
            const batch = adminDb.batch();
            const chunk = toUpdate.slice(start, start + BATCH_LIMIT);

            for (const document of chunk) {
                batch.update(document!.ref, {
                    status: "paid_demo",
                    paymentMode: "simulation",
                    demoPaidAt: FieldValue.serverTimestamp(),
                });
            }

            await batch.commit();
        }

        return res.status(200).json({
            ok: true,
            simulatedCount: toUpdate.length,
            message:
                "Status atualizado em modo demonstrativo. Nenhum pagamento real foi realizado.",
        });
    } catch (error) {
        console.error("Erro na API de faturas:", error);

        return res.status(500).json({
            error: "Não foi possível processar as faturas.",
        });
    }
}