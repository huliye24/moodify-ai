import type { Metadata } from "next";
import "./globals.css";
import SwRegister from "./sw-register";

export const metadata: Metadata = {
  title: "Moodify Music",
  description: "听见此刻与你更接近的音乐。",
  icons: { icon: "/moodify-logo.png" },
  manifest: "/manifest.webmanifest",
  other: { "codex-preview": "development" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <meta name="theme-color" content="#05081e" />
        <link rel="manifest" href="/manifest.webmanifest" />
      </head>
      <body>
        <SwRegister />
        {children}
      </body>
    </html>
  );
}
