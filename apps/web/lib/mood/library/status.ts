// MOOD LIBRARY 014 — Status helpers
// Authority: docs/mood/library/014_PUBLICATION_POLICY.md

import type { LibraryDocument, LibraryDocumentStatus } from "./types";

export const STATUS_LABEL: Record<LibraryDocumentStatus, string> = {
  active: "ACTIVE",
  draft: "DRAFT",
  superseded: "SUPERSEDED",
  archived: "ARCHIVED",
};

export const STATUS_TONE: Record<LibraryDocumentStatus, "success" | "muted" | "warning" | "archived"> = {
  active: "success",
  draft: "muted",
  superseded: "warning",
  archived: "archived",
};

export function isEconomicsDraft(doc: LibraryDocument): boolean {
  return doc.category === "economics" && doc.status === "draft";
}

export function isHistoricalSecurity(doc: LibraryDocument): boolean {
  return (
    doc.category === "security" &&
    (doc.status === "superseded" || doc.status === "archived")
  );
}

export function economicsDraftDisclaimer(): string {
  return "Parameters are not frozen and do not represent an active token configuration.";
}

export function historicalSecurityDisclaimer(): string {
  return "HISTORICAL / SUPERSEDED / LEGACY SCOPE — Not an audit of any future MOOD Token contract.";
}

export function isReadyForPublication(doc: LibraryDocument): boolean {
  return Boolean(doc.slug && doc.title && doc.version && doc.sourcePath);
}