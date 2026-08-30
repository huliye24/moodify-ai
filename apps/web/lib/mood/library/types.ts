// MOOD LIBRARY 014 — Type definitions
// Authority: docs/mood/library/014_METADATA_SCHEMA.md

export type LibraryDocumentStatus =
  | "draft"
  | "active"
  | "superseded"
  | "archived";

export type LibraryDocumentCategory =
  | "foundation"
  | "protocol"
  | "governance"
  | "economics"
  | "security"
  | "research";

export type LibraryDocumentLanguage = "zh" | "en" | "bilingual";

export type LibraryDocument = {
  // stable identifier (lowercase-kebab, no version suffix)
  slug: string;

  // display
  title: string;
  summary: string;
  category: LibraryDocumentCategory;
  language: LibraryDocumentLanguage;

  // versioning
  version: string;
  status: LibraryDocumentStatus;

  // source provenance
  sourcePath: string;
  sourceSha?: string;

  // publication surfaces (optional; absent => not provided)
  pdfUrl?: string;
  onlineUrl?: string;
  githubUrl?: string;
  ipfsCid?: string;

  // hash (optional; absent => "Hash unavailable")
  sha256?: string;

  // timestamps (ISO 8601)
  publishedAt?: string;
  updatedAt?: string;

  // 014 skeleton support: optional inline body for skeleton-only docs
  // (used when sourcePath does not exist in the repo yet)
  skeleton?: {
    chapters: Array<{
      id: string;
      title: string;
      body: string;
      status: "draft" | "placeholder";
    }>;
  };

  // relation
  supersededBy?: string;
  supersedes?: string;
};

export type LibraryFilter = {
  category?: LibraryDocumentCategory;
  status?: LibraryDocumentStatus;
  language?: LibraryDocumentLanguage;
  query?: string;
};

export type LibraryCategoryGroup = {
  category: LibraryDocumentCategory;
  label: string;
  documents: LibraryDocument[];
};