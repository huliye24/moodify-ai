"use client";

/**
 * MOOD-GENESIS-009: Wallet Connection Component
 *
 * Provides wallet connectivity UI with BSC mainnet detection.
 */

import { useWallet } from "../../lib/wallet";
import { Button } from "../../components/ui/primitives";

export default function WalletConnect() {
  const { state, account, error, hasWallet, connect, disconnect, switchToBSC } =
    useWallet();

  // Disconnected state
  if (state === "disconnected") {
    return (
      <div
        style={{
          padding: "var(--space-4)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-lg)",
          background: "var(--surface-subtle)",
        }}
      >
        <h3
          style={{
            margin: 0,
            fontFamily: "var(--font-display)",
            fontSize: "var(--text-lg)",
            color: "var(--text)",
          }}
        >
          连接钱包
        </h3>
        <p
          style={{
            margin: "var(--space-2) 0",
            fontSize: "var(--text-sm)",
            color: "var(--text-muted)",
          }}
        >
          连接您的 EVM 钱包以查看 MOOD 余额
        </p>
        {!hasWallet && (
          <p
            style={{
              margin: "var(--space-2) 0",
              fontSize: "var(--text-sm)",
              color: "var(--attention)",
            }}
          >
            未检测到钱包。请安装 MetaMask 或其他兼容钱包。
          </p>
        )}
        <Button
          type="button"
          variant="primary"
          onClick={connect}
          disabled={!hasWallet}
        >
          连接钱包
        </Button>
      </div>
    );
  }

  // Connecting state
  if (state === "connecting") {
    return (
      <div
        style={{
          padding: "var(--space-4)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-lg)",
          background: "var(--surface-subtle)",
        }}
      >
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
          正在连接钱包...
        </p>
      </div>
    );
  }

  // Wrong network state
  if (state === "wrongNetwork") {
    return (
      <div
        style={{
          padding: "var(--space-4)",
          border: "1px solid var(--attention)",
          borderLeft: "3px solid var(--attention)",
          borderRadius: "var(--radius-lg)",
          background: "var(--attention-soft)",
        }}
      >
        <h3
          style={{
            margin: 0,
            fontFamily: "var(--font-display)",
            fontSize: "var(--text-lg)",
            color: "var(--text)",
          }}
        >
          网络错误
        </h3>
        <p
          style={{
            margin: "var(--space-2) 0",
            fontSize: "var(--text-sm)",
            color: "var(--text-muted)",
          }}
        >
          当前网络: Chain ID {account?.chainId || "未知"}
          <br />
          需要切换到: BNB Smart Chain (Chain ID 56)
        </p>
        <Button type="button" variant="primary" onClick={switchToBSC}>
          切换到 BNB Smart Chain
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={disconnect}
          style={{ marginLeft: "var(--space-2)" }}
        >
          断开连接
        </Button>
      </div>
    );
  }

  // Error state
  if (state === "error") {
    return (
      <div
        style={{
          padding: "var(--space-4)",
          border: "1px solid var(--blocking)",
          borderLeft: "3px solid var(--blocking)",
          borderRadius: "var(--radius-lg)",
          background: "var(--blocking-soft)",
        }}
      >
        <h3
          style={{
            margin: 0,
            fontFamily: "var(--font-display)",
            fontSize: "var(--text-lg)",
            color: "var(--text)",
          }}
        >
          连接错误
        </h3>
        <p
          style={{
            margin: "var(--space-2) 0",
            fontSize: "var(--text-sm)",
            color: "var(--blocking)",
          }}
        >
          {error?.message || "未知错误"}
        </p>
        <Button type="button" variant="primary" onClick={connect}>
          重试连接
        </Button>
      </div>
    );
  }

  // Connected state
  if (state === "connected" && account) {
    return (
      <div
        style={{
          padding: "var(--space-4)",
          border: "1px solid var(--evidence)",
          borderLeft: "3px solid var(--evidence)",
          borderRadius: "var(--radius-lg)",
          background: "var(--evidence-soft)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "var(--space-3)",
          }}
        >
          <div>
            <p
              style={{
                margin: 0,
                fontSize: "var(--text-xs)",
                color: "var(--text-faint)",
                textTransform: "uppercase",
                letterSpacing: "0.1em",
              }}
            >
              已连接钱包
            </p>
            <p
              style={{
                margin: "var(--space-1) 0 0",
                fontSize: "var(--text-md)",
                color: "var(--text)",
                fontFamily: "ui-monospace, monospace",
              }}
            >
              {account.addressShort}
            </p>
          </div>
          <Button type="button" variant="ghost" size="sm" onClick={disconnect}>
            断开
          </Button>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-2)",
            marginBottom: "var(--space-3)",
          }}
        >
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--space-1)",
              padding: "var(--space-1) var(--space-3)",
              borderRadius: "var(--radius-pill)",
              border: "1px solid var(--evidence)",
              background: "var(--evidence-soft)",
              fontSize: "var(--text-xs)",
              color: "var(--text)",
            }}
          >
            <span
              aria-hidden
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: "var(--evidence)",
              }}
            />
            BNB Smart Chain
          </span>
          <span style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
            Chain ID {account.chainId}
          </span>
        </div>

        <div
          style={{
            padding: "var(--space-3)",
            borderRadius: "var(--radius-md)",
            background: "var(--bg)",
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: "var(--text-xs)",
              color: "var(--text-faint)",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
            }}
          >
            MOOD 余额
          </p>
          {account.moodBalanceLoading ? (
            <p
              style={{
                margin: "var(--space-2) 0 0",
                fontSize: "var(--text-lg)",
                color: "var(--text-muted)",
              }}
            >
              读取中...
            </p>
          ) : account.moodBalance ? (
            <p
              style={{
                margin: "var(--space-2) 0 0",
                fontSize: "var(--text-xl)",
                color: "var(--text)",
                fontWeight: 600,
              }}
            >
              {account.moodBalance} MOOD
            </p>
          ) : (
            <p
              style={{
                margin: "var(--space-2) 0 0",
                fontSize: "var(--text-sm)",
                color: "var(--text-muted)",
              }}
            >
              无法读取余额
            </p>
          )}
        </div>
      </div>
    );
  }

  return null;
}
