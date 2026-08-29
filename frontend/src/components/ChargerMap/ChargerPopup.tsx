"use client";

import { useState } from "react";
import Link from "next/link";

import type { Charger } from "@/data/mockChargers";

import { Circle, CircleDashed, CircleOff } from 'lucide-react'

import ReservationPanel from "./ReservationPanel";

interface ChargerPopupProps {
  charger: Charger;
}

function getStatusInfo(status: Charger["status"]) {
  switch (status) {
    case "available":
      return {
        label: "Disponível",
        icon: <Circle size={15} color="#2dcf3d"/>,
      };

    case "occupied":
      return {
        label: "Em uso",
        icon: <CircleDashed size={15} color="#f0d941"/>,
      };

    case "offline":
      return {
        label: "Offline",
        icon: <CircleOff size={15} color="#e01f53"/>,
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
    <>
      <div className="min-w-[280px] p-2">
        <h3 className="text-base font-semibold">
          {charger.name}
        </h3>

        <p className="mt-2 text-sm flex items-center justify-start flex-row">
          {status.icon}
          <span className="ml-[5px]">{status.label}</span>
        </p>

        <div className="mt-3 space-y-1 text-sm">
          <p>
             {charger.power} kW
          </p>

          <p>
            {charger.connectors} conectores
          </p>

          <p>
            Tarifa: {charger.establishment.tarifa}
          </p>

        </div>

        <div className="my-3 border-t border-[#1f1f1f]" />

        <Link
          href={`/establishments/${charger.establishment.id}`}
          className="font-medium text-blue-600 hover:underline"
        >
          {charger.establishment.name}
        </Link>

        <p className="text-sm text-gray-500">
          {charger.establishment.address}
        </p>

        <div className="mt-4">
          <button
            type="button"
            onClick={() => setReservationOpen(true)}
            disabled={charger.status !== "available"}
            className="rounded-[8px] mb-[8px] py-[6px] px-[15px] text-[14px] bg-[#f0d941] w-full text-[#070707] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#a3921f] disabled:bg-[#a3921f]"
          >
            Reservar carregador
          </button>

          <Link
            style={{ color: "#fff" }}
            href={`/establishments/${charger.establishment.id}`}
            className="flex items-center justify-center rounded-[8px] py-[6px] px-[15px] text-[#fff] text-[14px] border border-[#27272A] bg-[#070707] text-[#bebebe] font-semibold cursor-pointer transition-[0.2s] hover:bg-[#27272A] disabled:bg-[#a3921f] "
          >
            Ver estabelecimento
          </Link>
        </div>
      </div>
      <style jsx global>{`
        .leaflet-popup-content-wrapper {
          background: #0a0a0a;
          color: white;
        }

        .leaflet-popup-tip {
          background: #0a0a0a;
        }

        .leaflet-popup-close-button {
          color: white !important;
        }
      `}</style>
    </>
  );
}