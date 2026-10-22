import { useRouter } from "next/router";

export default function ChatDetailPage() {
  const router = useRouter();
  const { id } = router.query;

  return (
    <main className="min-h-screen bg-[#0a0a0a] p-6 text-white">
      <h1 className="text-2xl font-semibold">
        Conversa
      </h1>

      <p className="mt-2 text-sm text-neutral-400">
        {router.isReady
          ? `ID da conversa: ${id}`
          : "Carregando conversa..."}
      </p>
    </main>
  );
}