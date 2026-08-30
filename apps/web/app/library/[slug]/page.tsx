import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { promises as fs } from "node:fs";
import path from "node:path";
import {
  getDocumentBySlug,
  LIBRARY_DOCUMENTS,
  STATUS_LABEL,
  formatSha256,
  economicsDraftDisclaimer,
  historicalSecurityDisclaimer,
} from "../../../../lib/mood/library";
import type { LibraryDocument } from "../../../../lib/mood/library";

export function generateStaticParams() {
  return LIBRARY_DOCUMENTS.map((doc) => ({ slug: doc.slug }));
}

export const dynamic = "force-static";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDocumentBySlug(slug);
  if (!doc) return { title: "Library entry not found" };
  return {
    title: `${doc.title} — MOOD Library`,
    description: doc.summary,
  };
}

function buildBreadcrumb(doc: LibraryDocument): string {
  return `Library / ${doc.category} / ${doc.title}`;
}

function buildTableOfContents(body: string): string[] {
  const lines = body.split(/\r?\n/);
  const out: string[] = [];
  for (const line of lines) {
    const m = line.match(/^#{1,3}\s+(.+)$/);
    if (m) out.push(m[1].trim());
  }
  return out;
}

async function readSourceBody(sourcePath: string): Promise<string | null> {
  try {
    const cwd = process.cwd();
    const full = path.isAbsolute(sourcePath)
      ? sourcePath
      : path.join(cwd, sourcePath);
    return await fs.readFile(full, "utf8");
  } catch {
    return null;
  }
}

function renderSourceMarkdown(md: string): string {
  // Minimal renderer (no HTML injection from content).
  // Supports: headings, paragraphs, lists, blockquotes, code fences.
  const escaped = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped;
}

export default async function LibraryEntryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const doc = getDocumentBySlug(slug);
  if (!doc) notFound();

  const sourceBody = await readSourceBody(doc.sourcePath);
  const hasSource = sourceBody !== null;
  const isEconomicsDraft =
    doc.category === "economics" && doc.status === "draft";
  const isHistoricalSecurity =
    doc.category === "security" &&
    (doc.status === "superseded" || doc.status === "archived");

  const toc = hasSource ? buildTableOfContents(sourceBody ?? "") : [];
  const renderedSource = hasSource
    ? renderSourceMarkdown(sourceBody ?? "")
    : "";

  return (
    <main className="public-track library-entry">
      <Link href="/library">← Library</Link>

      <header className="library-entry-header">
        <p className="library-entry-breadcrumb">{buildBreadcrumb(doc)}</p>
        <h1>{doc.title}</h1>
        <div className="library-entry-meta">
          <span className="library-status-pill" data-status={doc.status}>
            {STATUS_LABEL[doc.status]}
          </span>
          <span className="library-category-pill">{doc.category}</span>
          <span className="library-version">v{doc.version}</span>
          <span className="library-language-pill">{doc.language}</span>
        </div>
        {isEconomicsDraft && (
          <p className="library-disclaimer library-disclaimer-warning">
            {economicsDraftDisclaimer()}
          </p>
        )}
        {isHistoricalSecurity && (
          <p className="library-disclaimer library-disclaimer-warning">
            {historicalSecurityDisclaimer()}
          </p>
        )}
        <p className="library-entry-summary">{doc.summary}</p>
      </header>

      <section className="library-entry-facts">
        <h2>Document Facts</h2>
        <dl>
          <dt>Status</dt>
          <dd>{STATUS_LABEL[doc.status]}</dd>
          <dt>Version</dt>
          <dd>v{doc.version}</dd>
          <dt>Category</dt>
          <dd>{doc.category}</dd>
          <dt>Language</dt>
          <dd>{doc.language}</dd>
          <dt>Source Path</dt>
          <dd>
            <code>{doc.sourcePath}</code>
          </dd>
          <dt>Source Commit</dt>
          <dd>
            {doc.sourceSha ? (
              <code>{doc.sourceSha.slice(0, 12)}…</code>
            ) : (
              <code>Source commit SHA pending</code>
            )}
          </dd>
          <dt>SHA-256</dt>
          <dd>
            <code title={doc.sha256 ?? ""}>
              {formatSha256(doc.sha256)}
            </code>
          </dd>
          {doc.publishedAt && (
            <>
              <dt>Published</dt>
              <dd>{doc.publishedAt}</dd>
            </>
          )}
          {doc.updatedAt && (
            <>
              <dt>Last Updated</dt>
              <dd>{doc.updatedAt}</dd>
            </>
          )}
        </dl>
        <div className="library-entry-actions">
          {doc.githubUrl ? (
            <a href={doc.githubUrl} target="_blank" rel="noopener noreferrer">
              GitHub source
            </a>
          ) : (
            <span className="library-entry-missing">GitHub source not available</span>
          )}
          {doc.pdfUrl ? (
            <a href={doc.pdfUrl} target="_blank" rel="noopener noreferrer">
              PDF
            </a>
          ) : (
            <span className="library-entry-missing">PDF not available yet</span>
          )}
          {doc.ipfsCid ? (
            <a href={`https://ipfs.io/ipfs/${doc.ipfsCid}`} target="_blank" rel="noopener noreferrer">
              IPFS
            </a>
          ) : null}
        </div>
      </section>

      <section className="library-entry-toc">
        <h2>Table of Contents</h2>
        {toc.length > 0 ? (
          <ol>
            {toc.map((heading, idx) => (
              <li key={`${heading}-${idx}`}>{heading}</li>
            ))}
          </ol>
        ) : (
          <p>No headings detected.</p>
        )}
      </section>

      <section className="library-entry-body">
        <h2>Content</h2>
        {hasSource ? (
          <pre className="library-source" aria-label="Document source markdown">
            <code>{renderedSource}</code>
          </pre>
        ) : doc.skeleton ? (
          <article className="library-skeleton">
            {doc.skeleton.chapters.map((chapter) => (
              <section key={chapter.id} className={`library-skeleton-chapter status-${chapter.status}`}>
                <h3>{chapter.title}</h3>
                <p>{chapter.body}</p>
                {chapter.status === "draft" && (
                  <p className="library-disclaimer library-disclaimer-warning">
                    DRAFT — pending human ratification
                  </p>
                )}
                {chapter.status === "placeholder" && (
                  <p className="library-disclaimer library-disclaimer-muted">
                    Placeholder — no content committed at this time
                  </p>
                )}
              </section>
            ))}
          </article>
        ) : (
          <p className="library-disclaimer library-disclaimer-muted">
            Content not available yet. See source path on GitHub.
          </p>
        )}
      </section>

      <section className="library-entry-related">
        <h2>Related Documents</h2>
        <ul>
          {LIBRARY_DOCUMENTS.filter(
            (d) => d.slug !== doc.slug && d.category === doc.category,
          )
            .slice(0, 5)
            .map((d) => (
              <li key={d.slug}>
                <Link href={d.onlineUrl ?? `/library/${d.slug}`}>{d.title}</Link>{" "}
                <span className="library-status-pill" data-status={d.status}>
                  {STATUS_LABEL[d.status]}
                </span>
              </li>
            ))}
        </ul>
      </section>
    </main>
  );
}