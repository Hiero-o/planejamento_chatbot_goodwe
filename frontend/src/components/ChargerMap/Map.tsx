"use client";

import * as L from "leaflet";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import { mockChargers } from "@/data/mockChargers";

import ChargerPopup from "./ChargerPopup";

import MapLegend from "./MapLegend";

const chargerIcon = L.icon({
  iconUrl: "/images/marker-25p.png",

  iconSize: [45, 45],
  iconAnchor: [22.5, 45],
  popupAnchor: [0, -45],
});

export default function Map() {
  return (
    <div className="relative w-full h-[500px]">
      <MapContainer
        center={[-23.5505, -46.6333]}
        zoom={13}
        className="w-full h-full"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {mockChargers.map((charger) => (
          <Marker
            key={charger.id}
            position={[
              charger.latitude,
              charger.longitude,
            ]}
            icon={chargerIcon}
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