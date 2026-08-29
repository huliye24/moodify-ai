"use client";

/**
 * MOOD-GENESIS-009: Wallet Connection Hook
 *
 * Provides wallet connectivity with BSC mainnet detection.
 * Uses viem for typed chain interactions.
 */

import { useState, useEffect, useCallback } from "react";
import { createWalletClient, custom, publicActions } from "viem";
import { bsc } from "viem/chains";
import { getBalance, formatMood } from "./mood-chain";

const BSC_CHAIN_ID = 56;
const BSC_HEX = "0x38";

type InjectedProvider = {
  isMetaMask?: boolean;
  providers?: InjectedProvider[];
  request: (args: { method: string; params?: unknown[] }) => Promise<any>;
  on: (event: string, handler: (...args: any[]) => void) => void;
  removeListener: (event: string, handler: (...args: any[]) => void) => void;
};

/** Prefer MetaMask when several browser wallets inject providers. */
function getInjectedProvider(): InjectedProvider | null {
  if (typeof window === "undefined") return null;
  const injected = (window as any).ethereum as InjectedProvider | undefined;
  if (!injected) return null;
  return injected.providers?.find((provider) => provider.isMetaMask) ?? injected;
}

export type WalletState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "wrongNetwork"
  | "error";

export interface WalletAccount {
  address: string;
  addressShort: string;
  chainId: number;
  isBSC: boolean;
  moodBalance: string | null;
  moodBalanceLoading: boolean;
}

export interface WalletError {
  code: string;
  message: string;
}

export function useWallet() {
  const [state, setState] = useState<WalletState>("disconnected");
  const [account, setAccount] = useState<WalletAccount | null>(null);
  const [error, setError] = useState<WalletError | null>(null);

  // Check if wallet is available
  const hasWallet = !!getInjectedProvider();

  // Get wallet client
  const getWalletClient = useCallback(() => {
    if (!hasWallet) return null;
    return createWalletClient({
      chain: bsc,
      transport: custom(getInjectedProvider()!),
    }).extend(publicActions);
  }, [hasWallet]);

  // Fetch MOOD balance
  const fetchMoodBalance = useCallback(async (address: string) => {
    if (!address) return;

    setAccount((prev) =>
      prev ? { ...prev, moodBalanceLoading: true } : null
    );

    try {
      const balanceData = await getBalance(address);
      if (balanceData.source === "rpc" && balanceData.value) {
        setAccount((prev) =>
          prev
            ? {
                ...prev,
                moodBalance: formatMood(balanceData.value),
                moodBalanceLoading: false,
              }
            : null
        );
      } else {
        setAccount((prev) =>
          prev
            ? { ...prev, moodBalance: null, moodBalanceLoading: false }
            : null
        );
      }
    } catch {
      setAccount((prev) =>
        prev
          ? { ...prev, moodBalance: null, moodBalanceLoading: false }
          : null
      );
    }
  }, []);

  // Check connection on mount
  useEffect(() => {
    if (!hasWallet) return;

    const checkConnection = async () => {
      try {
        const ethereum = getInjectedProvider();
        if (!ethereum) return;
        const accounts = await ethereum.request({ method: "eth_accounts" });

        if (accounts.length > 0) {
          const chainIdHex = await ethereum.request({ method: "eth_chainId" });
          const chainId = parseInt(chainIdHex, 16);
          const isBSC = chainId === BSC_CHAIN_ID;

          const address = accounts[0];
          const newAccount: WalletAccount = {
            address,
            addressShort: `${address.slice(0, 6)}...${address.slice(-4)}`,
            chainId,
            isBSC,
            moodBalance: null,
            moodBalanceLoading: true,
          };

          setAccount(newAccount);
          setState(isBSC ? "connected" : "wrongNetwork");

          if (isBSC) {
            fetchMoodBalance(address);
          }
        }
      } catch (err) {
        console.error("Failed to check connection:", err);
      }
    };

    checkConnection();
  }, [hasWallet, fetchMoodBalance]);

  // Listen for account/chain changes
  useEffect(() => {
    if (!hasWallet) return;

    const ethereum = getInjectedProvider();
    if (!ethereum) return;

    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        setState("disconnected");
        setAccount(null);
      } else {
        const address = accounts[0];
        setAccount((prev) =>
          prev
            ? {
                ...prev,
                address,
                addressShort: `${address.slice(0, 6)}...${address.slice(-4)}`,
              }
            : {
                address,
                addressShort: `${address.slice(0, 6)}...${address.slice(-4)}`,
                chainId: prev?.chainId || BSC_CHAIN_ID,
                isBSC: prev?.isBSC || true,
                moodBalance: null,
                moodBalanceLoading: true,
              }
        );
        fetchMoodBalance(address);
      }
    };

    const handleChainChanged = (chainIdHex: string) => {
      const chainId = parseInt(chainIdHex, 16);
      const isBSC = chainId === BSC_CHAIN_ID;

      setAccount((prev) =>
        prev
          ? { ...prev, chainId, isBSC, moodBalance: null }
          : null
      );
      setState(isBSC ? "connected" : "wrongNetwork");

      if (isBSC && account?.address) {
        fetchMoodBalance(account.address);
      }
    };

    ethereum.on("accountsChanged", handleAccountsChanged);
    ethereum.on("chainChanged", handleChainChanged);

    return () => {
      ethereum.removeListener("accountsChanged", handleAccountsChanged);
      ethereum.removeListener("chainChanged", handleChainChanged);
    };
  }, [hasWallet, account?.address, fetchMoodBalance]);

  // Connect wallet
  const connect = useCallback(async () => {
    if (!hasWallet) {
      setError({ code: "NO_WALLET", message: "未检测到 EVM 钱包" });
      setState("error");
      return;
    }

    setState("connecting");
    setError(null);

    try {
      const ethereum = getInjectedProvider();
      if (!ethereum) throw new Error("未检测到 MetaMask");
      const accounts = await ethereum.request({
        method: "eth_requestAccounts",
      });

      if (accounts.length === 0) {
        throw new Error("No accounts returned");
      }

      const chainIdHex = await ethereum.request({ method: "eth_chainId" });
      const chainId = parseInt(chainIdHex, 16);
      const isBSC = chainId === BSC_CHAIN_ID;
      const address = accounts[0];

      const newAccount: WalletAccount = {
        address,
        addressShort: `${address.slice(0, 6)}...${address.slice(-4)}`,
        chainId,
        isBSC,
        moodBalance: null,
        moodBalanceLoading: true,
      };

      setAccount(newAccount);
      setState(isBSC ? "connected" : "wrongNetwork");

      if (isBSC) {
        fetchMoodBalance(address);
      }
    } catch (err: any) {
      setError({
        code: "CONNECT_FAILED",
        message: err.message || "连接失败",
      });
      setState("error");
    }
  }, [hasWallet, fetchMoodBalance]);

  // Disconnect (clear local state)
  const disconnect = useCallback(() => {
    setState("disconnected");
    setAccount(null);
    setError(null);
  }, []);

  // Switch to BSC
  const switchToBSC = useCallback(async () => {
    if (!hasWallet) return;

    try {
      const ethereum = getInjectedProvider();
      if (!ethereum) return;
      await ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: BSC_HEX }],
      });
    } catch (switchError: any) {
      // Chain not added, try to add it
      if (switchError.code === 4902) {
        try {
          await ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: BSC_HEX,
                chainName: "BNB Smart Chain",
                nativeCurrency: {
                  name: "BNB",
                  symbol: "BNB",
                  decimals: 18,
                },
                rpcUrls: ["https://bsc-dataseed-public.bnbchain.org"],
                blockExplorerUrls: ["https://bscscan.com"],
              },
            ],
          });
          const accounts = await ethereum.request({ method: "eth_accounts" });
          if (accounts[0]) {
            const address = accounts[0];
            setAccount({ address, addressShort: `${address.slice(0, 6)}...${address.slice(-4)}`, chainId: BSC_CHAIN_ID, isBSC: true, moodBalance: null, moodBalanceLoading: true });
            setState("connected");
            fetchMoodBalance(address);
          }
        } catch (addError: any) {
          setError({
            code: "SWITCH_FAILED",
            message: addError.message || "切换网络失败",
          });
        }
      } else {
        setError({
          code: "SWITCH_FAILED",
          message: switchError.message || "切换网络失败",
        });
      }
    }
  }, [hasWallet, fetchMoodBalance]);

  return {
    state,
    account,
    error,
    hasWallet,
    connect,
    disconnect,
    switchToBSC,
  };
}
