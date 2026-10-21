interface ContainerChatProps {
    content: string
}

export default function ContainerChat({ content }: ContainerChatProps) {
    return(
        <article className="rounded-[8px] text-[13px] px-[14px] py-[6px] hover:bg-[#3d3d3d77] cursor-pointer transition-[0.2s] w-full mb-[5px]">
            {content}
        </article>
    )
}