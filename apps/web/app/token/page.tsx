import Link from "next/link";
import "./token.css";
import "./architecture.css";

export default function TokenPage() {
  return <main className="token-site">
    <nav className="token-nav" aria-label="MOOD 主导航"><Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link><div className="token-nav-links"><a href="#world">World</a><Link href="/protocol">Protocol</Link><Link href="/portal">Portal</Link><Link href="/network">Network</Link><Link href="/library">Library</Link></div><a className="token-nav-state" href="#entrances">ENTER MOOD</a></nav>

    <header className="token-hero"><div className="token-hero-copy"><p className="token-kicker">A DIGITAL HOME FOR FREE SPIRITS</p><h1>在这里，<br /><em>成为你自己。</em></h1><p className="token-lead">MOOD 是一个属于自由意志、独立选择与美的数字家园。没有被规定的人生，只有你愿意生活的方式。</p><div className="token-actions"><a className="token-primary" href="#world">进入这个世界</a><a className="token-secondary" href="#belief">阅读我们的信念</a></div></div><div className="token-hero-mark" aria-hidden="true"><img src="/moodify-brand-logo.png" alt="" /></div></header>

    <figure id="world" className="token-world-image"><img src="/mood-world-hero.png" alt="人们在开放的未来音乐空间相遇、聆听与创作" /></figure>

    <section id="entrances" className="token-architecture">
      <div className="token-primary-gates">
        <Link href="/world"><span>01</span><small>EXPERIENCE</small><h3>WORLD</h3><p>感受 MOOD 的信念、文化、空间与共同生活的想象。</p><b>进入世界 →</b></Link>
        <Link href="/protocol"><span>02</span><small>RULES</small><h3>PROTOCOL</h3><p>阅读贡献、Proof、Agents、Nodes 与治理如何共同运行。</p><b>阅读协议 →</b></Link>
        <Link href="/portal"><span>03</span><small>PARTICIPATION</small><h3>PORTAL</h3><p>从 Visitor 成为 Resident，建立 Passport 并开始参与。</p><b>进入门户 →</b></Link>
      </div>
      <div className="token-places">
        <Link href="/library"><strong>Library</strong><span>白皮书、文化与公共知识</span></Link><Link href="/build"><strong>Builder Workshop</strong><span>建设者与开放工具</span></Link><Link href="/agents"><strong>Agent Lab</strong><span>真实工作的 AI Agents</span></Link><Link href="/nodes"><strong>Node Station</strong><span>真实网络资源与服务</span></Link><Link href="/governance"><strong>Governance</strong><span>MIP 与共同决策</span></Link><Link href="/"><strong>Moodify Gate</strong><span>第一个 Genesis Application</span></Link>
      </div>
    </section>

    <section id="belief" className="token-statement"><div><p className="token-kicker">THE MOOD MANIFESTO</p><h2>世界不只需要<br />宏大的使命。</h2></div><div><p>我们相信，人不是为了成为工具而活。闲暇不是浪费，远行不必抵达，艺术也不需要证明价值。你可以思考，可以创造，可以相爱，也可以只是坐在阳光下。</p><p>选择自己的节奏，建立真实的关系，保留感受美的能力——这本身就是一种完整的人生。</p></div></section>

    <section className="token-chapters">
      <article><img src="/mood-cafe.png" alt="山景中的开放咖啡馆与图书空间" /><div><span>01 · THE CAFÉ</span><h3>思想在咖啡馆相遇。</h3><p>有人交谈，有人阅读，有人独处。我们因不同而靠近，也保留不被说服的权利。</p></div></article>
      <article><img src="/mood-road.png" alt="人们沿海岸道路自由旅行与创作" /><div><span>02 · ON THE ROAD</span><h3>路不一定通向目的地。</h3><p>慢下来，转身，停留，重新出发——人生属于选择它的人。</p></div></article>
      <article><img src="/mood-leisure.png" alt="夜色水上花园中的休息与创作" /><div><span>03 · IN PRAISE OF IDLENESS</span><h3>闲暇让灵魂重新生长。</h3><p>看星星、种花、跳舞，或和喜欢的人消磨一个夜晚。生活的美不需要效率来批准。</p></div></article>
    </section>

    <section className="token-principles" aria-label="MOOD 的信念"><article><span>01</span><h3>独立意志</h3><p>没有人替你定义完整的人生。选择权始终属于你。</p></article><article><span>02</span><h3>自由连接</h3><p>关系源于自愿，而不是许可。世界因真实的连接而存在。</p></article><article><span>03</span><h3>生活之美</h3><p>美不是附加项。它是我们愿意生活、创造和留下的理由。</p></article></section>

    <footer className="token-footer"><Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link><p>MOOD is the world. Moodify is only the beginning.</p><div><Link href="/library">Library</Link><Link href="/network">Network</Link><Link href="/">Moodify Gate</Link></div></footer>
  </main>;
}
