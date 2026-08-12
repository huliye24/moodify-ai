import type { Metadata } from "next";
import "./globals.css";
export const metadata:Metadata={title:"Moodify Music",description:"听见此刻与你更接近的音乐。",icons:{icon:"/moodify-logo.png"},other:{"codex-preview":"development"}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="zh-CN"><body>{children}</body></html>}
