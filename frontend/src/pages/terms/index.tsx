import Link from "next/link";

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <article className="mx-auto max-w-3xl space-y-6">
        <Link href="/settings" className="text-sm underline">
          ← Voltar às configurações
        </Link>

        <h1 className="text-3xl font-bold">Termos de Uso</h1>

        <p className="rounded-lg border border-amber-500/40 p-4 text-sm">
          Rascunho em elaboração. Estes termos precisam de revisão antes de
          serem adotados oficialmente.
        </p>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Uso do serviço</h2>
          <p className="text-muted-foreground">
            O GurAI oferece funcionalidades de conta, cadastro de veículos,
            registros de carregamento e assistência ao usuário. O usuário deve
            fornecer informações corretas e utilizar o serviço de forma lícita.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Informações e indicadores</h2>
          <p className="text-muted-foreground">
            Os registros e indicadores devem ser interpretados de acordo com a
            origem dos dados. Nesta versão, alguns carregadores e seus estados
            são dados demonstrativos, não confirmação de telemetria em tempo
            real.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Conta e suporte</h2>
          <p className="text-muted-foreground">
            O usuário pode acessar as funcionalidades de perfil e enviar
            solicitações de suporte. Procedimentos de cancelamento, exclusão,
            responsabilidades e limitações do serviço devem ser definidos nos
            termos oficiais.
          </p>
          <Link href="/help" className="underline">
            Acessar ajuda e suporte
          </Link>
        </section>

        <p className="text-sm text-muted-foreground">
          Antes da publicação, definir a identificação do responsável pelo
          serviço, as condições de uso, as regras de cancelamento e os canais
          oficiais de contato.
        </p>
      </article>
    </main>
  );
}