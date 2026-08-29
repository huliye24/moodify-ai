# Stop Conditions

## P0

Stop immediately for:

- private key/seed exposure;
- wrong MOOD contract address;
- non-deterministic Merkle root;
- unreconciled allocation total;
- deployment on wrong chain;
- deployed state differing from approved state;
- wrong funding recipient/token;
- unexpected asset movement;
- public claim becoming executable before Package 011.

## P1

Resolve before launch for:

- failed BscScan source verification;
- staging cannot read distributor state;
- undocumented treasury source;
- unclear owner/admin state;
- unexplained distributor balance mismatch;
- unstable Package 009 staging.

Do not work around P0 conditions.
