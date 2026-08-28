import ChargerMap from "@/components/ChargerMap";

export default function MonitoringPage() {
    return (
        <main className="w-full flex items-center justify-center flex-col">
            <header className="p-[12px] border-b border-[#1f1f1f] w-full">
                <h1 className="text-[14px]">Monitoramento</h1>
            </header>
            <ChargerMap />
        </main>
    )
}