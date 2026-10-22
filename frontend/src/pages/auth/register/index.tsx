import { useState, type FormEvent } from "react";
import { useRouter } from "next/router";

export default function Register() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function handleRegister(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          email: email.trim().toLowerCase(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.error || "Não foi possível realizar o cadastro."
        );
        return;
      }

      setSuccess(true);
    } catch (error) {
      console.error("Erro no cadastro:", error);

      setError(
        "Não foi possível conectar ao servidor. Tente novamente."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-[#0a0a0a] px-4 text-white">
      <img
        src="/icon.png"
        alt="GurAI"
        className="mb-4 h-[35px] w-[20px]"
      />

      <h1 className="mb-2 text-[30px] font-bold">
        Criar conta
      </h1>

      <p className="mb-6 max-w-[300px] text-center text-[14px] text-[#b3b3b3]">
        Cadastre-se para acessar o GurAI.
      </p>

      {success ? (
        <div className="w-full max-w-[300px] text-center">
          <p className="mb-5 text-sm text-green-400">
            Cadastro realizado com sucesso! Agora você pode
            entrar com seu e-mail.
          </p>

          <button
            type="button"
            onClick={() => router.push("/auth/login")}
            className="w-full rounded-lg bg-[#f0d941] px-4 py-2 text-sm font-semibold text-[#070707] transition hover:bg-[#a3921f]"
          >
            Ir para o login
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleRegister}
          className="flex w-full max-w-[300px] flex-col"
        >
          <label
            htmlFor="username"
            className="mb-1 text-sm text-[#b3b3b3]"
          >
            Nome
          </label>

          <input
            id="username"
            type="text"
            value={username}
            onChange={(event) =>
              setUsername(event.target.value)
            }
            minLength={2}
            maxLength={60}
            autoComplete="name"
            required
            placeholder="Seu nome"
            className="mb-4 w-full rounded-lg border border-[#27272A] bg-[#070707] px-3 py-2 text-sm outline-none transition focus:border-[#47474b]"
          />

          <label
            htmlFor="email"
            className="mb-1 text-sm text-[#b3b3b3]"
          >
            E-mail
          </label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            autoComplete="email"
            maxLength={254}
            required
            placeholder="seu@email.com"
            className="mb-4 w-full rounded-lg border border-[#27272A] bg-[#070707] px-3 py-2 text-sm outline-none transition focus:border-[#47474b]"
          />

          {error && (
            <p
              role="alert"
              className="mb-4 text-sm text-red-400"
            >
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-[#f0d941] px-4 py-2 text-sm font-semibold text-[#070707] transition hover:bg-[#a3921f] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Cadastrando..." : "Criar conta"}
          </button>
        </form>
      )}
    </main>
  );
}