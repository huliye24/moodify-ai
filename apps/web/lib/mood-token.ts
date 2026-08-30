/* MOOD token single source of truth — MOOD-GENESIS-001.
   This module is the ONLY application-level authority for MOOD token facts
   (chain, contract, supply, links, DEX metadata). UI pages must import from
   here and never hard-code the contract address elsewhere.
   Contract/address changes require human confirmation (see
   docs/protocol/MOOD_TOKEN.md). Facts mirror the MOOD-GENESIS-001 package
   canon; chain-readable values were verified against the deployed BEP-20
   contract on BNB Smart Chain. */

export const MOOD_TOKEN = {
  /** BNB Smart Chain mainnet */
  chainId: 56,
  network: "BNB Smart Chain",
  /** BEP-20 token name */
  name: "Moodify",
  /** BEP-20 symbol */
  symbol: "Mood",
  /** Official deployed contract (verified on BscScan). Never edit without human approval. */
  address: "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
  decimals: 18,
  /** Raw on-chain total supply (base units, as string). */
  totalSupply: "33000000",
  /** Human-readable total supply. */
  totalSupplyDisplay: "33,000,000 MOOD",
  /** Contract page on BscScan. */
  explorerUrl: "https://bscscan.com/token/0x1BB3115D43E397f7bb586F090831B02cA639e73E",
  /** Official trading entry on the primary DEX. */
  tradeUrl: "https://pancakeswap.finance/swap?outputCurrency=0x1BB3115D43E397f7bb586F090831B02cA639e73E",
  /** Moodify Product Home (canon: one site, one role). */
  officialSite: "https://rongjingmusic.com/",
  /** Moodify open-source repository. */
  githubUrl: "https://github.com/huliye24/moodify-ai",
  /** Primary DEX metadata. Pool address intentionally omitted: do not
      fabricate or hard-code a pool address unless verified from
      chain/explorer (MOOD-GENESIS-001 token canon). */
  dex: {
    name: "PancakeSwap V3",
    pair: "MOOD / WBNB",
    feeTier: "1%",
  },
} as const;

export type MoodToken = typeof MOOD_TOKEN;
