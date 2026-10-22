
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/router";

interface Profile {
  email: string;
  username: string;
  phone: string;
}

export default function ProfilePage() {
  const router = useRouter();

  const [profile, setProfile] = useState<Profile>({
    email: "",
    username: "",
    phone: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      try {
        const response = await fetch("/api/profile");
        const data = await response.json();

        if (!active) return;

        if (response.status === 401) {
          await router.replace({pathname: "/auth/login", query: { callbackUrl: router.asPath } });
          return;
        }

        if (!response.ok) {
          throw new Error(data.error || "Não foi possível carregar o perfil.");
        }

        setProfile({
          email: data.email ?? "",
          username: data.username ?? "",
          phone: data.phone ?? "",
        });
      } catch (err) {
        if (!active) return;

        console.error("Erro ao carregar perfil:", err);
        setError(
          err instanceof Error
            ? err.message
            : "Não foi possível carregar o perfil."
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadProfile();

    return () => {
      active = false;
    };
  }, [router]);

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: profile.username,
          phone: profile.phone,
        }),
      });

      const data = await response.json();

      if (response.status === 401) {
        await router.replace("/auth/login");
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || "Não foi possível salvar o perfil.");
      }

      setSuccess("Perfil atualizado com sucesso!");
    } catch (err) {
      console.error("Erro ao salvar perfil:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Não foi possível salvar o perfil."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0a0a0a] text-[#b3b3b3]">
        Carregando perfil...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a] px-5 py-10 text-white sm:px-10">
      <div className="mx-auto max-w-xl">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="mb-8 text-sm text-[#b3b3b3] transition hover:text-white"
        >
          ← Voltar ao dashboard
        </button>

        <h1 className="text-3xl font-bold">Meu perfil</h1>
        <p className="mt-2 mb-8 text-sm text-[#b3b3b3]">
          Consulte e atualize suas informações pessoais.
        </p>

        <form
          onSubmit={handleSave}
          className="flex flex-col gap-5 rounded-xl border border-[#27272A] bg-[#101010] p-6"
        >
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="text-sm text-[#b3b3b3]">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={profile.email}
              readOnly
              className="w-full rounded-lg border border-[#27272A] bg-[#070707] px-3 py-3 text-sm text-[#777] outline-none"
            />
            <p className="text-xs text-[#777]">
              O e-mail está vinculado à sua sessão e não pode ser alterado aqui.
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="username" className="text-sm text-[#b3b3b3]">
              Nome
            </label>
            <input
              id="username"
              type="text"
              value={profile.username}
              onChange={(event) =>
                setProfile((current) => ({
                  ...current,
                  username: event.target.value,
                }))
              }
              minLength={2}
              maxLength={60}
              autoComplete="name"
              required
              className="w-full rounded-lg border border-[#27272A] bg-[#070707] px-3 py-3 text-sm outline-none transition focus:border-[#f0d941]"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="phone" className="text-sm text-[#b3b3b3]">
              Telefone
            </label>
            <input
              id="phone"
              type="tel"
              value={profile.phone}
              onChange={(event) =>
                setProfile((current) => ({
                  ...current,
                  phone: event.target.value,
                }))
              }
              maxLength={30}
              autoComplete="tel"
              placeholder="(11) 99999-9999"
              className="w-full rounded-lg border border-[#27272A] bg-[#070707] px-3 py-3 text-sm outline-none transition focus:border-[#f0d941]"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-400">
              {error}
            </p>
          )}

          {success && (
            <p role="status" className="text-sm text-green-400">
              {success}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="mt-2 rounded-lg bg-[#f0d941] px-4 py-3 text-sm font-semibold text-[#070707] transition hover:bg-[#d9c439] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? "Salvando..." : "Salvar alterações"}
          </button>
        </form>
      </div>
    </main>
  );
}
