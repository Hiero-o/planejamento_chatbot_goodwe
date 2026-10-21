interface ItemNavProps {
    label: string
}

export default function ItemNav({ label }: ItemNavProps) {
    return(
        <p className="py-[5px] px-[12px] text-[13px] font-medium text-[#b3b3b3] cursor-pointer rounded-[8px] transition-[0.2s] hover:bg-[#181818] hover:text-[#fff]">{label}</p>
    )
}