import Link from "next/link";
import ItemNav from "./ItemNav";

type HeaderProps = {
  variant?: "landing" | "dashboard";
};

export default function Header({
  variant = "landing",
}: HeaderProps) {
  const isDashboard = variant === "dashboard";

  return (
    <header
      className={
        isDashboard
          ? "flex h-full w-auto shrink-0 items-center justify-end text-foreground"
          : "sticky top-0 z-40 flex h-[80px] w-full items-center justify-center border-b border-border bg-background/80 text-foreground backdrop-blur-md transition-colors duration-200"
      }
    >
      <div
        className={
          isDashboard
            ? "flex items-center justify-end"
            : "flex w-[90%] max-w-[1000px] items-center justify-between"
        }
      >
        {!isDashboard && (
          <Link
            href="/"
            aria-label="GurAI - Página inicial"
            className="flex shrink-0 items-center"
          >
            <img
              src="/icon.png"
              alt="GurAI"
              className="h-[35px] w-[20px] object-contain"
            />
          </Link>
        )}

        <nav
          aria-label="Navegação principal"
          className="
            flex items-center justify-center gap-[5px]
            [&_a]:inline-flex
            [&_a]:h-9
            [&_a]:items-center
            [&_a]:justify-center
            [&_a]:px-[10px]
            [&_a]:text-[14px]
            [&_a]:font-normal
            [&_a]:leading-5
            [&_a]:text-foreground
            [&_a]:no-underline
            [&_a]:transition-colors
            [&_a:hover]:opacity-70
            [&_button]:inline-flex
            [&_button]:h-9
            [&_button]:items-center
            [&_button]:justify-center
            [&_button]:px-[10px]
            [&_button]:text-[14px]
            [&_button]:font-normal
            [&_button]:leading-5
            [&_button]:text-foreground
            [&_button]:transition-colors
            [&_button:hover]:opacity-70
          "
        >
          <ItemNav label="Planos" />

          <Link href="/dashboard">
            Dashboard
          </Link>

          <Link
            href={isDashboard ? "/help?from=/dashboard" : "/help?from=/"}
          >
            Suporte
          </Link>

          {isDashboard && (
            <Link
              href="/"
              className="inline-flex h-9 items-center justify-center rounded-[8px] border border-[#f0d941] bg-[#f0d941] px-[15px] !text-[#070707] text-[14px] font-medium no-underline transition-colors duration-200 hover:border-[#a3921f] hover:bg-[#a3921f]"
            >
              Gurgel Enterprise
            </Link>
          )}
        </nav>

        {!isDashboard && (
          <Link
            href="/auth/login"
            className="inline-flex h-8 items-center justify-center rounded-[8px] bg-[#f0d941] px-[15px] text-[14px] font-medium text-[#070707] no-underline transition-colors duration-200 hover:bg-[#a3921f]"
          >
            Acessar
          </Link>
        )}
      </div>
    </header>
  );
}