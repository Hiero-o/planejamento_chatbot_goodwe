import type { Charger } from "@/data/mockChargers";

import Link from "next/link";


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
    const status = getStatusInfo(charger.status);

    return (
        <div className="min-w-[220px]">
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
        </div>
    );
}