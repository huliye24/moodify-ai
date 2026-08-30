/**
 * MOOD PASSPORT 015 — SIWE (EIP-4361) Message Builder
 *
 * Implements Sign-In with Ethereum message construction.
 * Reference: https://eips.ethereum.org/EIPS/eip-4361
 *
 * The message is intentionally human-readable to prevent phishing-style
 * "blind signing" attacks. Users always see what they are signing.
 */

import { normalizeEvmAddress } from "./evm-address.ts";
import type { SiweMessage } from "./types.ts";

/**
 * The fixed statement shown to the user when signing in.
 * Must NOT include any token / DEX / claim language.
 */
export const MOOD_SIGN_IN_STATEMENT = "Sign in to MOOD.";

/**
 * SIWE version supported by MOOD Passport (currently v1).
 */
export const SIWE_VERSION = "1";

/**
 * Default lifetime of a SIWE message (nonce expiry).
 * 15 minutes is industry-typical; long enough to read, short enough to
 * limit replay window.
 */
export const DEFAULT_NONCE_EXPIRY_MS = 15 * 60 * 1000;

/**
 * Build a SIWE message ready to be signed by the wallet.
 *
 * @param params.domain      - the SIWE "domain" (e.g. "moodify.example")
 * @param params.address     - the wallet address (normalized)
 * @param params.nonce       - server-issued single-use nonce
 * @param params.chainId     - the chain ID (56 = BSC at present, but not hard-coded)
 * @param params.uri         - the canonical URI of the resource being signed into
 * @param params.statement   - optional override of the fixed statement
 * @param params.ttlMs       - optional override of expiry window
 */
export function buildSiweMessage(params: {
  domain: string;
  address: string;
  nonce: string;
  chainId: number;
  uri: string;
  statement?: string;
  ttlMs?: number;
  requestId?: string;
}): SiweMessage {
  const normalized = normalizeEvmAddress(params.address);
  if (!normalized) throw new Error("invalid-address");
  if (!params.nonce || params.nonce.length < 8) {
    throw new Error("invalid-nonce");
  }
  if (!Number.isInteger(params.chainId) || params.chainId <= 0) {
    throw new Error("invalid-chain-id");
  }
  if (typeof params.domain !== "string" || !params.domain.trim()) {
    throw new Error("invalid-domain");
  }
  if (typeof params.uri !== "string" || !params.uri.trim()) {
    throw new Error("invalid-uri");
  }

  const ttlMs = params.ttlMs ?? DEFAULT_NONCE_EXPIRY_MS;
  const issued = new Date();
  const expires = new Date(issued.getTime() + ttlMs);

  const message: SiweMessage = {
    domain: params.domain.trim(),
    address: normalized,
    statement: params.statement ?? MOOD_SIGN_IN_STATEMENT,
    uri: params.uri.trim(),
    version: SIWE_VERSION,
    chainId: params.chainId,
    nonce: params.nonce,
    issuedAt: issued.toISOString(),
    expirationTime: expires.toISOString(),
    requestId: params.requestId,
  };

  return message;
}

/**
 * Serialize a SIWE message to its canonical human-readable text form,
 * exactly as it should be signed by the wallet.
 *
 * Format follows EIP-4361 §3:
 * <domain> wants you to sign in with your Ethereum account:
 * <address>
 *
 * <statement>
 *
 * URI: <uri>
 * Version: <version>
 * Chain ID: <chainId>
 * Nonce: <nonce>
 * Issued At: <issuedAt>
 * Expiration Time: <expirationTime>
 */
export function renderSiweMessage(msg: SiweMessage): string {
  const lines = [
    `${msg.domain} wants you to sign in with your Ethereum account:`,
    msg.address,
    "",
    msg.statement,
    "",
    `URI: ${msg.uri}`,
    `Version: ${msg.version}`,
    `Chain ID: ${msg.chainId}`,
    `Nonce: ${msg.nonce}`,
    `Issued At: ${msg.issuedAt}`,
  ];
  if (msg.expirationTime) {
    lines.push(`Expiration Time: ${msg.expirationTime}`);
  }
  if (msg.notBefore) {
    lines.push(`Not Before: ${msg.notBefore}`);
  }
  if (msg.requestId) {
    lines.push(`Request ID: ${msg.requestId}`);
  }
  if (msg.resources && msg.resources.length > 0) {
    for (const r of msg.resources) lines.push(`Resource: ${r}`);
  }
  return lines.join("\n");
}

/**
 * Re-parse a SIWE message string back into a structured object.
 * Strict: returns null if any required field is missing or invalid.
 */
export function parseSiweMessage(text: string): SiweMessage | null {
  if (typeof text !== "string") return null;
  const lines = text.split("\n");
  if (lines.length < 8) return null;

  const domainLine = lines[0] ?? "";
  const dm = /^(.+) wants you to sign in with your Ethereum account:$/.exec(
    domainLine,
  );
  if (!dm) return null;
  const domain = (dm[1] ?? "").trim();

  const addressLine = (lines[1] ?? "").trim();
  const normalized = normalizeEvmAddress(addressLine);
  if (!normalized) return null;

  // Statement is the line right after the blank line that follows addressLine.
  let statement = "";
  let i = 2;
  if (lines[i] === "") {
    i++;
    const stmtLines: string[] = [];
    while (i < lines.length && lines[i] !== "") {
      stmtLines.push(lines[i] ?? "");
      i++;
    }
    statement = stmtLines.join("\n");
  }

  // After the blank line, read label: value lines.
  const fields: Record<string, string> = {};
  while (i < lines.length) {
    const line = lines[i] ?? "";
    const fm = /^([A-Z][A-Za-z ]+):\s*(.+)$/.exec(line);
    if (fm) {
      fields[fm[1]!.trim()] = fm[2]!.trim();
    }
    i++;
  }

  const version = fields["Version"];
  if (version !== SIWE_VERSION) return null;

  const uri = fields["URI"];
  const nonce = fields["Nonce"];
  const chainIdStr = fields["Chain ID"];
  const issuedAt = fields["Issued At"];

  if (!uri || !nonce || !chainIdStr || !issuedAt) return null;

  const chainId = Number(chainIdStr);
  if (!Number.isInteger(chainId) || chainId <= 0) return null;

  const message: SiweMessage = {
    domain,
    address: normalized,
    statement,
    uri,
    version,
    chainId,
    nonce,
    issuedAt,
    expirationTime: fields["Expiration Time"],
    notBefore: fields["Not Before"],
    requestId: fields["Request ID"],
    resources: [],
  };

  return message;
}
