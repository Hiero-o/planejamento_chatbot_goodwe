
import { useEffect, useState } from "react";
import { MdOutlineKeyboardArrowDown } from "react-icons/md";

import {
  ChevronDown,
  ChevronRight,
  Clock3,
  MessageCircle,
  History,
  Zap,
  BatteryCharging,
  Battery,
  Gauge,
  Clock,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
} from "@/components/ui/sidebar";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import ContainerMonitoring from "../ContainerMonitoring";
import { signOut } from "next-auth/react";
import { useRouter } from "next/router";

interface DashboardSummary {
  averagePowerKw: number;
  accumulatedEnergyKwh: number;
  totalDurationMinutes: number;
  totalInstalledPowerKw: number;
  occupiedChargers: number;
  availableChargers: number;
}

interface SidebarProfile {
  username: string;
  email: string;
}

interface ChatConversation {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: number;
}

interface RecentQuestion {
  id: string;
  conversationId: string;
  conversationTitle: string;
  question: string;
  createdAtMs: number;
}

interface AppSidebarProps {
  onOpenConversation: (conversationId: string) => void;
}

function formatDuration(totalMinutes: number): string {
  const total = Math.max(0, Math.floor(totalMinutes));
  const hours = Math.floor(total / 60);
  const minutes = total % 60;

  return `${hours}h ${minutes.toString().padStart(2, "0")}min`;
}

export function AppSidebar({
  onOpenConversation,
}: AppSidebarProps) {
  const router = useRouter();

  const [profile, setProfile] = useState<SidebarProfile>({
    username: "",
    email: "",
  });

  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [summaryLoading, setSummaryLoading] = useState(true);

  const [conversations, setConversations] = useState<
    ChatConversation[]
  >([]);

  const [recentQuestions, setRecentQuestions] = useState<
    RecentQuestion[]
  >([]);

  const [chatNavigationLoading, setChatNavigationLoading] =
    useState(true);

  const [historyExpanded, setHistoryExpanded] = useState(true);

  // Carrega o perfil do usuário.
  useEffect(() => {
    let active = true;

    async function loadProfile() {
      try {
        const response = await fetch("/api/profile");

        if (!response.ok) return;

        const data = await response.json();

        if (active) {
          setProfile({
            username: data.username || "",
            email: data.email || "",
          });
        }
      } catch (error) {
        console.error(
          "Erro ao carregar perfil da sidebar:",
          error
        );
      }
    }

    void loadProfile();

    return () => {
      active = false;
    };
  }, []);

  // Carrega os indicadores da dashboard.
  useEffect(() => {
    let active = true;

    async function loadSummary() {
      try {
        const response = await fetch("/api/dashboard/summary");

        if (!response.ok) {
          throw new Error("Falha ao consultar os indicadores.");
        }

        const data =
          (await response.json()) as DashboardSummary;

        if (active) {
          setSummary(data);
        }
      } catch (error) {
        console.error(
          "Erro ao carregar indicadores:",
          error
        );

        if (active) {
          setSummary(null);
        }
      } finally {
        if (active) {
          setSummaryLoading(false);
        }
      }
    }

    void loadSummary();

    return () => {
      active = false;
    };
  }, []);

  // Carrega as conversas e as perguntas recentes do usuário.
  useEffect(() => {
    let active = true;

    async function loadChatNavigation() {
      setChatNavigationLoading(true);

      try {
        const [conversationsResponse, questionsResponse] =
          await Promise.all([
            fetch("/api/chat"),
            fetch("/api/chat?view=questions"),
          ]);

        const [conversationsData, questionsData] =
          await Promise.all([
            conversationsResponse.json(),
            questionsResponse.json(),
          ]);

        if (!active) return;

        if (conversationsResponse.ok) {
          setConversations(
            Array.isArray(conversationsData.conversations)
              ? conversationsData.conversations
              : []
          );
        }

        if (questionsResponse.ok) {
          setRecentQuestions(
            Array.isArray(questionsData.questions)
              ? questionsData.questions
              : []
          );
        }
      } catch (error) {
        console.error(
          "Erro ao carregar o histórico do GurAI:",
          error
        );
      } finally {
        if (active) {
          setChatNavigationLoading(false);
        }
      }
    }

    void loadChatNavigation();

    return () => {
      active = false;
    };
  }, []);

  return (
    <Sidebar>
      <SidebarContent className="mt-0 flex flex-col items-start justify-start bg-[#0a0a0a] p-0">
        {/* Perfil do usuário */}
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <article className="mb-0 flex w-full cursor-pointer items-center justify-between border-b border-[#1f1f1f] p-[12px] transition-colors duration-200 hover:bg-[#3d3d3d77]">
                <div className="flex items-center justify-start">
                  <img
                    className="mr-[8px] rounded-full"
                    height={40}
                    width={40}
                    src="/imageuser.jpg"
                    alt=""
                  />

                  <div className="min-w-0">
                    <h1 className="mb-[3px] text-[15px] leading-tight">
                      {profile.username || "Carregando perfil..."}
                    </h1>

                    <p className="mt-0 text-[11px] leading-tight text-[#b3b3b3]">
                      {profile.email || "Carregando email..."}
                    </p>
                  </div>
                </div>

                <MdOutlineKeyboardArrowDown size={20} />
              </article>
            }
          />

          <DropdownMenuContent
            className="w-60 rounded-[8px] bg-[#0a0a0a]"
            align="center"
          >
            <DropdownMenuGroup>
              <DropdownMenuLabel>Usuário</DropdownMenuLabel>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/profile")}
              >
                Perfil
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/settings")}
              >
                Configurações
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/help")}
              >
                Ajuda e suporte
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/vehicles")}
              >
                Meus veículos
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/vehicles")}
              >
                Adicionar veículo
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => void router.push("/charging-sessions")}
              >
                Registrar carregamento
              </DropdownMenuItem>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() =>
                  void signOut({ callbackUrl: "/auth/login" })
                }
              >
                Sair
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Histórico e últimas perguntas */}
        <div className="w-full border-b border-[#1f1f1f] px-3">          
          <div className="">
            <div className="flex items-center gap-2 py-2 text-sm font-medium text-[#b3b3b3]">
              <Clock3 size={16} />
              <span>Últimas perguntas</span>
            </div>

            <div className="mt-1 flex flex-col gap-1">
              {chatNavigationLoading && recentQuestions.length === 0 && (
                <p className="px-2 py-2 text-xs text-[#888]">
                  Carregando perguntas...
                </p>
              )}

              {!chatNavigationLoading &&
                recentQuestions.length === 0 && (
                  <p className="px-2 py-2 text-xs text-[#888]">
                    Suas perguntas aparecerão aqui.
                  </p>
                )}

              {recentQuestions.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  title={`Abrir conversa: ${item.conversationTitle}`}
                  onClick={() =>
                    onOpenConversation(item.conversationId)
                  }
                  className="flex w-full items-start gap-2 rounded-md px-2 py-2 text-left text-sm text-[#ededed] transition-colors hover:bg-[#f0d941] hover:text-[#070707]"
                >
                  <MessageCircle
                    size={14}
                    className="mt-0.5 shrink-0 opacity-60"
                  />

                  <span className="min-w-0 break-words">
                    {item.question}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Indicadores da dashboard */}
        <div className="flex w-full flex-col items-center justify-center">
          <ContainerMonitoring
            label="Potência média (kW)"
            value={
              summaryLoading
                ? "…"
                : summary
                  ? summary.averagePowerKw.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })
                  : "—"
            }
            icon={<Zap size={20} />}
          />

          <ContainerMonitoring
            label="Carregadores em uso"
            value={
              summaryLoading
                ? "…"
                : summary
                  ? summary.occupiedChargers
                  : "—"
            }
            icon={<BatteryCharging size={20} />}
          />

          <ContainerMonitoring
            label="Carregadores livres"
            value={
              summaryLoading
                ? "…"
                : summary
                  ? summary.availableChargers
                  : "—"
            }
            icon={<Battery size={20} />}
          />

          <ContainerMonitoring
            label="Energia acumulada (kWh)"
            value={
              summaryLoading
                ? "…"
                : summary
                  ? summary.accumulatedEnergyKwh.toLocaleString(
                      "pt-BR",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )
                  : "—"
            }
            icon={<Gauge size={20} />}
          />

          <ContainerMonitoring
            label="Tempo total de uso"
            value={
              summaryLoading
                ? "…"
                : summary
                  ? formatDuration(summary.totalDurationMinutes)
                  : "—"
            }
            icon={<Clock size={20} />}
          />
        </div>
      </SidebarContent>
    </Sidebar>
  );
}
