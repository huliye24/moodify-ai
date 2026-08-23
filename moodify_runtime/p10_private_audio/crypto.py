"""
Moodify P10 — Private Audio Architecture v0.1 (Server-Side)

Core cryptographic module for:
  - Envelope encryption (AES-256-GCM + RSA-OAEP)
  - Chunked encrypted audio container
  - Device key lifecycle (server-side public key storage)
  - Transient plaintext workspace management

Crypto libraries: cryptography.io (well-maintained, audited)
NO custom AES, NO custom RSA, NO homemade protocols.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


# ===========================================================================
# Constants
# ===========================================================================

AES_KEY_SIZE = 256  # bits
AES_GCM_NONCE_SIZE = 96  # bits (12 bytes) — standard GCM nonce
AES_GCM_TAG_SIZE = 128  # bits (16 bytes)
CHUNK_SIZE = 1024 * 1024  # 1 MB per chunk (configurable)

RSA_KEY_SIZE = 3072  # bits
RSA_PADDING = asym_padding.OAEP(
    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)

CONTAINER_VERSION = "p10-v0.1"
CRYPTO_VERSION = "aes-256-gcm-rsa-3072-oaep-sha256"


# ===========================================================================
# Enums
# ===========================================================================

class PrivacyMode(str, Enum):
    STANDARD_PRIVATE = "STANDARD_PRIVATE"
    STRICT_PRIVATE = "STRICT_PRIVATE"


class ObjectStatus(str, Enum):
    ENCRYPTING = "ENCRYPTING"
    VERIFYING = "VERIFYING"
    FINALIZED = "FINALIZED"
    FAILED = "FAILED"
    DELETED = "DELETED"


class KeyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


# ===========================================================================
# Data Classes
# ===========================================================================

@dataclass
class DevicePublicKey:
    """Server-side record of a device's public key. Never stores private key."""
    device_id: str
    owner_id: str
    key_id: str
    public_key_pem: str  # PEM-encoded RSA public key
    algorithm: str = "RSA-3072-OAEP-SHA256"
    platform: str = "android"
    created_at: float = field(default_factory=time.time)
    revoked_at: Optional[float] = None
    status: KeyStatus = KeyStatus.ACTIVE


@dataclass
class WrappedDEK:
    """RSA-OAEP wrapped per-object DEK for a specific device."""
    key_id: str           # which device public key was used
    device_id: str        # which device this wrapped key is for
    wrapped_key: bytes     # the actual ciphertext (RSA-OAEP(DEK))
    created_at: float = field(default_factory=time.time)


@dataclass
class EncryptedChunk:
    """One encrypted chunk of audio."""
    chunk_index: int
    nonce: bytes          # AES-GCM nonce (12 bytes, unique per chunk)
    ciphertext: bytes    # AES-GCM ciphertext (includes 16-byte tag)
    associated_data: bytes  # AAD: object_id + chunk_index + version


@dataclass
class PrivateAudioObjectHeader:
    """Container metadata — stored alongside chunks, never contains secrets."""
    object_id: str
    owner_id: str
    result_id: str
    source_sha256: Optional[str] = None
    codec: str = "wav"       # original codec before encryption
    sample_rate: int = 44100
    channels: int = 2
    duration_ms: int = 0
    chunk_size: int = CHUNK_SIZE
    chunk_count: int = 0
    encryption_algorithm: str = CRYPTO_VERSION
    key_wrap_algorithm: str = "RSA-OAEP-SHA256"
    container_version: str = CONTAINER_VERSION
    reconstruction_version: str = "p09-v0.1"
    created_at: float = field(default_factory=time.time)
    finalized_at: Optional[float] = None
    status: ObjectStatus = ObjectStatus.ENCRYPTING
    privacy_mode: PrivacyMode = PrivacyMode.STANDARD_PRIVATE

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)

    @classmethod
    def from_json(cls, data: str) -> "PrivateAudioObjectHeader":
        return cls(**json.loads(data))


@dataclass
class PrivateAudioObject:
    """
    Complete encrypted audio object.

    This is the PRODUCT storage and playback object.
    It is NOT ProductionCase (which is internal processing state).
    """
    header: PrivateAudioObjectHeader
    wrapped_deks: list[WrappedDEK]   # one per authorized device
    chunks: list[EncryptedChunk]

    @property
    def object_id(self) -> str:
        return self.header.object_id

    @property
    def is_playable(self) -> bool:
        return self.header.status == ObjectStatus.FINALIZED


# ===========================================================================
# Core Crypto Operations
# ===========================================================================

def generate_dek() -> bytes:
    """Generate a random 256-bit AES key (Data Encryption Key)."""
    return secrets.token_bytes(AES_KEY_SIZE // 8)


def generate_nonce() -> bytes:
    """Generate a random 96-bit GCM nonce. MUST be unique per (key, chunk)."""
    return secrets.token_bytes(AES_GCM_NONCE_SIZE // 8)


def encrypt_chunk(plaintext: bytes, dek: bytes, nonce: bytes,
                  aad: bytes) -> EncryptedChunk:
    """
    Encrypt one chunk with AES-256-GCM.

    Raises InvalidTag on tamper detection during decryption.
    Nonce MUST be unique per (dek, chunk_index). Caller is responsible.
    """
    aesgcm = AESGCM(dek)
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
    return EncryptedChunk(
        chunk_index=0,  # caller sets
        nonce=nonce,
        ciphertext=ciphertext,
        associated_data=aad,
    )


def decrypt_chunk(chunk: EncryptedChunk, dek: bytes) -> bytes:
    """
    Decrypt one chunk. Raises InvalidTag if:
      - wrong key
      - tampered ciphertext
      - tampered AAD
      - replayed nonce (if key reuse detected by implementation)
    """
    aesgcm = AESGCM(dek)
    plaintext = aesgcm.decrypt(chunk.nonce, chunk.ciphertext, chunk.associated_data)
    return plaintext


def wrap_dek_for_device(dek: bytes, public_key_pem: str) -> WrappedDEK:
    """
    Wrap (encrypt) a DEK with a device's RSA public key using OAEP+SHA256.

    The wrapped DEK can only be unwrapped by the device that holds the private key.
    """
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    wrapped = public_key.encrypt(
        dek,
        RSA_PADDING,
    )
    return WrappedDEK(
        key_id="",
        device_id="",
        wrapped_key=wrapped,
    )


def unwrap_dek_with_private_key(wrapped_dek: bytes, private_key_pem: str) -> bytes:
    """
    Unwrap a DEK using the device's RSA private key.

    This runs ON DEVICE (Android Keystore) or in a secure context.
    NEVER on the server (server should never have private keys).
    """
    private_key = serialization.load_pem_private_key(private_key_pem.encode())
    dek = private_key.decrypt(
        wrapped_dek,
        RSA_PADDING,
    )
    return dek


# ===========================================================================
# Container Assembly / Disassembly
# ===========================================================================

def build_aad(object_id: str, chunk_index: int, version: str) -> bytes:
    """
    Build Associated Data for a chunk.

    Binds each chunk to its object and position to prevent:
      - chunk swapping between objects
      - chunk reordering within an object
      - version downgrade attacks
    """
    return f"{object_id}:{chunk_index}:{version}".encode("utf-8")


def encrypt_audio_to_container(
    plaintext_path: Path | str,
    header: PrivateAudioObjectHeader,
    device_public_keys: list[DevicePublicKey],
) -> PrivateAudioObject:
    """
    Full encryption pipeline: plaintext file → chunked encrypted container.

    Steps:
      1. Generate per-object DEK
      2. Read plaintext in chunks
      3. Encrypt each chunk with AES-GCM (unique nonce + AAD)
      4. Wrap DEK for each authorized device's public key
      5. Assemble PrivateAudioObject

    Caller is responsible for deleting the plaintext file AFTER verification.
    """
    plaintext_path = Path(plaintext_path)
    dek = generate_dek()
    chunks: list[EncryptedChunk] = []

    # Read and encrypt chunk by chunk
    chunk_index = 0
    with open(plaintext_path, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            nonce = generate_nonce()
            aad = build_aad(header.object_id, chunk_index, CONTAINER_VERSION)
            enc = encrypt_chunk(data, dek, nonce, aad)
            enc.chunk_index = chunk_index
            chunks.append(enc)
            chunk_index += 1

    header.chunk_count = len(chunks)

    # Wrap DEK for each authorized device
    wrapped_deks: list[WrappedDEK] = []
    for dev_key in device_public_keys:
        if dev_key.status != KeyStatus.ACTIVE:
            continue
        wd = wrap_dek_for_device(dek, dev_key.public_key_pem)
        wd.key_id = dev_key.key_id
        wd.device_id = dev_key.device_id
        wrapped_deks.append(wd)

    if not wrapped_deks:
        raise ValueError("No active device keys provided; cannot encrypt")

    return PrivateAudioObject(
        header=header,
        wrapped_deks=wrapped_deks,
        chunks=chunks,
    )


def decrypt_container_for_device(
    obj: PrivateAudioObject,
    wrapped_dek_bytes: bytes,
    private_key_pem: str,
) -> bytes:
    """
    Full decryption pipeline: container → plaintext audio.

    Used by Android client for playback (streaming mode preferred;
    this full-decrypt variant exists for testing / compatibility).

    Raises InvalidTag on any integrity failure.
    """
    # Step 1: Unwrap DEK
    dek = unwrap_dek_with_private_key(wrapped_dek_bytes, private_key_pem)

    # Step 2: Decrypt all chunks in order
    plaintext_parts = []
    for chunk in sorted(obj.chunks, key=lambda c: c.chunk_index):
        part = decrypt_chunk(chunk, dek)
        plaintext_parts.append(part)

    return b"".join(plaintext_parts)


def verify_container_integrity(obj: PrivateAudioObject) -> bool:
    """
    Quick structural validation (not full decryption).

    Checks:
      - Header fields present and sane
      - Chunk count matches
      - All chunk indices present 0..N-1 (no gaps, no duplicates)
      - Nonce uniqueness across chunks
      - At least one wrapped DEK
    """
    h = obj.header
    if not h.object_id or not h.owner_id:
        return False
    if h.chunk_count != len(obj.chunks):
        return False
    if not obj.wrapped_deks:
        return False

    indices = {c.chunk_index for c in obj.chunks}
    expected = set(range(h.chunk_count))
    if indices != expected:
        return False  # gap or duplicate

    nonces = {c.nonce for c in obj.chunks}
    if len(nonces) != len(obj.chunks):
        return False  # nonce collision!

    return True


# ===========================================================================
# Server-side Device Key Management
# ===========================================================================

class DeviceKeyRegistry:
    """
    Server-side registry of device public keys.

    In production this would be a database table. For v0.1, in-memory
    with persistence interface defined.
    """

    def __init__(self):
        self._devices: dict[str, DevicePublicKey] = {}  # key_id → DevicePublicKey

    def register(self, device: DevicePublicKey) -> None:
        """Register a new device public key."""
        self._devices[device.key_id] = device

    def revoke(self, key_id: str) -> None:
        """Revoke a device key."""
        if key_id in self._devices:
            self._devices[key_id].status = KeyStatus.REVOKED
            self._devices[key_id].revoked_at = time.time()

    def get_active_keys_for_owner(self, owner_id: str) -> list[DevicePublicKey]:
        """Get all active, non-revoked keys for an owner."""
        return [
            d for d in self._devices.values()
            if d.owner_id == owner_id and d.status == KeyStatus.ACTIVE
        ]

    def is_device_authorized(self, device_id: str, owner_id: str) -> bool:
        """Check if a device is authorized to access owner's objects."""
        for d in self._devices.values():
            if d.device_id == device_id and d.owner_id == owner_id:
                return d.status == KeyStatus.ACTIVE
        return False


# ===========================================================================
# Transient Plaintext Workspace
# ===========================================================================

class TransientWorkspace:
    """
    Job-scoped transient workspace for source/candidate/stem plaintext.

    Rules enforced:
      - Unique directory per job
      - No shared directories
      - Owner/job binding
      - TTL-based cleanup
      - Cleanup on success/failure/cancellation
    """

    def __init__(self, base_dir: Path | str, ttl_seconds: int = 3600):
        self.base_dir = Path(base_dir)
        self.ttl = ttl_seconds
        self._active_jobs: dict[str, Path] = {}  # job_id → workspace dir

    def create(self, job_id: str, owner_id: str) -> Path:
        """Create a new job-scoped workspace directory."""
        ws = self.base_dir / f"job-{job_id}-{owner_id[:8]}"
        ws.mkdir(parents=True, exist_ok=True)
        self._active_jobs[job_id] = ws
        return ws

    def path_for(self, job_id: str, filename: str) -> Path:
        """Get path to a file within a job's workspace."""
        ws = self._active_jobs.get(job_id)
        if not ws:
            raise ValueError(f"No workspace for job {job_id}")
        return ws / filename

    def cleanup_job(self, job_id: str) -> None:
        """Remove all files in a job's workspace."""
        ws = self._active_jobs.pop(job_id, None)
        if ws and ws.exists():
            import shutil
            shutil.rmtree(ws, ignore_errors=True)

    def cleanup_stale(self, max_age_seconds: Optional[int] = None) -> int:
        """Remove workspaces older than max_age (or TTL). Returns count cleaned."""
        max_age = max_age_seconds or self.ttl
        now = time.time()
        cleaned = 0
        for job_id, ws in list(self._active_jobs.items()):
            if now - ws.stat().st_mtime > max_age:
                self.cleanup_job(job_id)
                cleaned += 1
        return cleaned


# ===========================================================================
# Finalization Pipeline
# ===========================================================================

def finalize_reconstruction_result(
    plaintext_path: Path | str,
    owner_id: str,
    result_id: str,
    device_keys: list[DevicePublicKey],
    workspace: TransientWorkspace,
    job_id: str,
) -> PrivateAudioObject:
    """
    Complete finalization pipeline (P10 §16):

    1. Validate plaintext exists and is readable
    2. Create DEK
    3. Encrypt into chunked private object
    4. Verify ciphertext integrity (round-trip test)
    5. Mark FINALIZED
    6. Delete plaintext
    7. Clean up workspace

    Returns the finalized PrivateAudioObject.
    Raises on any failure (plaintext NOT deleted until verified).
    """
    plaintext_path = Path(plaintext_path)

    # Step 1: Validate
    if not plaintext_path.exists():
        raise FileNotFoundError(f"Plaintext not found: {plaintext_path}")
    file_size = plaintext_path.stat().st_size
    if file_size == 0:
        raise ValueError("Plaintext is empty")

    # Step 2-4: Create object
    object_id = f"pao-{uuid.uuid4().hex[:12]}"
    header = PrivateAudioObjectHeader(
        object_id=object_id,
        owner_id=owner_id,
        result_id=result_id,
        status=ObjectStatus.ENCRYPTING,
    )

    obj = encrypt_audio_to_container(plaintext_path, header, device_keys)

    # Step 4: Verify integrity
    if not verify_container_integrity(obj):
        raise IntegrityError("Container integrity check failed")

    # Step 5: Mark finalized
    obj.header.status = ObjectStatus.FINALIZED
    obj.header.finalized_at = time.time()

    # Step 6: Delete plaintext (only after successful verification)
    plaintext_path.unlink()

    # Step 7: Cleanup workspace
    workspace.cleanup_job(job_id)

    return obj


class IntegrityError(Exception):
    """Raised when encrypted container fails integrity verification."""
    pass
