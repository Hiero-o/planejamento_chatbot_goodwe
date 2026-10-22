"use client";

import { useState } from "react";
import type { Charger } from "@/data/mockChargers";

interface ReservationPanelProps {
  charger: Charger;
  onClose: () => void;
}

export default function ReservationPanel({
  charger,
  onClose,
}: ReservationPanelProps) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [duration, setDuration] = useState("30");
  const [confirmed, setConfirmed] = useState(false);

  function handleReservation() {
    if (!date || !time) return;

    setConfirmed(true);
  }

  const primaryButtonClass =
    "mb-2 w-full cursor-pointer rounded-lg bg-[#f0d941] px-[15px] py-[8px] text-sm font-semibold text-[#070707] transition-colors hover:bg-[#a3921f] disabled:cursor-not-allowed disabled:opacity-50";

  const secondaryButtonClass =
    "flex w-full cursor-pointer items-center justify-center rounded-lg border border-border bg-card px-[15px] py-[8px] text-sm font-semibold text-card-foreground transition-colors hover:bg-muted";

  if (confirmed) {
    return (
      <div className="min-w-[280px] space-y-3 bg-popover p-2 text-popover-foreground">
        <div className="text-center">
          <div className="text-3xl text-green-600">✓</div>

          <h3 className="mt-2 text-base font-semibold">
            Reserva realizada!
          </h3>

          <p className="mt-3 text-sm text-muted-foreground">
            {charger.name}
          </p>

          <p className="text-sm text-muted-foreground">
            {date} às {time}
          </p>

          <p className="text-sm text-muted-foreground">
            Duração: {duration} minutos
          </p>

          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              onClose();
            }}
            className={`${primaryButtonClass} mt-4`}
          >
            Fechar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-w-[280px] space-y-3 bg-popover p-2 text-popover-foreground">
      <h3 className="text-base font-semibold">
        Reservar carregador
      </h3>

      <p className="text-sm text-muted-foreground">
        {charger.name}
      </p>

      <div className="space-y-3 pt-1">
        <div>
          <label
            htmlFor="reservation-date"
            className="mb-1 block text-xs font-medium"
          >
            Data
          </label>

          <input
            id="reservation-date"
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        <div>
          <label
            htmlFor="reservation-time"
            className="mb-1 block text-xs font-medium"
          >
            Horário
          </label>

          <input
            id="reservation-time"
            type="time"
            value={time}
            onChange={(event) => setTime(event.target.value)}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        <div>
          <label
            htmlFor="reservation-duration"
            className="mb-1 block text-xs font-medium"
          >
            Duração
          </label>

          <select
            id="reservation-duration"
            value={duration}
            onChange={(event) => setDuration(event.target.value)}
            className="mb-2 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="30">30 minutos</option>
            <option value="60">1 hora</option>
            <option value="90">1 hora e 30 minutos</option>
            <option value="120">2 horas</option>
          </select>
        </div>
      </div>

      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          handleReservation();
        }}
        disabled={!date || !time}
        className={primaryButtonClass}
      >
        Confirmar reserva
      </button>

      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          onClose();
        }}
        className={secondaryButtonClass}
      >
        Voltar
      </button>
    </div>
  );
}