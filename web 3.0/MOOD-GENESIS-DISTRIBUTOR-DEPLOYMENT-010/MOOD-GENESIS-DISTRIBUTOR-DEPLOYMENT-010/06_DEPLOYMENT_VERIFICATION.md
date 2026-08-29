# Mainnet Deployment Verification

Record:

- chain ID;
- deployment tx hash;
- block;
- deployer;
- distributor address;
- gas used;
- status.

Verify all readable state actually exposed by the ABI, especially:

- MOOD token address;
- Merkle root;
- owner/admin;
- pause/claim settings if present.

Where possible compare expected and deployed runtime bytecode.

Attempt BscScan source verification and record:

`VERIFIED / PENDING / FAILED / NOT_SUPPORTED`

After funding verify:

- funding tx;
- token contract;
- sender;
- recipient;
- exact amount;
- distributor MOOD balance.

Any unexplained mismatch is a stop condition.
