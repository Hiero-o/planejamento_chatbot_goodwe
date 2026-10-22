export interface Charger {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  status: "available" | "occupied" | "offline";
  power: number;
  connectors: number;
  establishment: {
    id: string;
    name: string;
    address: string;
    tarifa: string;
    basePricePerKwh: number;
    passThroughEnergyFlag: boolean;
  };
}

// ATENÇÃO: tarifas-base e percentuais são valores demonstrativos.
// Ajuste-os de acordo com as regras comerciais de cada estabelecimento.
const DEMO_BASE_PRICE_PER_KWH = 1.85;

export const mockChargers: Charger[] = [
  {
    id: "charger-001",
    name: "Gurgel Charger #001",
    latitude: -23.5505,
    longitude: -46.6333,
    status: "available",
    power: 150,
    connectors: 4,
    establishment: {
      id: "shopping-gurgel",
      name: "Shopping Gurgel",
      address: "São Paulo - SP",
      tarifa: "10%",
      basePricePerKwh: DEMO_BASE_PRICE_PER_KWH,
      passThroughEnergyFlag: true,
    },
  },
  {
    id: "charger-002",
    name: "Gurgel Charger #002",
    latitude: -23.556,
    longitude: -46.64,
    status: "occupied",
    power: 60,
    connectors: 2,
    establishment: {
      id: "posto-central",
      name: "Posto Central",
      address: "São Paulo - SP",
      tarifa: "15%",
      basePricePerKwh: DEMO_BASE_PRICE_PER_KWH,
      passThroughEnergyFlag: true,
    },
  },
  {
    id: "charger-003",
    name: "Gurgel Charger #003",
    latitude: -23.545,
    longitude: -46.625,
    status: "offline",
    power: 120,
    connectors: 3,
    establishment: {
      id: "mercado-central",
      name: "Mercado Central",
      address: "São Paulo - SP",
      tarifa: "9%",
      basePricePerKwh: DEMO_BASE_PRICE_PER_KWH,
      passThroughEnergyFlag: true,
    },
  },
  {
    id: "charger-004",
    name: "Gurgel Charger #004",
    latitude: -23.562,
    longitude: -46.628,
    status: "available",
    power: 180,
    connectors: 6,
    establishment: {
      id: "estacionamento-gurgel",
      name: "Estacionamento Gurgel",
      address: "São Paulo - SP",
      tarifa: "7%",
      basePricePerKwh: DEMO_BASE_PRICE_PER_KWH,
      passThroughEnergyFlag: true,
    },
  },
];