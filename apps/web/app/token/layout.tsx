export const metadata = {
  title: "MOOD — World · Protocol · Portal",
  description: "进入 MOOD：一个由 WORLD、PROTOCOL 与 PORTAL 共同构成的开放数字世界。Moodify 只是开始。",
  alternates: { canonical: "https://crestwavecoin.com/token" },
  openGraph: {
    title: "MOOD — The World Is Open",
    description: "MOOD is the world. Moodify is only the beginning.",
    url: "https://crestwavecoin.com/token",
    siteName: "MOOD",
    type: "website",
  },
};

export default function TokenLayout({ children }: { children: React.ReactNode }) {
  return children;
}
