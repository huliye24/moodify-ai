import type { Metadata } from "next";
import "./globals.css";
import SwRegister from "./sw-register";

export const metadata: Metadata = {
  title: "Moodify Player — Better Sound Experience",
  description: "Minimal music player. Just press Play.",
  icons: { icon: "/moodify-logo.png", apple: "/moodify-logo.png" },
  manifest: "/manifest.webmanifest",
  alternates: { canonical: "https://play.rongjingmusic.com/" },
  openGraph: {
    title: "Moodify Player — Better Sound Experience",
    description: "Minimal music player. Just press Play.",
    url: "https://play.rongjingmusic.com/",
    siteName: "Moodify Player",
    locale: "zh_CN",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Moodify Player — Better Sound Experience",
    description: "Minimal music player. Just press Play.",
  },
  other: { "codex-preview": "development" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <meta name="theme-color" content="#05081e" />
        <link rel="manifest" href="/manifest.webmanifest" />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "Moodify Player",
          "description": "Minimal music player",
          "url": "https://play.rongjingmusic.com/",
          "applicationCategory": "MusicApplication",
          "operatingSystem": "Any",
          "offers": { "@type": "Offer", "price": "0", "priceCurrency": "CNY" },
          "isPartOf": {
            "@type": "Product",
            "name": "Moodify",
            "url": "https://rongjingmusic.com/"
          }
        })}} />
      </head>
      <body>
        <SwRegister />
        {children}
      </body>
    </html>
  );
}
