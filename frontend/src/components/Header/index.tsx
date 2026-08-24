import ItemNav from "./ItemNav";

export default function Header() {
  return (
    <header className="flex items-center justify-center h-[80px] sticky top-0 z-[999] transition-[0.2s] bg-[#0a0a0a]/70 backdrop-blur-md w-full">
      <div className="flex items-center justify-between max-w-[1000px] w-[90%]">
        <img src="/icon.png" alt="" className="h-[35px] w-[20px]" />
        <nav className="hidden items-center justify-center flex-row gap-[5px] md:flex">
          <ItemNav label="Planos" />
          <ItemNav label="Dashboard" />
          <ItemNav label="Suporte" />
          <button className="rounded-[8px] py-[5px] px-[15px] text-[14px] bg-[#ECFF00] text-[#070707] font-medium cursor-pointer transition-[0.2s] hover:bg-[#a5af11]">
            Acessar
          </button>
        </nav>
      </div>
    </header>
  );
}
