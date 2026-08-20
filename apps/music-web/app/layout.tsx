import type { Metadata } from "next";
import "./globals.css";
import SwRegister from "./sw-register";

export const metadata: Metadata = {
  title: "Moodify — Play",
  description: "正在播放。Moodify 让每一种声音都值得被世界听见。",
  icons: { icon: "/moodify-logo.png" },
  manifest: "/manifest.webmanifest",
  alternates: { canonical: "https://play.rongjingmusic.com/" },
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
