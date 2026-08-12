import { TbSunHighFilled } from "react-icons/tb";

export default function Header() {
    return (
        <header className="flex items-center justify-center h-[80px] sticky top-0">
            <div className="flex items-center justify-between max-w-[1000px] w-[90%]">
                <img height={65} width={65} src="./icon.png" alt="Icon" />
                <nav className="flex items-center justify-center gap-[10px]">
                    <a className="flex items-center justify-center font-semibold px-[15px] h-[35px] rounded-[8px] text-[16px] hover:bg-[#2c2c2c93] transition-[0.2s] cursor-pointer">Ínicio</a>
                    <a className="flex items-center justify-center font-semibold px-[15px] h-[35px] rounded-[8px] text-[16px] hover:bg-[#2c2c2c93] transition-[0.2s] cursor-pointer">Sobre nós</a>
                    <a className="flex items-center justify-center font-semibold px-[15px] h-[35px] rounded-[8px] text-[16px] hover:bg-[#2c2c2c93] transition-[0.2s] cursor-pointer">GurAi</a>
                </nav>
                <div className="flex items-center justify-center flex-row gap-[10px]">
                    <button className="font-bold px-[15px] h-[35px] bg-[white] text-[16px] transition-[0.2s] hover:bg-[#bebebe] rounded-[8px] text-[black] cursor-pointer">Entrar</button>
                    <button className="flex items-center justify-center border border-[#757575] rounded-[8px] bg-transparent h-[35px] w-[35px]"><TbSunHighFilled color="#757575" /></button>
                </div>
            </div>
        </header>
    )
}