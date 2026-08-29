// SPDX-License-Identifier: GPL-3.0-only
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {MoodGenesisDistributor} from "../protocol/MoodGenesisDistributor.sol";

/**
 * @title DeployLocal
 * @notice Local deployment for testing
 *
 * Usage:
 *   forge script contracts/script/DeployLocal.s.sol --rpc-url local --broadcast
 */

contract DeployLocal is Script {
    // Mock token for local testing
    address public constant MOCK_TOKEN = address(0x123);

    // Test merkle root (replace with actual Package 004 root for real deployment)
    bytes32 public constant TEST_ROOT = keccak256("test");

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("LOCAL_PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console2.log("Deploying MoodGenesisDistributor (Local)...");
        console2.log("Deployer:", deployer);

        vm.startBroadcast(deployerPrivateKey);

        MoodGenesisDistributor distributor = new MoodGenesisDistributor(
            MOCK_TOKEN,
            TEST_ROOT,
            0, // no deadline
            address(0) // no owner
        );

        vm.stopBroadcast();

        console2.log("Deployed to:", address(distributor));
        console2.log("Token:", address(distributor.token()));
        console2.log("Merkle Root:");
        console2.logBytes32(distributor.merkleRoot());
    }
}
