"use client";

import { useState } from "react";
import Link from "next/link";

import type { Charger } from "@/data/mockChargers";

import ReservationPanel from "./ReservationPanel";

interface ChargerPopupProps {
  charger: Charger;
}

function getStatusInfo(status: Charger["status"]) {
  switch (status) {
    case "available":
      return {
        label: "Disponível",
        icon: "🟢",
      };

    case "occupied":
      return {
        label: "Em uso",
        icon: "🟡",
      };

    case "offline":
      return {
        label: "Offline",
        icon: "🔴",
      };
  }
}

export default function ChargerPopup({
  charger,
}: ChargerPopupProps) {
  const [reservationOpen, setReservationOpen] =
    useState(false);

  const status = getStatusInfo(charger.status);

  if (reservationOpen) {
    return (
      <ReservationPanel
        charger={charger}
        onClose={() => setReservationOpen(false)}
      />
    );
  }

  return (
    <div className="min-w-[280px] p-2">
      <h3 className="text-base font-semibold">
        {charger.name}
      </h3>

      <p className="mt-2 text-sm">
        {status.icon} {status.label}
      </p>

      <div className="mt-3 space-y-1 text-sm">
        <p>
          ⚡ {charger.power} kW
        </p>

        <p>
          🔌 {charger.connectors} conectores
        </p>

        <p>
            💰 Tarifa: {charger.establishment.tarifa}
        </p>
        
      </div>

      <div className="my-3 border-t border-gray-200" />

      <Link
        href={`/establishments/${charger.establishment.id}`}
        className="font-medium text-blue-600 hover:underline"
      >
        {charger.establishment.name}
      </Link>

      <p className="text-sm text-gray-500">
        {charger.establishment.address}
      </p>

      <div className="mt-4 space-y-2">
        <button
          type="button"
          onClick={() => setReservationOpen(true)}
          disabled={charger.status !== "available"}
          className="w-full rounded-md bg-[#ECFF00] px-4 py-2 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-50"
        >
          ⚡ Reservar carregador
        </button>

        <Link
          href={`/establishments/${charger.establishment.id}`}
          className="block w-full rounded-md border border-gray-300 px-4 py-2 text-center text-sm font-medium hover:bg-gray-100"
        >
          🏢 Ver estabelecimento
        </Link>
      </div>
    </div>
  );
}