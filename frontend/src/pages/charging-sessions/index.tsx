
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/router";
import { ArrowLeft, Zap, Clock, CalendarDays } from "lucide-react";
import { mockChargers } from "@/data/mockChargers";

interface Vehicle {
  id: string;
  brand: string;
  model: string;
  year: number;
  plate?: string | null;
}

interface ChargingSession {
  id: string;
  vehicleId: string;
  vehicleBrand: string;
  vehicleModel: string;
  chargerId: string;
  chargerName: string;
  startedAt: string;
  durationMinutes: number;
  energyKwh: number;
}

function getLocalDateTimeValue() {
  const now = new Date();
  const localDate = new Date(
    now.getTime() - now.getTimezoneOffset() * 60_000
  );

  return localDate.toISOString().slice(0, 16);
}

export default function ChargingSessionsPage() {
  const router = useRouter();

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [sessions, setSessions] = useState<ChargingSession[]>([]);
  const [vehicleId, setVehicleId] = useState("");
  const [chargerId, setChargerId] = useState("");
  const [durationMinutes, setDurationMinutes] = useState("30");
  const [energyKwh, setEnergyKwh] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [startedAt, setStartedAt] = useState("");
  const startedAtInputRef = useRef<HTMLInputElement>(null);
  const [chargerError, setChargerError] = useState("");

  useEffect(() => {
    let active = true;

    setStartedAt(getLocalDateTimeValue());

    async function loadData() {
      try {
        const [vehiclesResponse, sessionsResponse] = await Promise.all([
          fetch("/api/vehicles"),
          fetch("/api/charging-sessions"),
        ]);

        const vehiclesData = await vehiclesResponse.json();
        const sessionsData = await sessionsResponse.json();

        if (!active) return;

        if (
          vehiclesResponse.status === 401 ||
          sessionsResponse.status === 401
        ) {
          void router.replace({
            pathname: "/auth/login",
            query: { callbackUrl: "/charging-sessions" },
          });
          return;
        }

        if (!vehiclesResponse.ok || !sessionsResponse.ok) {
          throw new Error(
            vehiclesData.error ||
              sessionsData.error ||
              "Não foi possível carregar os dados."
          );
        }

        setVehicles(vehiclesData.vehicles ?? []);
        setSessions(sessionsData.sessions ?? []);
      } catch (err) {
        if (!active) return;

        setError(
          err instanceof Error
            ? err.message
            : "Falha ao carregar as sessões."
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadData();

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
      const response = await fetch("/api/charging-sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          vehicleId,
          chargerId,
          startedAt: new Date(startedAt).toISOString(),
          durationMinutes: Number(durationMinutes),
          energyKwh: Number(energyKwh),
        }),
      });

      const data = await response.json();

      if (response.status === 401) {
        await router.replace({
          pathname: "/auth/login",
          query: { callbackUrl: "/charging-sessions" },
        });
        return;
      }

      if (!response.ok) {
        throw new Error(
          data.error || "Não foi possível registrar a sessão."
        );
      }

      setSessions((current) => [data.session, ...current]);
      setStartedAt(getLocalDateTimeValue());
      setChargerError("")
      setDurationMinutes("30");
      setEnergyKwh("");
      setSuccess("Sessão registrada com sucesso!");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Não foi possível registrar a sessão."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a] px-5 py-8 text-white sm:px-10">
      <div className="mx-auto max-w-5xl">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="mb-7 flex items-center gap-2 text-sm text-[#b3b3b3] transition hover:text-white"
        >
          <ArrowLeft size={16} />
          Voltar ao dashboard
        </button>

        <h1 className="text-3xl font-bold">
          Sessões de carregamento
        </h1>

        <p className="mt-2 mb-8 text-sm text-[#999]">
          Registre carregamentos e consulte seu histórico.
        </p>

        <form
          onSubmit={handleSubmit}
          className="mb-10 rounded-xl border border-[#27272A] bg-[#101010] p-5 sm:p-6"
        >
          <h2 className="mb-5 text-lg font-semibold">
            Registrar sessão
          </h2>

          {vehicles.length === 0 && !loading && (
            <p className="mb-5 rounded-lg border border-[#554b20] bg-[#2a2512] p-3 text-sm text-[#f0d941]">
              Você ainda não possui veículos cadastrados. Cadastre um
              veículo antes de registrar uma sessão.
              <button
                type="button"
                onClick={() => router.push("/vehicles")}
                className="ml-1 underline"
              >
                Ir para veículos
              </button>
            </p>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <label htmlFor="vehicle" className="text-sm text-[#b3b3b3]">
                Veículo
              </label>

              <select
                id="vehicle"
                value={vehicleId}
                onChange={(event) => setVehicleId(event.target.value)}
                required
                disabled={loading || vehicles.length === 0}
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941] disabled:opacity-50"
              >
                <option value="">Selecione um veículo</option>
                {vehicles.map((vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.brand} {vehicle.model} ({vehicle.year})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="charger" className="text-sm text-[#b3b3b3]">
                Carregador
              </label>

              <select
                id="charger"
                value={chargerId}
                onChange={(event) => {
                  const selectedId = event.target.value;
                  const charger = mockChargers.find(
                    (item) => item.id === selectedId
                  );

                  if (!charger) {
                    setChargerId("");
                    setChargerError("");
                    return;
                  }

                  if (charger.status !== "available") {
                    setChargerId("");

                    setChargerError(
                      `${charger.name} está indisponível no momento: ${
                        charger.status === "occupied" ? "está em uso" : "está offline"
                      }. Escolha um carregador livre ou volte em outro momento!`
                    );

                    return;
                  }

                  setChargerId(selectedId);
                  setChargerError("");
                }}
                required
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
              >
                <option value="">Selecione um carregador</option>

                {mockChargers.map((charger) => (
                  <option key={charger.id} value={charger.id}>
                    {charger.name} —{" "}
                    {charger.status === "available"
                      ? "Livre"
                      : charger.status === "occupied"
                        ? "Indisponível · Em uso"
                        : "Indisponível · Offline"}
                  </option>
                ))}
              </select>

              {chargerError && (
                <p role="alert" className="text-sm text-red-400">
                  {chargerError}
                </p>
              )}

              <p className="text-xs text-[#777]">
                Somente carregadores livres podem ser utilizados.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="startedAt" className="text-sm text-[#b3b3b3]">
                Início do carregamento
              </label>

              <div className="flex gap-2">
                <input
                  ref={startedAtInputRef}
                  id="startedAt"
                  type="datetime-local"
                  value={startedAt}
                  onChange={(event) => setStartedAt(event.target.value)}
                  required
                  className="min-w-0 flex-1 rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
                />

                <button
                  type="button"
                  title="Escolher data e horário"
                  aria-label="Abrir seletor de data e horário"
                  onClick={() => {
                    const input = startedAtInputRef.current;

                    if (!input) return;

                    if (typeof input.showPicker === "function") {
                      input.showPicker();
                    } else {
                      input.focus();
                      input.click();
                    }
                  }}
                  className="flex items-center justify-center rounded-lg border border-[#333] px-3 text-[#b3b3b3] transition hover:bg-[#1f1f1f] hover:text-white"
                >
                  <CalendarDays size={18} />
                </button>
              </div>

              <p className="text-xs text-[#777]">
                A data e o horário atuais são preenchidos automaticamente.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <label
                htmlFor="duration"
                className="text-sm text-[#b3b3b3]"
              >
                Duração (minutos)
              </label>

              <input
                id="duration"
                type="number"
                min={1}
                max={10080}
                step={1}
                value={durationMinutes}
                onChange={(event) => setDurationMinutes(event.target.value)}
                required
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
              />
            </div>

            <div className="flex flex-col gap-2 sm:col-span-2">
              <label htmlFor="energy" className="text-sm text-[#b3b3b3]">
                Energia carregada (kWh)
              </label>

              <input
                id="energy"
                type="number"
                min="0.01"
                max="10000"
                step="0.01"
                value={energyKwh}
                onChange={(event) => setEnergyKwh(event.target.value)}
                required
                placeholder="Ex.: 12.50"
                className="rounded-lg border border-[#333] bg-[#070707] px-3 py-3 text-sm outline-none focus:border-[#f0d941]"
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
            disabled={saving || loading || vehicles.length === 0}
            className="mt-5 rounded-lg bg-[#f0d941] px-5 py-3 text-sm font-semibold text-[#070707] transition hover:bg-[#d9c439] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? "Registrando..." : "Registrar carregamento"}
          </button>
        </form>

        <section>
          <h2 className="mb-4 text-lg font-semibold">
            Histórico de carregamentos ({sessions.length})
          </h2>

          {loading ? (
            <p className="text-sm text-[#999]">Carregando histórico...</p>
          ) : sessions.length === 0 ? (
            <div className="rounded-xl border border-dashed border-[#333] p-8 text-center text-sm text-[#999]">
              Nenhuma sessão registrada até agora.
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {sessions.map((item) => (
                <article
                  key={item.id}
                  className="rounded-xl border border-[#27272A] bg-[#101010] p-5"
                >
                  <h3 className="font-semibold">
                    {item.vehicleBrand} {item.vehicleModel}
                  </h3>

                  <p className="mt-1 text-sm text-[#999]">
                    {item.chargerName}
                  </p>

                  <div className="mt-4 flex flex-col gap-3 text-sm text-[#b3b3b3]">
                    <p className="flex items-center gap-2">
                      <CalendarDays size={16} />
                      {new Date(item.startedAt).toLocaleString("pt-BR")}
                    </p>

                    <p className="flex items-center gap-2">
                      <Clock size={16} />
                      {item.durationMinutes} minutos
                    </p>

                    <p className="flex items-center gap-2">
                      <Zap size={16} />
                      {Number(item.energyKwh).toLocaleString("pt-BR", {
                        maximumFractionDigits: 2,
                      })}{" "}
                      kWh
                    </p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
