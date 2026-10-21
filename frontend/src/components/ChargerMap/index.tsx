import dynamic from "next/dynamic";

const ChargerMap = dynamic(
  () => import("./Map"),
  {
    ssr: false,
  }
);

export default ChargerMap;