
import {
  useEffect,
  useRef,
  useState,
  type SubmitEvent,
} from "react";

import {
  MessageCircle,
  LineChart,
  Plus,
  PanelLeftIcon,
  BatteryCharging,
  History,
  X,
} from "lucide-react";

import Header from "@/components/Header";
import { AppSidebar } from "@/components/SidebarDashboard";

import {
  useSidebar,
  SidebarProvider,
} from "@/components/ui/sidebar";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import WalletPage from "@/components/WalletComponent";
import MonitoringPage from "@/components/MonitoringPage";
import { useRouter } from "next/router";

type DashboardPage = "monitoramento" | "chat";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type ChatConversation = {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: number;
};

export default function Dashboard() {
  const router = useRouter();

  const [page, setPage] =
    useState<DashboardPage>("monitoramento");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState("");

  const conversationId = useRef("");

  const [conversations, setConversations] =
    useState<ChatConversation[]>([]);

  const [activeConversationId, setActiveConversationId] = useState("");

  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyPopupOpen, setHistoryPopupOpen] = useState(false);




  // Busca apenas conversas, não perguntas individuais.
  async function refreshConversations() {
    try {
      const response = await fetch("/api/chat", {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Não foi possível carregar as conversas.");
      }

      const data = await response.json();

      setConversations(
        Array.isArray(data.conversations)
          ? data.conversations
          : []
      );
    } catch (error) {
      console.error(
        "Erro ao atualizar as conversas do GurAI:",
        error
      );
    }
  }

  // Recupera a conversa ativa e a lista de conversas.
  useEffect(() => {
    let cancelled = false;

    async function loadInitialChat() {
      const savedId = window.localStorage.getItem(
        "gurai-active-conversation"
      );

      const id =
        savedId && /^[a-zA-Z0-9_-]{1,100}$/.test(savedId)
          ? savedId
          : crypto.randomUUID();

      conversationId.current = id;

      setActiveConversationId(id);

      window.localStorage.setItem(
        "gurai-active-conversation",
        id
      );

      setLoadingHistory(true);
      setChatError("");

      try {
        const [historyResponse, conversationsResponse] =
          await Promise.all([
            fetch(
              `/api/chat?conversationId=${encodeURIComponent(id)}`
            ),
            fetch("/api/chat"),
          ]);

        const [historyData, conversationsData] =
          await Promise.all([
            historyResponse.json(),
            conversationsResponse.json(),
          ]);

        if (!historyResponse.ok) {
          throw new Error(
            historyData.error ||
            "Não foi possível recuperar a conversa."
          );
        }

        if (!cancelled) {
          setMessages(
            Array.isArray(historyData.messages)
              ? historyData.messages
              : []
          );

          setConversations(
            conversationsResponse.ok &&
              Array.isArray(conversationsData.conversations)
              ? conversationsData.conversations
              : []
          );
        }
      } catch (error) {
        if (!cancelled) {
          setChatError(
            error instanceof Error
              ? error.message
              : "Erro ao recuperar a conversa."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingHistory(false);
        }
      }
    }

    void loadInitialChat();

    return () => {
      cancelled = true;
    };
  }, []);

  // Envia uma mensagem ao backend do GurAI.
  async function handleSend(
    event: SubmitEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const message = draft.trim();

    if (!message || sending || loadingHistory) {
      return;
    }

    if (!conversationId.current) {
      const id = crypto.randomUUID();

      conversationId.current = id;

      window.localStorage.setItem(
        "gurai-active-conversation",
        id
      );
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    setDraft("");
    setChatError("");
    setSending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          conversationId: conversationId.current,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
          "Não foi possível obter uma resposta do GurAI."
        );
      }

      if (typeof data.response !== "string") {
        throw new Error(
          "O backend retornou uma resposta inválida."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

      // Atualiza a lista de conversas depois da resposta.
      await refreshConversations();
    } catch (error) {
      setChatError(
        error instanceof Error
          ? error.message
          : "Erro ao conectar com o GurAI."
      );
    } finally {
      setSending(false);
    }
  }

  // Cria uma conversa nova. Ela será salva quando a primeira
  // mensagem for enviada.
  function startNewConversation() {
    if (sending) return;

    const id = crypto.randomUUID();

    conversationId.current = id;

    window.localStorage.setItem(
      "gurai-active-conversation",
      id
    );

    setActiveConversationId(id);
    setMessages([]);
    setDraft("");
    setChatError("");
    setLoadingHistory(false);
    setHistoryPopupOpen(false);
    setPage("chat");
  }

  // Abre uma conversa selecionada no popup.
  async function openConversation(id: string) {
    if (sending || loadingHistory) {
      return;
    }

    conversationId.current = id;

    window.localStorage.setItem(
      "gurai-active-conversation",
      id
    );
    setActiveConversationId(id);
    setMessages([]);
    setDraft("");
    setChatError("");
    setHistoryPopupOpen(false);
    setLoadingHistory(true);
    setPage("chat");

    try {
      const response = await fetch(
        `/api/chat?conversationId=${encodeURIComponent(id)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
          "Não foi possível abrir a conversa."
        );
      }

      setMessages(
        Array.isArray(data.messages)
          ? data.messages
          : []
      );

      await refreshConversations();
    } catch (error) {
      setChatError(
        error instanceof Error
          ? error.message
          : "Erro ao abrir a conversa."
      );
    } finally {
      setLoadingHistory(false);
    }
  }

  return (
    <SidebarProvider>
      <TooltipProvider>
        <div className="flex h-screen w-full overflow-hidden">
          <AppSidebar
            onOpenConversation={(id) => {
              void openConversation(id);
            }}
          />

          {/* Barra vertical de ícones */}
          <nav className="relative z-30 flex h-screen shrink-0 flex-col items-center justify-start overflow-visible border-r border-[#1f1f1f] p-[10px]">
            <SidebarCollapsedTrigger />
            <ButtonToggleSideBar />

            {/* Monitoramento */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => setPage("monitoramento")}
                aria-label="Voltar ao mapa"
                aria-pressed={page === "monitoramento"}
                title="Voltar ao mapa"
                className={`mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707] ${page === "monitoramento"
                  ? "bg-[#1f1f1f]"
                  : "bg-transparent"
                  }`}
              >
                <LineChart size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Monitoramento
              </TooltipContent>
            </Tooltip>

            {/* Abrir GurAI */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() => setPage("chat")}
                aria-label="Abrir GurAI"
                aria-pressed={page === "chat"}
                title="GurAI"
                className={`mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f] transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707] ${page === "chat"
                  ? "bg-[#1f1f1f]"
                  : "bg-transparent"
                  }`}
              >
                <MessageCircle size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                GurAI
              </TooltipContent>
            </Tooltip>

            {/* Carteira */}
            <div className="mb-[8px]">
              <WalletPage />
            </div>

            {/* Registrar carregamento */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={() =>
                  void router.push("/charging-sessions")
                }
                aria-label="Registrar carregamento"
                title="Registrar carregamento"
                className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
              >
                <BatteryCharging size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Adicionar sessão de carregamento
              </TooltipContent>
            </Tooltip>

            {/* Nova conversa */}
            <Tooltip>
              <TooltipTrigger
                type="button"
                onClick={startNewConversation}
                title="Nova conversa"
                aria-label="Nova conversa"
                className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
              >
                <Plus size={16} />
              </TooltipTrigger>

              <TooltipContent side="right">
                Nova conversa
              </TooltipContent>
            </Tooltip>

            {/* Popup de conversas recentes */}
            <div className="relative">
              <Tooltip>
                <TooltipTrigger
                  type="button"
                  aria-label="Abrir conversas recentes"
                  aria-expanded={historyPopupOpen}
                  title="Conversas recentes"
                  onClick={() =>
                    setHistoryPopupOpen((open) => !open)
                  }
                  className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
                >
                  <History size={16} />
                </TooltipTrigger>

                <TooltipContent side="right">
                  Conversas recentes
                </TooltipContent>
              </Tooltip>

              {historyPopupOpen && (
                <div className="absolute left-[45px] top-0 z-[1200] flex max-h-[calc(100vh-24px)] w-[300px] flex-col overflow-y-auto rounded-xl border border-border bg-card p-3 text-card-foreground shadow-xl">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h2 className="text-sm font-semibold">
                      Conversas recentes
                    </h2>

                    <button
                      type="button"
                      aria-label="Fechar conversas recentes"
                      onClick={() =>
                        setHistoryPopupOpen(false)
                      }
                      className="rounded-md p-1 transition-colors hover:bg-muted"
                    >
                      <X size={16} />
                    </button>
                  </div>

                  {/* Uma entrada por conversa; o título é a primeira mensagem. */}
                  <div className="flex flex-col gap-1">
                    {conversations.map((conversation) => (
                      <button
                        key={conversation.id}
                        type="button"
                        disabled={sending || loadingHistory}
                        onClick={() => {
                          void openConversation(conversation.id);
                        }}
                        title={conversation.title}
                        className={`w-full rounded-lg border px-3 py-3 text-left text-sm transition-colors hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707] disabled:cursor-not-allowed disabled:opacity-50 ${activeConversationId === conversation.id
                          ? "border-border bg-background"
                          : "border-transparent"
                          }`}
                      >
                        <span className="block break-words">
                          {conversation.title || "Nova conversa"}
                        </span>
                      </button>
                    ))}

                    {conversations.length === 0 && (
                      <p className="px-2 py-4 text-center text-xs text-muted-foreground">
                        Nenhuma conversa salva ainda.
                      </p>
                    )}
                  </div>

                  <div className="my-3 border-t border-border" />

                  <button
                    type="button"
                    onClick={startNewConversation}
                    disabled={sending}
                    className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#f0d941] px-3 py-2 text-sm font-medium text-[#070707] transition-colors duration-200 hover:bg-[#d8c331] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Plus size={15} />
                    Nova conversa
                  </button>
                </div>
              )}
            </div>
          </nav>

          {/* Conteúdo principal */}
          <div className="flex h-screen min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
            <div className="flex h-[50px] shrink-0 items-center justify-between gap-3 border-b border-border px-3">
              <div className="min-w-0">
                <h1 className="text-sm font-medium">
                  {page === "monitoramento"
                    ? "Monitoramento"
                    : "GurAI"}
                </h1>

                {page === "chat" && (
                  <p className="text-xs text-muted-foreground">
                    Assistente virtual
                  </p>
                )}
              </div>

              <Header variant="dashboard" />
            </div>

            {page === "monitoramento" ? (
              <div className="min-h-0 min-w-0 flex-1">
                <MonitoringPage
                  onOpenChat={() => setPage("chat")}
                />
              </div>
            ) : (
              <main className="flex min-h-0 min-w-0 flex-1 flex-col p-4 sm:p-6">
                <div className="mx-auto flex min-h-0 w-full max-w-4xl flex-1 flex-col">
                  <section className="flex min-h-0 flex-1 flex-col">
                    {/* Mensagens */}
                    <div className="min-h-0 flex-1 overflow-y-auto py-2">
                      {loadingHistory ? (
                        <div className="flex h-full items-center justify-center">
                          <p className="text-sm text-muted-foreground">
                            Carregando conversa...
                          </p>
                        </div>
                      ) : messages.length === 0 ? (
                        <div className="flex h-full flex-col items-center justify-center text-center">
                          <MessageCircle
                            size={36}
                            className="mb-3 text-muted-foreground"
                          />

                          <h2 className="text-xl font-semibold">
                            Como posso ajudar?
                          </h2>

                          <p className="mt-2 text-sm text-muted-foreground">
                            Converse com o GurAI sobre seus carregadores e sua plataforma.
                          </p>
                        </div>
                      ) : (
                        <div className="flex flex-col gap-4">
                          {messages.map((message, index) => (
                            <div
                              key={`${index}-${message.role}`}
                              className={`max-w-[85%] whitespace-pre-wrap break-words rounded-xl px-4 py-3 text-sm ${message.role === "user"
                                ? "self-end bg-[#f0d941] text-[#070707]"
                                : "self-start border border-border bg-card text-card-foreground"
                                }`}
                            >
                              {message.content}
                            </div>
                          ))}

                          {sending && (
                            <p className="text-sm text-muted-foreground">
                              GurAI está pensando...
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    {chatError && (
                      <p
                        role="alert"
                        className="mb-2 text-sm text-red-500"
                      >
                        {chatError}
                      </p>
                    )}

                    {/* Campo de mensagem */}
                    <form
                      onSubmit={handleSend}
                      className="flex shrink-0 gap-2 border-t border-border pt-4"
                    >
                      <input
                        type="text"
                        value={draft}
                        onChange={(event) =>
                          setDraft(event.target.value)
                        }
                        placeholder="Digite sua mensagem..."
                        aria-label="Mensagem para o GurAI"
                        maxLength={4000}
                        disabled={sending || loadingHistory}
                        className="min-w-0 flex-1 rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground outline-none focus:border-[#f0d941] disabled:cursor-not-allowed disabled:opacity-60"
                      />

                      <button
                        type="submit"
                        disabled={
                          sending ||
                          loadingHistory ||
                          !draft.trim()
                        }
                        className="rounded-lg bg-[#f0d941] px-5 py-3 text-sm font-medium text-[#070707] transition-colors hover:bg-[#d8c331] disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {sending ? "Enviando..." : "Enviar"}
                      </button>
                    </form>
                  </section>
                </div>
              </main>
            )}
          </div>
        </div>
      </TooltipProvider>
    </SidebarProvider>
  );
}

function ButtonToggleSideBar() {
  const { toggleSidebar } = useSidebar();

  return (
    <button
      type="button"
      onClick={toggleSidebar}
      aria-label="Expandir ou recolher a barra lateral"
      title="Expandir ou recolher a barra lateral"
      className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-border text-foreground transition-colors duration-200 hover:border-[#f0d941] hover:bg-[#f0d941] hover:text-[#070707]"
    >
      <PanelLeftIcon size={16} />
    </button>
  );
}

function SidebarCollapsedTrigger() {
  const { state } = useSidebar();

  if (state !== "collapsed") return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <button
            type="button"
            aria-label="Abrir menu do usuário"
            title="Menu do usuário"
            className="mb-[8px] flex h-[35px] w-[35px] cursor-pointer items-center justify-center rounded-[8px] border border-[#1f1f1f]"
          >
            <img
              height={35}
              width={35}
              src="/imageuser.jpg"
              alt=""
              className="rounded-[8px]"
            />
          </button>
        }
      />

      <DropdownMenuContent
        className="w-60 rounded-[8px] bg-[#0a0a0a]"
        align="start"
      >
        <DropdownMenuGroup>
          <DropdownMenuLabel>Usuário</DropdownMenuLabel>

          <DropdownMenuItem className="cursor-pointer">
            Perfil
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Configurações
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Ajuda
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
            Adicionar veículo
          </DropdownMenuItem>
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuItem className="cursor-pointer">
            Sair
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
