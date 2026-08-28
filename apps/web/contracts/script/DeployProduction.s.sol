// SPDX-License-Identifier: GPL-3.0-only
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {MoodGenesisDistributor} from "../protocol/MoodGenesisDistributor.sol";

/**
 * @title DeployProduction
 * @notice Production deployment preparation for BNB Smart Chain
 *
 * IMPORTANT: This script PREPARES the deployment transaction.
 * It does NOT sign or broadcast automatically.
 *
 * Human approval required before:
 * - Setting PRIVATE_KEY environment variable
 * - Running with --broadcast flag
 *
 * Usage (dry run):
 *   forge script contracts/script/DeployProduction.s.sol --rpc-url bsc
 *
 * Usage (with broadcast - HUMAN APPROVAL REQUIRED):
 *   forge script contracts/script/DeployProduction.s.sol --rpc-url bsc --broadcast
 *
 * Required environment variables:
 *   - PRODUCTION_PRIVATE_KEY (only when ready to broadcast)
 *   - BSC_RPC (or use default in foundry.toml)
 */

contract DeployProduction is Script {
    // Official MOOD token on BNB Smart Chain
    address public constant MOOD_TOKEN = 0x1BB3115D43E397f7bb586F090831B02cA639e73E;

    // Chain ID verification
    uint256 public constant EXPECTED_CHAIN_ID = 56;

    function run() external {
        // Verify chain
        uint256 chainId = block.chainid;
        require(chainId == EXPECTED_CHAIN_ID, "Wrong chain - expected BNB Smart Chain (56)");

        console2.log("=".repeat(60));
        console2.log("MOOD-GENESIS-005: Production Deployment");
        console2.log("=".repeat(60));
        console2.log();

        // Read configuration from environment
        bytes32 merkleRoot = vm.envBytes32("MERKLE_ROOT");
        uint256 deadline = vm.envUint("CLAIM_DEADLINE"); // 0 for no deadline
        address owner = vm.envAddress("RECOVERY_OWNER"); // address(0) for no recovery

        // Validate configuration
        require(merkleRoot != bytes32(0), "MERKLE_ROOT must be set");
        require(MOOD_TOKEN.code.length > 0, "MOOD token not deployed at expected address");

        console2.log("Configuration:");
        console2.log("  Chain ID:", chainId);
        console2.log("  MOOD Token:", MOOD_TOKEN);
        console2.log("  Merkle Root:");
        console2.logBytes32(merkleRoot);
        console2.log("  Deadline:", deadline == 0 ? "None" : vm.toString(deadline));
        console2.log("  Recovery Owner:", owner == address(0) ? "None" : owner);
        console2.log();

        // Check if private key is available (for actual deployment)
        string memory privateKeyEnv = vm.envOr("PRODUCTION_PRIVATE_KEY", string(""));
        bool hasPrivateKey = bytes(privateKeyEnv).length > 0;

        if (!hasPrivateKey) {
            console2.log("DRY RUN MODE");
            console2.log("No PRODUCTION_PRIVATE_KEY set - simulating deployment");
            console2.log();
            console2.log("To deploy, set:");
            console2.log("  export PRODUCTION_PRIVATE_KEY=<your_private_key>");
            console2.log("  export MERKLE_ROOT=<approved_root>");
            console2.log("  export CLAIM_DEADLINE=<unix_timestamp_or_0>");
            console2.log("  export RECOVERY_OWNER=<owner_address_or_0>");
            console2.log();
            console2.log("Then run with --broadcast flag");
            console2.log();

            // Simulate deployment
            _simulateDeployment(merkleRoot, deadline, owner);
            return;
        }

        // PRODUCTION DEPLOYMENT - HUMAN APPROVAL REQUIRED
        console2.log("PRODUCTION DEPLOYMENT");
        console2.log("This will deploy to BNB Smart Chain mainnet!");
        console2.log();

        uint256 deployerPrivateKey = vm.envUint("PRODUCTION_PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console2.log("Deployer:", deployer);
        console2.log("Deployer balance:", deployer.balance);
        console2.log();

        // Additional safety check
        console2.log("SAFETY CHECK: Verify the above configuration is correct.");
        console2.log("This transaction will be broadcast to mainnet.");
        console2.log();

        // Deployment
        vm.startBroadcast(deployerPrivateKey);

        MoodGenesisDistributor distributor = new MoodGenesisDistributor(
            MOOD_TOKEN,
            merkleRoot,
            deadline,
            owner
        );

        vm.stopBroadcast();

        console2.log("=".repeat(60));
        console2.log("DEPLOYMENT SUCCESSFUL");
        console2.log("=".repeat(60));
        console2.log("Distributor Address:", address(distributor));
        console2.log();
        console2.log("NEXT STEPS:");
        console2.log("1. Verify contract on BscScan");
        console2.log("2. Fund distributor with MOOD tokens");
        console2.log("3. Update deployment record");
        console2.log();

        // Generate deployment record
        _generateDeploymentRecord(address(distributor), merkleRoot, deadline, owner, deployer);
    }

    function _simulateDeployment(
        bytes32 merkleRoot,
        uint256 deadline,
        address owner
    ) internal {
        console2.log("Simulated deployment parameters:");
        console2.log("  Token:", MOOD_TOKEN);
        console2.log("  Merkle Root:");
        console2.logBytes32(merkleRoot);
        console2.log("  Deadline:", deadline);
        console2.log("  Owner:", owner);
        console2.log();
        console2.log("Simulation complete. No transaction broadcast.");
    }

    function _generateDeploymentRecord(
        address distributor,
        bytes32 merkleRoot,
        uint256 deadline,
        address owner,
        address deployer
    ) internal {
        console2.log("Deployment Record:");
        console2.log("{");
        console2.log('  "chainId":', EXPECTED_CHAIN_ID, ",");
        console2.log('  "tokenAddress": "', MOOD_TOKEN, '",');
        console2.log('  "distributorAddress": "', distributor, '",');
        console2.log('  "merkleRoot": "', vm.toString(merkleRoot), '",');
        console2.log('  "snapshotId": "', vm.envOr("SNAPSHOT_ID", string("unknown")), '",');
        console2.log('  "snapshotSha256": "', vm.envOr("SNAPSHOT_SHA256", string("unknown")), '",');
        console2.log('  "participantCount":', vm.envOr("PARTICIPANT_COUNT", uint256(0)), ",");
        console2.log('  "totalMood": "', vm.envOr("TOTAL_MOOD", string("unknown")), '",');
        console2.log('  "deployedTx": "', vm.toString(tx.origin), '",');
        console2.log('  "fundedTx": "",');
        console2.log('  "deployedAt":', block.timestamp, ",");
        console2.log('  "claimDeadline":', deadline == 0 ? "null" : deadline, ",");
        console2.log('  "owner": "', owner == address(0) ? "none" : vm.toString(owner), '",');
        console2.log('  "deployer": "', deployer, '",');
        console2.log('  "gitCommit": "', vm.envOr("GIT_COMMIT", string("unknown")), '"');
        console2.log("}");
    }
}
