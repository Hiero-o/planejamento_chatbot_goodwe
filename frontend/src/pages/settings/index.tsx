import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";

type Preferences = {
  theme: "dark" | "light";
  fontSize: "small" | "medium" | "large";
};

const defaultPreferences: Preferences = {
  theme: "dark",
  fontSize: "medium",
};

export default function SettingsPage() {
  const router = useRouter();
  const [preferences, setPreferences] =
    useState<Preferences>(defaultPreferences);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("gurai-preferences");

      if (saved) {
        const parsed = JSON.parse(saved);

        const next: Preferences = {
          theme: parsed.theme === "light" ? "light" : "dark",
          fontSize: ["small", "medium", "large"].includes(parsed.fontSize)
            ? parsed.fontSize
            : "medium",
        };

        setPreferences(next);
        document.documentElement.dataset.theme = next.theme;
        document.documentElement.dataset.fontSize = next.fontSize;
      }
    } catch (error) {
      console.error("Erro ao carregar preferências:", error);
    }
  }, []);

  function updatePreferences(next: Preferences) {
    setPreferences(next);
    localStorage.setItem("gurai-preferences", JSON.stringify(next));

    document.documentElement.dataset.theme = next.theme;
    document.documentElement.dataset.fontSize = next.fontSize;

    window.dispatchEvent(new Event("gurai:preferences-changed"));
  }

  const sectionClass =
    "rounded-xl border border-border bg-card p-5 space-y-3";
  const linkClass =
    "inline-flex rounded-lg border border-border px-4 py-2 hover:opacity-80";

  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <div className="mx-auto max-w-3xl space-y-6">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="text-sm text-muted-foreground hover:underline"
        >
          ← Voltar para a dashboard
        </button>

        <header>
          <h1 className="text-3xl font-bold">Configurações</h1>
          <p className="mt-2 text-muted-foreground">
            Personalize sua experiência no GurAI e gerencie sua conta.
          </p>
        </header>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Aparência</h2>

          <div className="space-y-2">
            <label htmlFor="theme" className="block font-medium">
              Cor de fundo
            </label>
            <select
              id="theme"
              className="w-full rounded-lg border border-border bg-background p-3"
              value={preferences.theme}
              onChange={(event) =>
                updatePreferences({
                  ...preferences,
                  theme: event.target.value as Preferences["theme"],
                })
              }
            >
              <option value="dark">Preto — tema escuro</option>
              <option value="light">Branco — tema claro</option>
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="fontSize" className="block font-medium">
              Tamanho da fonte
            </label>
            <select
              id="fontSize"
              className="w-full rounded-lg border border-border bg-background p-3"
              value={preferences.fontSize}
              onChange={(event) =>
                updatePreferences({
                  ...preferences,
                  fontSize: event.target.value as Preferences["fontSize"],
                })
              }
            >
              <option value="small">Pequena</option>
              <option value="medium">Média</option>
              <option value="large">Grande</option>
            </select>
            <p className="text-sm text-muted-foreground">
              O tamanho da fonte afeta principalmente os textos que utilizam
              tamanhos relativos. Componentes com tamanhos fixos podem não mudar.
            </p>
          </div>
        </section>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Gerenciar conta</h2>
          <p className="text-muted-foreground">
            Atualize suas informações pessoais ou gerencie seus veículos.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/profile" className={linkClass}>
              Meu perfil
            </Link>
            <Link href="/vehicles" className={linkClass}>
              Meus veículos
            </Link>
          </div>
        </section>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Senha e acesso</h2>
          <p className="text-muted-foreground">
            O GurAI utiliza código de verificação por e-mail ou autenticação
            com Google. No acesso por código, não há uma senha do GurAI para
            alterar.
          </p>
          <a
            href="https://myaccount.google.com/security"
            target="_blank"
            rel="noreferrer"
            className={linkClass}
          >
            Segurança da conta Google
          </a>
        </section>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Métodos de pagamento</h2>
          <p className="text-muted-foreground">
            O gerenciamento de cartões ainda não está integrado. Não informe
            nem armazene os dados do seu cartão nesta página.
          </p>
        </section>

        <section className={sectionClass}>
          <h2 className="text-xl font-semibold">Privacidade e termos</h2>
          <div className="flex flex-wrap gap-3">
            <Link href="/privacy" className={linkClass}>
              Privacidade
            </Link>
            <Link href="/terms" className={linkClass}>
              Termos de uso
            </Link>
          </div>
        </section>

        <section className="rounded-xl border border-red-500/40 bg-card p-5 space-y-3">
          <h2 className="text-xl font-semibold text-red-500">
            Excluir conta
          </h2>
          <p className="text-muted-foreground">
            Solicite ajuda para excluir sua conta e os dados associados. A
            exclusão ainda não é automática nesta versão.
          </p>
          <button
            type="button"
            onClick={() =>
              router.push("/help?category=Excluir%20conta")
            }
            className="rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Solicitar exclusão
          </button>
        </section>
      </div>
    </main>
  );
}