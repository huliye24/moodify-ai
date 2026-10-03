"use client";
import Link from "next/link";
import { useState } from "react";
import { MOOD_TOKEN } from "../../lib/mood-token";
import WalletConnect from "./WalletConnect";

function CopyAddress() {
  const [copied, setCopied] = useState(false);
  async function copy() { try { await navigator.clipboard.writeText(MOOD_TOKEN.address); setCopied(true); window.setTimeout(() => setCopied(false), 1800); } catch { setCopied(false); } }
  return <button className="mood-copy" onClick={copy}>{copied ? "已复制 ✓" : "复制地址"}</button>;
}

export default function TokenPage() {
  return <main className="mood-site">
    <nav className="mood-nav" aria-label="主导航">
      <Link className="mood-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link>
      <div className="mood-nav-links"><a href="#world">我们的世界</a><a href="#story">我们的信念</a><a href="#home">世界地图</a><a href={MOOD_TOKEN.officialSite} target="_blank" rel="noreferrer">Moodify Music ↗</a></div>
      <a className="mood-nav-action" href="#world">ENTER</a>
    </nav>

    <header className="mood-hero">
      <div className="mood-hero-copy"><span className="mood-kicker">MOOD · A DIGITAL HOME FOR FREE SPIRITS</span><h1><span>BE YOURSELF.</span><small>在这里，成为你自己。</small></h1><p>MOOD 是一个属于自由意志、独立选择与美的数字家园。没有规定的人生，只有你愿意生活的方式。</p><div className="mood-actions"><a className="mood-primary" href="#world">进入 MOOD <span aria-hidden="true">→</span></a><a className="mood-secondary" href="#story">阅读我们的信念</a></div></div>
      <div className="mood-hero-mark" aria-hidden="true"><span className="mood-orbit mood-orbit-one" /><span className="mood-orbit mood-orbit-two" /><img src="/moodify-brand-logo.png" alt="" /><small>ENTER THE WORLD</small></div>
    </header>

    <section id="world" className="mood-world-gate"><div className="mood-world-intro"><span className="mood-kicker">ENTER THE WORLD</span><h2>一个入口，<br />通向许多种生活。</h2><p>MOOD 不是一张功能清单。它是一座逐渐生长的数字世界；你可以选择自己的方向，也可以只是停留。</p></div><nav className="mood-world-map" aria-label="MOOD 世界地图"><a href="#cafe"><span>01</span><strong>咖啡馆</strong><small>思想与不同的人相遇</small></a><a href="#road"><span>02</span><strong>在路上</strong><small>选择自己的方向</small></a><a href="#leisure"><span>03</span><strong>闲暇之地</strong><small>让生活重新生长</small></a><a href={MOOD_TOKEN.officialSite} target="_blank" rel="noreferrer"><span>04</span><strong>Moodify Music</strong><small>从音乐进入这个世界 ↗</small></a></nav></section>

    <figure className="mood-world"><img src="/mood-world-hero.png" alt="人们在开放的未来音乐空间里围绕紫蓝色波形相遇、聆听与创作" /><figcaption>MOOD WORLD · A PLACE WITHOUT A PRESCRIBED LIFE</figcaption></figure>

    <section id="story" className="mood-story"><div><span className="mood-kicker">THE MOOD MANIFESTO</span><h2>世界不只需要<br />宏大的使命。</h2></div><div className="mood-story-copy"><p>我们相信，人不是为了成为工具而活。闲暇不是浪费，远行不必抵达，艺术也不需要证明价值。你可以思考，可以创造，可以相爱，也可以只是坐在阳光下。</p><p>MOOD 尊重每个人的独立意志。选择自己的节奏，建立真实的关系，保留感受美的能力——这本身就是一种完整的人生。</p></div></section>

    <section id="home" className="mood-chapters">
      <article id="cafe" className="mood-chapter"><div className="mood-chapter-copy"><span>01 · THE CAFÉ</span><h2>思想在咖啡馆相遇。</h2><p>没有标准答案，也没有被安排好的立场。有人交谈，有人阅读，有人独处。我们因不同而靠近，也保留不被说服的权利。</p></div><figure><img src="/mood-cafe.png" alt="开放山景中的咖啡馆与图书空间，人们阅读、交谈、写作和演奏音乐" /></figure></article>
      <article id="road" className="mood-chapter mood-chapter-reverse"><div className="mood-chapter-copy"><span>02 · ON THE ROAD</span><h2>路不一定通向目的地。</h2><p>自由不是拥有更多选项，而是能够决定什么值得追寻。慢下来，转身，停留，重新出发——人生属于选择它的人。</p></div><figure><img src="/mood-road.png" alt="人们沿着海岸道路自由旅行、绘画、游泳、阅读和演奏" /></figure></article>
      <article id="leisure" className="mood-chapter mood-chapter-night"><div className="mood-chapter-copy"><span>03 · IN PRAISE OF IDLENESS</span><h2>闲暇让灵魂重新生长。</h2><p>创造并不只发生在工作里。看星星、种花、跳舞、做一顿饭，或和喜欢的人消磨一个夜晚——生活的美不需要效率来批准。</p></div><figure><img src="/mood-leisure.png" alt="夜色中的水上花园，人们休息、创作、观星、共餐和跳舞" /></figure></article>
    </section>

    <section className="mood-principles" aria-label="MOOD 的信念"><article><span>01</span><h3>独立意志</h3><p>没有人替你定义完整的人生。选择权始终属于你。</p></article><article><span>02</span><h3>自由连接</h3><p>关系源于自愿，而不是许可。世界因真实的连接而存在。</p></article><article><span>03</span><h3>生活之美</h3><p>美不是附加项。它是我们愿意生活、创造和留下的理由。</p></article></section>

    <section id="use" className="mood-use"><div className="mood-use-intro"><span className="mood-kicker">COME AS YOU ARE</span><h2>这里就是入口。</h2><p>钱包不是身份的全部，只是你进入 MOOD 数字家园的一把钥匙。Moodify 是其中一扇门，音乐让我们最先相遇。</p><div className="mood-mini-facts"><span>BNB Smart Chain</span><span>33,000,000 MOOD</span><a href={MOOD_TOKEN.officialSite} target="_blank" rel="noreferrer">Moodify Music ↗</a></div></div><div className="mood-wallet-shell"><WalletConnect /></div></section>

    <section id="contract" className="mood-contract"><div><span className="mood-kicker">OFFICIAL CONTRACT</span><h2>只认这一个地址。</h2><p>交易或添加代币前，请核对完整合约地址。</p></div><div className="mood-address"><code>{MOOD_TOKEN.address}</code><CopyAddress /><a href={MOOD_TOKEN.explorerUrl} target="_blank" rel="noreferrer">验证合约 ↗</a></div></section>

    <footer className="mood-footer"><Link className="mood-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link><p>Every voice deserves to be heard.</p><div><a href={MOOD_TOKEN.tradeUrl} target="_blank" rel="noreferrer">PancakeSwap ↗</a><a href={MOOD_TOKEN.officialSite} target="_blank" rel="noreferrer">Moodify ↗</a></div></footer>
  </main>;
}
