
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/router";
import { ArrowLeft, CarFront, Plus, Trash2 } from "lucide-react";

interface Vehicle {
  id: string;
  brand: string;
  model: string;
  year: number;
  plate: string | null;
  createdAt: number;
}

export default function VehiclesPage() {
  const router = useRouter();

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [plate, setPlate] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function loadVehicles() {
      try {
        const response = await fetch("/api/vehicles");
        const data = await response.json();

        if (!active) return;

        if (response.status === 401) {
          void router.replace({
            pathname: "/auth/login",
            query: { callbackUrl: "/vehicles" },
          });
          return;
        }

        if (!response.ok) {
          throw new Error(data.error || "Não foi possível carregar os veículos.");
        }

        setVehicles(data.vehicles ?? []);
      } catch (err) {
        if (!active) return;

        setError(
          err instanceof Error
            ? err.message
            : "Não foi possível carregar os veículos."
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadVehicles();

    return () => {
      active = false;
    };
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("/api/vehicles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand,
          model,
          year,
          plate,
        }),
      });

      const data = await response.json();

      if (response.status === 401) {
        await router.replace({
          pathname: "/auth/login",
          query: { callbackUrl: "/vehicles" },
        });
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || "Não foi possível cadastrar o veículo.");
      }

      setVehicles((current) => [data.vehicle, ...current]);
      setBrand("");
      setModel("");
      setYear("");
      setPlate("");
      setSuccess("Veículo cadastrado com sucesso!");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Não foi possível cadastrar o veículo."
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    const confirmed = window.confirm(
      "Tem certeza de que deseja excluir este veículo?"
    );

    if (!confirmed) return;

    setDeletingId(id);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`/api/vehicles/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (response.status === 401) {
        await router.replace({
          pathname: "/auth/login",
          query: { callbackUrl: "/vehicles" },
        });
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || "Não foi possível excluir o veículo.");
      }

      setVehicles((current) => current.filter((vehicle) => vehicle.id !== id));
      setSuccess("Veículo excluído com sucesso!");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Não foi possível excluir o veículo."
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a] px-5 py-8 text-white sm:px-10">
      <div className="mx-auto max-w-4xl">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="mb-7 flex items-center gap-2 text-sm text-[#b3b3b3] transition hover:text-white"
        >
          <ArrowLeft size={16} />
          Voltar ao dashboard
        </button>

        <div className="mb-8 flex items-center gap-3">
          <CarFront size={30} />
          <div>
            <h1 className="text-3xl font-bold">Meus veículos</h1>
            <p className="mt-1 text-sm text-[#999]">
              Cadastre e consulte os veículos da sua conta.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="mb-8 rounded-xl border border-[#27272A] bg-[#101010] p-5 sm:p-6"
        >
          <h2 className="mb-5 flex items-center gap-2 text-lg font-semibold">
            <Plus size={19} />
            Adicionar veículo
          </h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <label htmlFor="brand" className="text-sm text-[#b3b3b3]">
                Marca
              </label>
              <input
                id="brand"
                value={brand}
                onChange={(event) => setBrand(event.target.value)}
                minLength={2}
                maxLength={50}
                required
                placeholder="Ex.: BYD"
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="model" className="text-sm text-[#b3b3b3]">
                Modelo
              </label>
              <input
                id="model"
                value={model}
                onChange={(event) => setModel(event.target.value)}
                maxLength={60}
                required
                placeholder="Ex.: Dolphin Mini"
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="year" className="text-sm text-[#b3b3b3]">
                Ano
              </label>
              <input
                id="year"
                type="number"
                value={year}
                onChange={(event) => setYear(event.target.value)}
                min={1886}
                max={new Date().getFullYear() + 2}
                required
                placeholder="Ex.: 2025"
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="plate" className="text-sm text-[#b3b3b3]">
                Placa (opcional)
              </label>
              <input
                id="plate"
                value={plate}
                onChange={(event) => setPlate(event.target.value.toUpperCase())}
                maxLength={10}
                placeholder="Ex.: ABC1D23"
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm uppercase outline-none focus:border-[#f0d941]"
              />
            </div>
          </div>

          {error && (
            <p role="alert" className="mt-4 text-sm text-red-400">
              {error}
            </p>
          )}

          {success && (
            <p role="status" className="mt-4 text-sm text-green-400">
              {success}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="mt-5 flex items-center justify-center gap-2 rounded-lg bg-[#f0d941] px-5 py-3 text-sm font-semibold text-[#070707] transition hover:bg-[#d9c439] disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Plus size={17} />
            {saving ? "Salvando..." : "Cadastrar veículo"}
          </button>
        </form>

        <section>
          <h2 className="mb-4 text-lg font-semibold">
            Veículos cadastrados ({vehicles.length})
          </h2>

          {loading ? (
            <p className="text-sm text-[#999]">Carregando veículos...</p>
          ) : vehicles.length === 0 ? (
            <div className="rounded-xl border border-dashed border-[#333] p-8 text-center">
              <CarFront size={32} className="mx-auto mb-3 text-[#777]" />
              <p className="text-sm text-[#b3b3b3]">
                Você ainda não cadastrou nenhum veículo.
              </p>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {vehicles.map((vehicle) => (
                <article
                  key={vehicle.id}
                  className="flex items-start justify-between gap-4 rounded-xl border border-[#27272A] bg-[#101010] p-5"
                >
                  <div className="flex min-w-0 gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#1f1f1f]">
                      <CarFront size={20} />
                    </div>

                    <div className="min-w-0">
                      <h3 className="font-semibold">
                        {vehicle.brand} {vehicle.model}
                      </h3>
                      <p className="mt-1 text-sm text-[#999]">
                        Ano {vehicle.year}
                      </p>
                      {vehicle.plate && (
                        <p className="mt-1 text-xs text-[#777]">
                          Placa: {vehicle.plate}
                        </p>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => void handleDelete(vehicle.id)}
                    disabled={deletingId === vehicle.id}
                    aria-label={`Excluir ${vehicle.brand} ${vehicle.model}`}
                    title="Excluir veículo"
                    className="rounded-md p-2 text-[#999] transition hover:bg-red-950 hover:text-red-400 disabled:opacity-50"
                  >
                    <Trash2 size={17} />
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
