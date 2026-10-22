import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useEffect } from "react";
import { Inter } from "next/font/google";
import { Toaster } from "@/components/ui/toast";

const inter = Inter({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
  display: "swap",
});

type Preferences = {
  theme: "dark" | "light";
  fontSize: "small" | "medium" | "large";
};

function applyPreferences(preferences: Preferences) {
  document.documentElement.dataset.theme = preferences.theme;
  document.documentElement.dataset.fontSize = preferences.fontSize;
}

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    function loadPreferences() {
      try {
        const saved = localStorage.getItem("gurai-preferences");

        const preferences: Preferences = saved
          ? { theme: "dark", fontSize: "medium", ...JSON.parse(saved) }
          : { theme: "dark", fontSize: "medium" };

        applyPreferences(preferences);
      } catch (error) {
        console.error("Erro ao carregar preferências:", error);
        applyPreferences({ theme: "dark", fontSize: "medium" });
      }
    }

    loadPreferences();

    window.addEventListener("gurai:preferences-changed", loadPreferences);

    return () => {
      window.removeEventListener(
        "gurai:preferences-changed",
        loadPreferences
      );
    };
  }, []);

  return (
    <main className={inter.className}>
      <Component {...pageProps} />
      <Toaster />
    </main>
  );
}
