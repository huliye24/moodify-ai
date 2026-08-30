import Link from "next/link";
import "./token.css";

export default function TokenPage() {
  return <main className="token-site">
    <nav className="token-nav" aria-label="MOOD 主导航"><Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link><div className="token-nav-links"><a href="#world">我们的世界</a><a href="#belief">我们的信念</a><a href="#arrival">MOOD Token</a><Link href="/">Moodify Music</Link></div><span className="token-nav-state">COMING SOON</span></nav>

    <header className="token-hero"><div className="token-hero-copy"><p className="token-kicker">A DIGITAL HOME FOR FREE SPIRITS</p><h1>在这里，<br /><em>成为你自己。</em></h1><p className="token-lead">MOOD 是一个属于自由意志、独立选择与美的数字家园。没有被规定的人生，只有你愿意生活的方式。</p><div className="token-actions"><a className="token-primary" href="#world">进入这个世界</a><a className="token-secondary" href="#belief">阅读我们的信念</a></div></div><div className="token-hero-mark" aria-hidden="true"><img src="/moodify-brand-logo.png" alt="" /></div></header>

    <figure id="world" className="token-world-image"><img src="/mood-world-hero.png" alt="人们在开放的未来音乐空间相遇、聆听与创作" /></figure>

    <section id="belief" className="token-statement"><div><p className="token-kicker">THE MOOD MANIFESTO</p><h2>世界不只需要<br />宏大的使命。</h2></div><div><p>我们相信，人不是为了成为工具而活。闲暇不是浪费，远行不必抵达，艺术也不需要证明价值。你可以思考，可以创造，可以相爱，也可以只是坐在阳光下。</p><p>选择自己的节奏，建立真实的关系，保留感受美的能力——这本身就是一种完整的人生。</p></div></section>

    <section className="token-chapters">
      <article><img src="/mood-cafe.png" alt="山景中的开放咖啡馆与图书空间" /><div><span>01 · THE CAFÉ</span><h3>思想在咖啡馆相遇。</h3><p>有人交谈，有人阅读，有人独处。我们因不同而靠近，也保留不被说服的权利。</p></div></article>
      <article><img src="/mood-road.png" alt="人们沿海岸道路自由旅行与创作" /><div><span>02 · ON THE ROAD</span><h3>路不一定通向目的地。</h3><p>慢下来，转身，停留，重新出发——人生属于选择它的人。</p></div></article>
      <article><img src="/mood-leisure.png" alt="夜色水上花园中的休息与创作" /><div><span>03 · IN PRAISE OF IDLENESS</span><h3>闲暇让灵魂重新生长。</h3><p>看星星、种花、跳舞，或和喜欢的人消磨一个夜晚。生活的美不需要效率来批准。</p></div></article>
    </section>

    <section className="token-principles" aria-label="MOOD 的信念"><article><span>01</span><h3>独立意志</h3><p>没有人替你定义完整的人生。选择权始终属于你。</p></article><article><span>02</span><h3>自由连接</h3><p>关系源于自愿，而不是许可。世界因真实的连接而存在。</p></article><article><span>03</span><h3>生活之美</h3><p>美不是附加项。它是我们愿意生活、创造和留下的理由。</p></article></section>

    <section id="arrival" className="token-arrival"><p className="token-kicker">MOOD TOKEN · COMING SOON</p><h2>先让世界发生。</h2><p>MOOD Token 将成为这个世界里的经济媒介。目前正在香港为 BNB Smart Chain 发行做准备，尚未开放购买，也没有官方合约地址。</p><small>正式发布时，唯一可信的合约地址与验证入口会首先出现在本页。</small></section>

    <footer className="token-footer"><Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link><p>Every voice deserves to be heard.</p><div><Link href="/">Moodify Music</Link><a href="#belief">Manifesto</a></div></footer>
  </main>;
}
