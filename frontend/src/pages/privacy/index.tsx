import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <article className="mx-auto max-w-3xl space-y-6">
        <Link href="/settings" className="text-sm underline">
          ← Voltar às configurações
        </Link>

        <h1 className="text-3xl font-bold">Política de Privacidade</h1>

        <p className="rounded-lg border border-amber-500/40 p-4 text-sm">
          Rascunho em elaboração. Este conteúdo precisa ser revisado e aprovado
          antes de ser apresentado como política oficial.
        </p>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Dados tratados</h2>
          <p className="text-muted-foreground">
            Conforme as funcionalidades utilizadas, o GurAI pode armazenar
            informações de cadastro, e-mail, veículos, registros de
            carregamento e solicitações de suporte.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Finalidade</h2>
          <p className="text-muted-foreground">
            Essas informações são utilizadas pelas funcionalidades de conta,
            gerenciamento de veículos, histórico de carregamentos e atendimento
            ao usuário.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Solicitações e exclusão</h2>
          <p className="text-muted-foreground">
            Para solicitar suporte ou exclusão da conta, acesse a página de
            ajuda. O envio de uma solicitação não significa que os dados já
            foram excluídos.
          </p>
          <Link href="/help" className="underline">
            Acessar ajuda e suporte
          </Link>
        </section>

        <p className="text-sm text-muted-foreground">
          Antes da publicação, definir o responsável pelo tratamento, os
          contatos oficiais, os prazos de retenção, os direitos dos titulares e
          os procedimentos aplicáveis à legislação de proteção de dados.
        </p>
      </article>
    </main>
  );
}