"use client";

import React from 'react';
import { renderToString } from 'react-dom/server'; // Importação necessária para converter o JSX em String
import * as L from "leaflet";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import {
  mockChargers,
  type Charger,
} from "@/data/mockChargers";

import ChargerPopup from "./ChargerPopup";
import MapLegend from "./MapLegend";


// 1. Componente do Ícone SVG (Ajustado o xmlns obrigatório para renderizar)
export function MapPinIcon({
  size = 45,
  color = "red",
  ...props
}: {
  size?: number;
  color?: string;
  [key: string]: any;
}) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={color}
      fillOpacity={0.2}
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" />

      <circle
        cx="12"
        cy="10"
        r="3"
        fill="white"
        fillOpacity="0.9"
      />
    </svg>
  );
}

// 2. Criando o ícone do Leaflet usando L.divIcon com a String do SVG
function getChargerIcon(status: Charger["status"]) {
  const colors = {
    available: "#22c55e",
    occupied: "#ffda6b",
    offline: "#ef4444",
  };

  return L.divIcon({
    html: renderToString(
      <MapPinIcon
        size={45}
        color={colors[status]}
      />
    ),
    className: "custom-leaflet-pin",
    iconSize: [45, 45],
    iconAnchor: [22.5, 45],
    popupAnchor: [0, -45],
  });
}

export default function Map() {
  return (
    <div className="relative w-full h-[500px] rounded-[8px] overflow-hidden">
      <MapContainer
        center={[-23.5505, -46.6333]}
        zoom={13}
        className="w-full h-full"
        style={{ zIndex: 0 }} // Garantindo que o mapa fique atrás dos outros elementos
      >
        <TileLayer
          url={`https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=${process.env.NEXT_PUBLIC_CARTO_API_KEY}`}
          attribution='&copy; OpenStreetMap contributors &copy; CARTO'
          subdomains={["a", "b", "c", "d"]}
          maxZoom={20}
        />

        {mockChargers.map((charger) => (
          <Marker
            key={charger.id}
            position={[
              charger.latitude,
              charger.longitude,
            ]}
            icon={getChargerIcon(charger.status)} // 3. Aplicando o novo ícone aqui
          >
            <Popup>
              <ChargerPopup charger={charger} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <MapLegend />
    </div>
  );
}
