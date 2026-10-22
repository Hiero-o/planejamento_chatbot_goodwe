import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

const categories = [
  "Dúvida geral",
  "Problema na conta",
  "Alterar senha ou acesso",
  "Excluir conta",
  "Outro",
];

export default function HelpPage() {
  const router = useRouter();
  const [category, setCategory] = useState("Dúvida geral");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");

  useEffect(() => {
    const queryCategory = router.query.category;

    if (
      typeof queryCategory === "string" &&
      categories.includes(queryCategory)
    ) {
      setCategory(queryCategory);
    }
  }, [router.query.category]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setFeedback("");

    try {
      const response = await fetch("/api/support", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, message }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Não foi possível enviar a solicitação.");
      }

      setFeedback(
        `Solicitação registrada com sucesso. Protocolo: ${data.ticketId}`
      );
      setMessage("");
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "Ocorreu um erro ao enviar a solicitação."
      );
    } finally {
      setLoading(false);
    }
  }

  const sectionClass =
    "rounded-xl border border-border bg-card p-5 space-y-3";

  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <div className="mx-auto max-w-3xl space-y-6">
        <button
            type="button"
            onClick={() => {
                const from = router.query.from;

                const returnTo =
                typeof from === "string" &&
                ["/", "/dashboard"].includes(from)
                    ? from
                    : "/dashboard";

                void router.push(returnTo);
            }}
            className="text-sm text-muted-foreground hover:underline"
            >
            ← Voltar
        </button>

        <header>
          <h1 className="text-3xl font-bold">Ajuda e suporte</h1>
          <p className="mt-2 text-muted-foreground">
            Consulte as perguntas frequentes ou envie uma solicitação.
          </p>
        </header>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Perguntas frequentes</h2>

          <details className="border-b border-border py-3">
            <summary className="cursor-pointer font-medium">
              Como alterar meus dados?
            </summary>
            <p className="mt-2 text-muted-foreground">
              Acesse as configurações da conta e escolha “Meu perfil” para
              visualizar os campos disponíveis para edição.
            </p>
          </details>

          <details className="border-b border-border py-3">
            <summary className="cursor-pointer font-medium">
              Como alterar minha senha?
            </summary>
            <p className="mt-2 text-muted-foreground">
              O GurAI oferece acesso por código de verificação enviado por
              e-mail ou por conta Google. Se você utiliza Google, gerencie sua
              senha na segurança da sua conta Google.
            </p>
          </details>

          <details className="border-b border-border py-3">
            <summary className="cursor-pointer font-medium">
              Como excluir minha conta?
            </summary>
            <p className="mt-2 text-muted-foreground">
              Envie uma solicitação de exclusão pelo formulário abaixo. Nesta
              versão, a solicitação é registrada para análise; a conta ainda
              não é apagada automaticamente.
            </p>
          </details>

          <details className="py-3">
            <summary className="cursor-pointer font-medium">
              Como gerenciar meus veículos?
            </summary>
            <p className="mt-2 text-muted-foreground">
              Abra a página de veículos para consultar os cadastrados e acessar
              as opções disponíveis.
            </p>
            <Link href="/vehicles" className="mt-2 inline-block underline">
              Ir para meus veículos
            </Link>
          </details>
        </section>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Solicitar suporte</h2>
          <p className="text-muted-foreground">
            Descreva o problema ou sua dúvida. Não envie senhas, códigos de
            verificação nem dados de cartão.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="category" className="block font-medium">
                Assunto
              </label>
              <select
                id="category"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                className="w-full rounded-lg border border-border bg-background p-3"
              >
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="message" className="block font-medium">
                Como podemos ajudar?
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                minLength={10}
                maxLength={3000}
                required
                rows={5}
                placeholder="Descreva sua dúvida ou problema..."
                className="w-full rounded-lg border border-border bg-background p-3"
              />
              <p className="text-sm text-muted-foreground">
                De 10 a 3.000 caracteres.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-blue-600 px-5 py-3 font-medium text-white disabled:opacity-50"
            >
              {loading ? "Enviando..." : "Enviar solicitação"}
            </button>

            {feedback && (
              <p role="status" className="break-words text-sm">
                {feedback}
              </p>
            )}
          </form>
        </section>
      </div>
    </main>
  );
}