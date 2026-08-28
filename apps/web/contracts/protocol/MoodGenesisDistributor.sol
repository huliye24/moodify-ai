// SPDX-License-Identifier: GPL-3.0-only
pragma solidity ^0.8.20;

/**
 * @title MoodGenesisDistributor
 * @notice Genesis MOOD token distribution via Merkle proofs
 * @dev Immutable root, single claim per participant, SafeERC20 transfers
 *
 * MOOD-GENESIS-005: Merkle Airdrop
 *
 * Security invariants:
 * - Only approved Merkle leaves can claim
 * - Each approved allocation can be claimed exactly once
 * - Claim amount cannot be changed by claimant
 * - Claim wallet cannot be redirected (msg.sender must match)
 * - Root cannot be changed after deployment
 * - Contract cannot mint MOOD
 * - Claimant never needs to approve MOOD
 */

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract MoodGenesisDistributor {
    using SafeERC20 for IERC20;

    /* ========== ERRORS ========== */

    error AlreadyClaimed(uint256 participantNumber);
    error InvalidProof();
    error ZeroAddress();
    error ZeroRoot();
    error ZeroAmount();
    error DeadlinePassed();
    error DeadlineNotPassed();
    error UnauthorizedRecovery();
    error InsufficientBalance();

    /* ========== EVENTS ========== */

    event Claimed(
        uint256 indexed participantNumber,
        address indexed account,
        uint256 amount
    );

    event UnclaimedRecovered(
        address indexed recipient,
        uint256 amount
    );

    /* ========== STATE ========== */

    /// @notice MOOD token contract
    IERC20 public immutable token;

    /// @notice Approved Merkle root from Package 004
    bytes32 public immutable merkleRoot;

    /// @notice Optional claim deadline (0 = no deadline)
    uint256 public immutable claimDeadline;

    /// @notice Owner authorized for recovery (address(0) = no recovery)
    address public immutable owner;

    /// @notice Tracks claimed participants
    mapping(uint256 => bool) public claimedParticipant;

    /// @notice Total MOOD claimed so far
    uint256 public totalClaimed;

    /* ========== CONSTRUCTOR ========== */

    /**
     * @param _token MOOD token contract address
     * @param _merkleRoot Approved Merkle root from Package 004
     * @param _claimDeadline Optional deadline (0 for no deadline)
     * @param _owner Optional owner for recovery (address(0) for no recovery)
     */
    constructor(
        address _token,
        bytes32 _merkleRoot,
        uint256 _claimDeadline,
        address _owner
    ) {
        if (_token == address(0)) revert ZeroAddress();
        if (_merkleRoot == bytes32(0)) revert ZeroRoot();
        if (_claimDeadline > 0 && _claimDeadline <= block.timestamp) {
            // Deadline must be in the future if set
            revert DeadlinePassed();
        }

        token = IERC20(_token);
        merkleRoot = _merkleRoot;
        claimDeadline = _claimDeadline;
        owner = _owner;
    }

    /* ========== CLAIM ========== */

    /**
     * @notice Claim approved MOOD allocation
     * @param participantNumber Genesis participant number
     * @param amount Approved allocation in atomic units
     * @param proof Merkle proof from Package 004
     *
     * Requirements:
     * - msg.sender must match the approved wallet
     * - Proof must be valid for participantNumber + msg.sender + amount
     * - Participant must not have claimed before
     * - Must be before deadline (if set)
     * - Contract must have sufficient MOOD balance
     */
    function claim(
        uint256 participantNumber,
        uint256 amount,
        bytes32[] calldata proof
    ) external {
        // 1. Check deadline
        if (claimDeadline > 0 && block.timestamp > claimDeadline) {
            revert DeadlinePassed();
        }

        // 2. Check not already claimed
        if (claimedParticipant[participantNumber]) {
            revert AlreadyClaimed(participantNumber);
        }

        // 3. Validate amount
        if (amount == 0) revert ZeroAmount();

        // 4. Construct and verify leaf
        // Leaf encoding matches Package 004: [uint256, address, uint256]
        bytes32 leaf = keccak256(
            abi.encode(participantNumber, msg.sender, amount)
        );

        if (!_verifyProof(leaf, proof)) {
            revert InvalidProof();
        }

        // 5. Mark claimed BEFORE transfer (checks-effects-interactions)
        claimedParticipant[participantNumber] = true;
        totalClaimed += amount;

        // 6. Transfer MOOD (SafeERC20 handles failures)
        token.safeTransfer(msg.sender, amount);

        // 7. Emit event
        emit Claimed(participantNumber, msg.sender, amount);
    }

    /* ========== RECOVERY ========== */

    /**
     * @notice Recover unclaimed MOOD after deadline
     * @param recipient Address to receive recovered tokens
     *
     * Requirements:
     * - Only callable by owner
     * - Only callable after deadline
     * - Only available if owner was set in constructor
     */
    function recoverUnclaimed(address recipient) external {
        if (owner == address(0)) revert UnauthorizedRecovery();
        if (msg.sender != owner) revert UnauthorizedRecovery();
        if (claimDeadline == 0) revert UnauthorizedRecovery();
        if (block.timestamp <= claimDeadline) revert DeadlineNotPassed();

        uint256 balance = token.balanceOf(address(this));
        if (balance == 0) revert InsufficientBalance();

        token.safeTransfer(recipient, balance);

        emit UnclaimedRecovered(recipient, balance);
    }

    /* ========== VIEW FUNCTIONS ========== */

    /**
     * @notice Check if a participant has claimed
     */
    function hasClaimed(uint256 participantNumber) external view returns (bool) {
        return claimedParticipant[participantNumber];
    }

    /**
     * @notice Get contract MOOD balance
     */
    function distributorBalance() external view returns (uint256) {
        return token.balanceOf(address(this));
    }

    /**
     * @notice Get remaining claimable amount
     */
    function remainingClaimable() external view returns (uint256) {
        return token.balanceOf(address(this)) - totalClaimed;
    }

    /* ========== INTERNAL FUNCTIONS ========== */

    /**
     * @notice Verify a Merkle proof
     * @param leaf Leaf hash to verify
     * @param proof Merkle proof
     * @return True if proof is valid
     */
    function _verifyProof(
        bytes32 leaf,
        bytes32[] calldata proof
    ) internal view returns (bool) {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            // Sort for deterministic ordering (OpenZeppelin convention)
            if (computedHash <= proofElement) {
                computedHash = keccak256(
                    abi.encodePacked(computedHash, proofElement)
                );
            } else {
                computedHash = keccak256(
                    abi.encodePacked(proofElement, computedHash)
                );
            }
        }

        return computedHash == merkleRoot;
    }
}
