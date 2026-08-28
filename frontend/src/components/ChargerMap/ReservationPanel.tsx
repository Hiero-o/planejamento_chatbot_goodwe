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
    if (!date || !time) {
      return;
    }

    setConfirmed(true);
  }

  if (confirmed) {
    return (
      <div className="min-w-[280px] p-2">
        <div className="text-center">
          <div className="text-3xl">✓</div>

          <h3 className="mt-2 text-base font-semibold">
            Reserva realizada!
          </h3>

          <p className="mt-2 text-sm text-gray-500">
            {charger.name}
          </p>

          <p className="text-sm text-gray-500">
            {date} às {time}
          </p>

          <p className="text-sm text-gray-500">
            Duração: {duration} minutos
          </p>

          <button
            type="button"
            onClick={onClose}
            className="mt-4 w-full rounded-md bg-[#ECFF00] px-4 py-2 text-sm font-medium text-black"
          >
            Fechar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-w-[280px] p-2">
      <h3 className="text-base font-semibold">
        Reservar carregador
      </h3>

      <p className="mt-1 text-sm text-gray-500">
        {charger.name}
      </p>

      <div className="mt-4 space-y-3">
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
            onChange={(event) =>
              setDate(event.target.value)
            }
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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
            onChange={(event) =>
              setTime(event.target.value)
            }
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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
            onChange={(event) =>
              setDuration(event.target.value)
            }
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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
        onClick={handleReservation}
        disabled={!date || !time}
        className="mt-5 w-full rounded-md bg-[#ECFF00] px-4 py-2 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-50"
      >
        Confirmar reserva
      </button>

      <button
        type="button"
        onClick={onClose}
        className="mt-2 w-full rounded-md px-4 py-2 text-sm text-gray-500 hover:bg-gray-100"
      >
        Voltar
      </button>
    </div>
  );
}