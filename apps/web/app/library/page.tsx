import Link from "next/link";
import type { Metadata } from "next";
import {
  LIBRARY_DOCUMENTS,
  listByCategory,
  listFeatured,
  listDraft,
  listArchived,
  STATUS_LABEL,
  formatSha256,
} from "@/lib/mood/library";
import type { LibraryDocument } from "@/lib/mood/library";
import LibraryFilters from "./LibraryFilters";

export const metadata: Metadata = {
  title: "MOOD Library — Culture · Whitepaper · Protocol · Governance",
  description:
    "MOOD 的文化、世界观、白皮书与公共协议文献。",
};

type SearchParams = Record<string, string | string[] | undefined>;

function readParam(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) return value[0];
  return value;
}

function isEconomicsDraft(doc: LibraryDocument): boolean {
  return doc.category === "economics" && doc.status === "draft";
}

export default async function LibraryPage({
  searchParams,
}: {
  searchParams?: Promise<SearchParams>;
}) {
  const params = (await searchParams) ?? {};
  const category = readParam(params.category);
  const status = readParam(params.status);
  const language = readParam(params.language);
  const query = readParam(params.q);

  const allDocs = LIBRARY_DOCUMENTS;
  const filtered = allDocs.filter((doc) => {
    if (category && doc.category !== category) return false;
    if (status && doc.status !== status) return false;
    if (language && doc.language !== language) return false;
    if (query) {
      const q = query.toLowerCase();
      if (
        !doc.title.toLowerCase().includes(q) &&
        !doc.summary.toLowerCase().includes(q) &&
        !doc.slug.includes(q)
      ) {
        return false;
      }
    }
    return true;
  });

  const featured = listFeatured();
  const draft = listDraft();
  const archived = listArchived();
  const grouped = listByCategory();

  return (
    <main className="public-track library-root">
      <Link href="/">← Moodify</Link>

      <header className="library-hero">
        <span className="eyebrow">MOOD LIBRARY</span>
        <h1>MOOD 图书馆</h1>
        <p className="library-hero-sub">
          这里收藏 MOOD 的文化、世界观、公共规则与研究。技术告诉我们如何建设，文化告诉我们为什么出发。
        </p>
        <p className="library-hero-meta">
          注册于 <code>97c9106</code>（2026-08-30） · 共 {allDocs.length} 份文档 ·
          其中 active {allDocs.filter((d) => d.status === "active").length}，
          draft {draft.length}，archived {archived.length}。
        </p>
      </header>

      <section className="library-culture-shelf" aria-labelledby="library-culture-heading">
        <div>
          <span className="eyebrow">CULTURE / 文化</span>
          <h2 id="library-culture-heading">一个世界，也需要自己的书。</h2>
          <p>我们会在这里慢慢放入信念、宣言、边界、故事与思想。它们与协议和代码同样构成 MOOD。</p>
        </div>
        <div className="library-culture-links">
          <Link href="/library/mood-scope-freeze-cn"><small>中文 · 01</small><strong>MOOD 范围冻结</strong><span>阅读中文版本 →</span></Link>
          <Link href="/library/mood-scope-freeze-en"><small>ENGLISH · 01</small><strong>MOOD Scope Freeze</strong><span>Read in English →</span></Link>
        </div>
      </section>

      <LibraryFilters
        initialCategory={category}
        initialStatus={status}
        initialLanguage={language}
        initialQuery={query}
      />

      <section className="library-section" aria-labelledby="library-featured-heading">
        <h2 id="library-featured-heading">Featured</h2>
        <p className="library-section-help">
          活跃的 Foundation 与 Governance 文档。版本、状态、Source Commit 可在每页详情页查看。
        </p>
        <ul className="library-grid">
          {featured.map((doc) => (
            <li key={doc.slug} className="library-card">
              <div className="library-card-meta">
                <span className="library-status-pill" data-status={doc.status}>
                  {STATUS_LABEL[doc.status]}
                </span>
                <span className="library-category-pill">{doc.category}</span>
                <span className="library-version">v{doc.version}</span>
              </div>
              <h3>
                <Link href={doc.onlineUrl ?? `/library/${doc.slug}`}>{doc.title}</Link>
              </h3>
              <p className="library-summary">{doc.summary}</p>
              <p className="library-hash">
                SHA-256: <code>{formatSha256(doc.sha256)}</code>
              </p>
            </li>
          ))}
        </ul>
      </section>

      {filtered.length > 0 && (
        <section className="library-section" aria-labelledby="library-results-heading">
          <h2 id="library-results-heading">Filtered</h2>
          <p className="library-section-help">
            按当前过滤器显示 {filtered.length} 份文档。
          </p>
          <ul className="library-list">
            {filtered.map((doc) => (
              <li key={doc.slug} className="library-list-item">
                <span className="library-status-pill" data-status={doc.status}>
                  {STATUS_LABEL[doc.status]}
                </span>
                <Link href={doc.onlineUrl ?? `/library/${doc.slug}`} className="library-list-title">
                  {doc.title}
                </Link>
                <span className="library-list-version">v{doc.version}</span>
                <span className="library-list-category">{doc.category}</span>
                {isEconomicsDraft(doc) && (
                  <span className="library-list-warning">
                    Parameters UNFROZEN
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {grouped.map((group) => (
        <section key={group.category} className="library-section" aria-labelledby={`library-cat-${group.category}`}>
          <h2 id={`library-cat-${group.category}`}>{group.label}</h2>
          <ul className="library-list">
            {group.documents.map((doc) => (
              <li key={doc.slug} className="library-list-item">
                <span className="library-status-pill" data-status={doc.status}>
                  {STATUS_LABEL[doc.status]}
                </span>
                <Link href={doc.onlineUrl ?? `/library/${doc.slug}`} className="library-list-title">
                  {doc.title}
                </Link>
                <span className="library-list-version">v{doc.version}</span>
                <span className="library-list-language">{doc.language}</span>
                {isEconomicsDraft(doc) && (
                  <span className="library-list-warning">
                    Parameters UNFROZEN
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      ))}

      <section className="library-section" aria-labelledby="library-draft-heading">
        <h2 id="library-draft-heading">Draft &amp; Archived</h2>
        <p className="library-section-help">
          Draft 文档 <strong>不</strong> 应作为最终承诺解释。Archived / Superseded 文档仅作历史阅读。
        </p>
        <ul className="library-list">
          {draft.map((doc) => (
            <li key={doc.slug} className="library-list-item">
              <span className="library-status-pill" data-status={doc.status}>
                {STATUS_LABEL[doc.status]}
              </span>
              <Link href={doc.onlineUrl ?? `/library/${doc.slug}`} className="library-list-title">
                {doc.title}
              </Link>
              <span className="library-list-version">v{doc.version}</span>
            </li>
          ))}
          {archived.map((doc) => (
            <li key={doc.slug} className="library-list-item">
              <span className="library-status-pill" data-status={doc.status}>
                {STATUS_LABEL[doc.status]}
              </span>
              <Link href={doc.onlineUrl ?? `/library/${doc.slug}`} className="library-list-title">
                {doc.title}
              </Link>
              <span className="library-list-version">v{doc.version}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="library-section library-status-honesty">
        <h2>Status Honesty</h2>
        <ul>
          <li>
            <strong>Draft Tokenomics</strong>：Tokenomics / Treasury / Holder Rewards / Legacy Token /
            Launch Policy 全部 <code>Draft / Parameters UNFROZEN</code>。
          </li>
          <li>
            <strong>Historical Security</strong>：历史 Genesis v1.0 安全文档必须明确 <code>HISTORICAL / SUPERSEDED / LEGACY SCOPE</code>。
          </li>
          <li>
            <strong>No future official CA</strong>：Library 不显示未激活 Token CA、不显示 Buy / Trade CTA。
          </li>
        </ul>
      </section>
    </main>
  );
}
