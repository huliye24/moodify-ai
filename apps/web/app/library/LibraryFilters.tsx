"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";

const CATEGORIES = ["", "foundation", "protocol", "governance", "economics", "security", "research"];
const STATUSES = ["", "active", "draft", "superseded", "archived"];
const LANGUAGES = ["", "zh", "en", "bilingual"];

const CATEGORY_LABEL: Record<string, string> = {
  "": "All categories",
  foundation: "Foundation",
  protocol: "Protocol",
  governance: "Governance",
  economics: "Economics",
  security: "Security",
  research: "Research",
};

const STATUS_LABEL: Record<string, string> = {
  "": "All statuses",
  active: "ACTIVE",
  draft: "DRAFT",
  superseded: "SUPERSEDED",
  archived: "ARCHIVED",
};

const LANGUAGE_LABEL: Record<string, string> = {
  "": "All languages",
  zh: "中文",
  en: "English",
  bilingual: "Bilingual",
};

export default function LibraryFilters({
  initialCategory,
  initialStatus,
  initialLanguage,
  initialQuery,
}: {
  initialCategory?: string;
  initialStatus?: string;
  initialLanguage?: string;
  initialQuery?: string;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const [pending, startTransition] = useTransition();
  const [q, setQ] = useState(initialQuery ?? "");

  function pushParams(next: Record<string, string | undefined>) {
    const usp = new URLSearchParams(params?.toString() ?? "");
    for (const [key, value] of Object.entries(next)) {
      if (!value) usp.delete(key);
      else usp.set(key, value);
    }
    const qs = usp.toString();
    startTransition(() => {
      router.replace(qs ? `/library?${qs}` : "/library");
    });
  }

  return (
    <form
      className="library-filters"
      role="search"
      aria-label="Library filters"
      onSubmit={(event) => {
        event.preventDefault();
        pushParams({ q });
      }}
    >
      <label className="library-filter">
        <span>Search</span>
        <input
          type="search"
          value={q}
          onChange={(event) => setQ(event.target.value)}
          placeholder="title, summary, slug…"
          aria-label="Search library"
        />
      </label>

      <label className="library-filter">
        <span>Category</span>
        <select
          defaultValue={initialCategory ?? ""}
          onChange={(event) => pushParams({ category: event.target.value || undefined })}
          aria-label="Filter by category"
        >
          {CATEGORIES.map((c) => (
            <option key={c || "all"} value={c}>
              {CATEGORY_LABEL[c]}
            </option>
          ))}
        </select>
      </label>

      <label className="library-filter">
        <span>Status</span>
        <select
          defaultValue={initialStatus ?? ""}
          onChange={(event) => pushParams({ status: event.target.value || undefined })}
          aria-label="Filter by status"
        >
          {STATUSES.map((s) => (
            <option key={s || "all"} value={s}>
              {STATUS_LABEL[s]}
            </option>
          ))}
        </select>
      </label>

      <label className="library-filter">
        <span>Language</span>
        <select
          defaultValue={initialLanguage ?? ""}
          onChange={(event) => pushParams({ language: event.target.value || undefined })}
          aria-label="Filter by language"
        >
          {LANGUAGES.map((l) => (
            <option key={l || "all"} value={l}>
              {LANGUAGE_LABEL[l]}
            </option>
          ))}
        </select>
      </label>

      {pending && <span className="library-filter-loading">updating…</span>}
    </form>
  );
}