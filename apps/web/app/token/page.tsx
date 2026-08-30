import Link from "next/link";
import "./token.css";

const facts = [
  ["发行状态", "准备中 · 尚未发行", "hold"],
  ["发行地点", "香港 · 法律与主体审查中", "review"],
  ["目标网络", "BNB Smart Chain · Chain ID 56", "target"],
  ["候选启动路径", "Flap · 最终评估中", "review"],
  ["官方合约地址", "不存在 · 未部署", "hold"],
  ["公开购买", "未开放", "hold"],
] as const;

const gates = [
  { n: "01", title: "范围冻结", state: "已生效", copy: "MOOD v0.1 只服务 WORLD、PROTOCOL、PORTAL 与真实网络闭环。" },
  { n: "02", title: "香港法律与发行主体", state: "审查中", copy: "完成代币属性分类、发行主体、营销对象、AML/KYC 与服务商边界审查。" },
  { n: "03", title: "代币参数冻结", state: "待决定", copy: "总量、分配、锁仓、流动性、税率与治理权限均须形成可审计决议。" },
  { n: "04", title: "合约与权限安全", state: "未开始", copy: "测试网部署、权限清单、多签与密钥保管、源码验证及独立安全复核。" },
  { n: "05", title: "Genesis 真实网络", state: "未满足", copy: "真实 Resident、Node、Agent、Contribution、Proof 与 Reputation 形成最小闭环。" },
  { n: "06", title: "公开 Genesis 决议", state: "未签署", copy: "发布最终参数、风险披露、验证链接与签署后的 Genesis Release。" },
] as const;

export default function TokenPage() {
  return (
    <main className="token-site">
      <nav className="token-nav" aria-label="MOOD 主导航">
        <Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link>
        <div className="token-nav-links"><a href="#world">World</a><Link href="/protocol">Protocol</Link><a href="#readiness">Preparation</a><Link href="/">Moodify</Link></div>
        <span className="token-nav-state">NOT YET ISSUED</span>
      </nav>

      <header className="token-hero">
        <div className="token-hero-copy">
          <p className="token-kicker">HONG KONG ISSUANCE PREPARATION · BNB SMART CHAIN</p>
          <h1>先让世界成立，<br /><em>再让经济进入。</em></h1>
          <p className="token-lead">MOOD Token 是 MOOD World 未来的经济媒介，不是项目本身。当前阶段只做发行准备、网络验证与公开披露；没有官方合约地址，也没有开放购买。</p>
          <div className="token-actions"><a className="token-primary" href="#status">查看准备状态</a><Link className="token-secondary" href="/library">阅读 Protocol</Link></div>
        </div>
        <aside className="token-hero-status" aria-label="当前发行状态">
          <span>VERIFIED PUBLIC STATE</span><strong>PREPARATION</strong><p>Hong Kong · 2026</p>
          <div><i /> No contract deployed</div><div><i /> No public sale</div><div><i /> No wallet connection required</div>
        </aside>
      </header>

      <figure className="token-world-image"><img src="/mood-world-hero.png" alt="人们在开放的未来音乐空间相遇、聆听与创作" /></figure>

      <section id="world" className="token-statement">
        <div><p className="token-kicker">WORLD BEFORE TOKEN</p><h2>MOOD 不是一枚等待叙事的币。</h2></div>
        <div><p>MOOD 是 <strong>WORLD + PROTOCOL + PORTAL</strong>。Moodify 是第一个 Genesis Application。只有真实参与、Contribution、Proof 与 Reputation 已经存在，Token 才能成为这个世界内部的经济媒介。</p><p>规则先于口号，真实数据先于宏大数字，贡献先于奖励。</p></div>
      </section>

      <section id="status" className="token-status-section">
        <header><p className="token-kicker">CURRENT VERIFIED STATE</p><h2>现在可以确认什么</h2><p>未冻结的参数不以营销数字替代；未部署的合约不显示地址。</p></header>
        <div className="token-facts">{facts.map(([label, value, tone]) => <article key={label}><span>{label}</span><strong>{value}</strong><i className={`tone-${tone}`} /></article>)}</div>
      </section>

      <section id="readiness" className="token-readiness">
        <header><p className="token-kicker">PUBLIC GENESIS GATES</p><h2>发行不是日期，<br />而是一组必须通过的门槛。</h2></header>
        <div>{gates.map((gate) => <article key={gate.n}><span>{gate.n}</span><div><small>{gate.state}</small><h3>{gate.title}</h3><p>{gate.copy}</p></div></article>)}</div>
      </section>

      <section className="token-safety">
        <div><p className="token-kicker">ANTI-SCAM NOTICE</p><h2>现在没有官方 MOOD 合约地址。</h2></div>
        <div><p>任何声称可以购买、领取、预售或添加 MOOD 的合约地址与交易链接，都不是本页面确认的官方发行信息。</p><p>只有在 Genesis 门槛通过后，本页才会同时公布完整合约地址、区块浏览器验证、权限说明、安全报告与签署后的发行决议。</p></div>
      </section>

      <section className="token-chapters">
        <article><img src="/mood-cafe.png" alt="山景中的开放咖啡馆与图书空间" /><div><span>WORLD</span><h3>世界可进入</h3><p>人先以 Resident、Creator、Developer 与 Node Operator 的身份真实参与。</p></div></article>
        <article><img src="/mood-road.png" alt="人们沿海岸道路自由旅行与创作" /><div><span>PROTOCOL</span><h3>规则可验证</h3><p>Contribution、Proof、Reputation、Governance 与 Economics 有明确规则和证据。</p></div></article>
        <article><img src="/mood-leisure.png" alt="夜色水上花园中的休息与创作" /><div><span>PORTAL</span><h3>参与可发生</h3><p>钱包、Passport、Agents、Nodes 与 Network 展示真实状态，而不是演示数字。</p></div></article>
      </section>

      <footer className="token-footer">
        <Link className="token-brand" href="/token"><img src="/moodify-brand-logo.png" alt="" /><span>MOOD</span></Link>
        <p>Issuance preparation in Hong Kong. This page is a project-status disclosure, not an offer, solicitation, investment advice or promise of returns.</p>
        <div><Link href="/world">World</Link><Link href="/protocol">Protocol</Link><Link href="/network">Network</Link></div>
      </footer>
    </main>
  );
}
