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
            onClick={(event) => {
              event.stopPropagation();
              onClose();
            }}
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

      <p className="mt-1 text-sm text-[#b3b3b3]">
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
            className="w-full rounded-md border border-[#1f1f1f] px-3 py-2 text-sm outine-none"
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
            className="w-full rounded-md border border-[#1f1f1f] px-3 py-2 text-sm outline-none"
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
            className="w-full rounded-md border border-[#1f1f1f] px-3 py-2 text-sm mb-[8px] outline-none"
          >
            <option className="text-[#000]" value="30">30 minutos</option>
            <option className="text-[#000]" value="60">1 hora</option>
            <option className="text-[#000]" value="90">1 hora e 30 minutos</option>
            <option className="text-[#000]" value="120">2 horas</option>
          </select>
        </div>
      </div>

      <button
        type="button"
        onClick={handleReservation}
        disabled={!date || !time}
        className="rounded-[8px] py-[6px] px-[15px] mb-[8px] text-[14px] bg-[#f0d941] w-full text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f] disabled:bg-[#a3921f]"
      >
        Confirmar reserva
      </button>

      <button
        type="button"
        onClick={onClose}
        className="flex items-center justify-center w-full rounded-[8px] py-[6px] px-[15px] text-[#fff] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A] disabled:bg-[#a3921f] "
      >
        Voltar
      </button>
    </div>
  );
}