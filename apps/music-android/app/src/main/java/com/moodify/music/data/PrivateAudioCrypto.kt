package com.moodify.music.data

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.security.KeyStore
import java.util.UUID
import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * P10 Private Audio — Android-side decryption and device key management.
 *
 * Responsibilities:
 *  - Generate RSA-3072 keypair in Android Keystore (non-exportable)
 *  - Export public key PEM for server registration
 *  - Unwrap per-object DEK using Keystore private key
 *  - Decrypt AES-GCM chunks for streaming playback
 *  - No plaintext cache; streaming-only decryption
 */
object PrivateAudioCrypto {

    private const val KEY_ALIAS = "MoodifyDeviceKey"
    private const val KEYSTORE_TYPE = "AndroidKeyStore"
    private const val RSA_KEY_SIZE = 3072
    private const val RSA_PADDING_OAEP = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding"
    private const val AES_GCM = "AES/GCM/NoPadding"
    private const val GCM_IV_SIZE = 12   // 96 bits
    private const val GCM_TAG_SIZE = 16 // 128 bits

    // =========================================================================
    // Device Key Lifecycle
    // =========================================================================

    /**
     * Ensure the Moodify device RSA keypair exists in Android Keystore.
     * Generates a new one if not present. Non-exportable on TEE-capable devices.
     *
     * @return the key ID (alias-based, stable across app restarts)
     */
    fun ensureDeviceKeyExists(): String {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        ks.load(null)

        if (!ks.containsAlias(KEY_ALIAS)) {
            generateRsaKeypair(ks)
        }
        return KEY_ALIAS
    }

    /**
     * Get the public key in PEM format for server registration.
     *
     * The private key NEVER leaves Keystore. This PEM is safe to transmit.
     */
    fun getPublicKeyPem(): String {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        ks.load(null)
        val cert = ks.getCertificate(KEY_ALIAS)
            ?: throw IllegalStateException("Device key not found")
        val publicKey = cert.publicKey

        // Build PEM manually (no external dependency needed)
        val encoded = publicKey.encoded
        val base64 = android.util.Base64.encodeToString(encoded, android.util.Base64.NO_WRAP)
        val lines = base64.chunked(64).joinToString("\n")
        return "-----BEGIN PUBLIC KEY-----\n$lines\n-----END PUBLIC KEY-----"
    }

    /**
     * Revoke (delete) the device key from Keystore.
     * After this, all encrypted objects wrapped for this key become unrecoverable.
     */
    fun revokeDeviceKey() {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        ks.load(null)
        ks.deleteEntry(KEY_ALIAS)
    }

    /**
     * Check if device key exists.
     */
    fun hasDeviceKey(): Boolean {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        ks.load(null)
        return ks.containsAlias(KEY_ALIAS)
    }

    // =========================================================================
    // DEK Unwrap (RSA-OAEP decrypt with Keystore private key)
    // =========================================================================

    /**
     * Unwrap a DEK using the device's Keystore private key.
     *
     * The wrapped DEK was encrypted server-side with this device's public key.
     * Only the Keystore private key can decrypt it.
     *
     * @param wrappedDek RSA-OAEP ciphertext of the AES key
     * @return raw AES-256 key bytes (keep in memory only, never persist)
     */
    fun unwrapDek(wrappedDek: ByteArray): ByteArray {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        ks.load(null)
        val privateKey = ks.getKey(KEY_ALIAS, null)
            as? java.security.interfaces.RSAPrivateKey
            ?: throw IllegalStateException("No RSA private key in Keystore")

        val cipher = Cipher.getInstance(RSA_PADDING_OAEP)
        cipher.init(Cipher.DECRYPT_MODE, privateKey)
        return cipher.doFinal(wrappedDek)
    }

    // =========================================================================
    // Chunk Decryption (AES-GCM)
    // =========================================================================

    /**
     * Decrypt a single chunk using AES-256-GCM.
     *
     * @param dek the unwrapped Data Encryption Key (from unwrapDek)
     * @param nonce 12-byte unique nonce for this chunk
     * @param ciphertext includes 16-byte GCM tag at the end
     * @param aad associated data (object_id:chunk_index:version)
     * @return decrypted plaintext bytes
     * @throws javax.crypto.AEADBadTagException if tampered/wrong key/replayed
     */
    fun decryptChunk(
        dek: ByteArray,
        nonce: ByteArray,
        ciphertext: ByteArray,
        aad: ByteArray,
    ): ByteArray {
        require(nonce.size == GCM_IV_SIZE) { "Nonce must be $GCM_IV_SIZE bytes" }

        val secretKey = SecretKeySpec(dek, "AES")
        val spec = GCMParameterSpec(GCM_TAG_SIZE * 8, nonce)
        val cipher = Cipher.getInstance(AES_GCM)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
        if (aad.isNotEmpty()) {
            cipher.updateAAD(aad)
        }
        return cipher.doFinal(ciphertext)
    }

    // =========================================================================
    // Streaming Decryptor (for Media3 DataSource)
    // =========================================================================

    /**
     * Streaming chunk decryptor state machine.
     *
     * Maintains position within the logical plaintext stream,
     * decrypting chunks on demand as ExoPlayer reads bytes.
     *
     * Usage:
     *   1. Create with DEK + total chunk count
     *   2. Call seek(position) to set read position
     *   3. call read(buffer, offset, length) to get decrypted bytes
     *   4. Chunks are fetched via [chunkFetcher] callback
     */
    class StreamingDecryptor(
        private val dek: ByteArray,
        private val totalChunkCount: Int,
        private val objectId: String,
        private val chunkFetcher: (chunkIndex: Int) -> EncryptedChunkData?,
    ) {
        var currentChunkIndex = -1
        var currentPlaintext: ByteArray? = null
        var positionInChunk = 0
        var globalPosition = 0L

        data class EncryptedChunkData(
            val nonce: ByteArray,
            val ciphertext: ByteArray,
            val aad: ByteArray,
        )

        fun seek(position: Long) {
            globalPosition = position.coerceIn(0L, Long.MAX_VALUE)
            // Determine which chunk we're in (requires knowing chunk sizes;
            // simplified: assume fixed CHUNK_SIZE except last)
            // Full implementation would need a chunk index table from header
            currentChunkIndex = -1  // force re-fetch
            currentPlaintext = null
            positionInChunk = 0
        }

        fun read(buffer: ByteArray, offset: Int, length: Int): Int {
            if (currentPlaintext == null || positionInChunk >= currentPlaintext!!.size) {
                loadNextChunk()
                if (currentPlaintext == null) return -1  // EOF
                positionInChunk = 0
            }

            val available = currentPlaintext!!.size - positionInChunk
            val toRead = minOf(length, available)
            System.arraycopy(currentPlaintext!!, positionInChunk, buffer, offset, toRead)
            positionInChunk += toRead
            globalPosition += toRead
            return toRead
        }

        private fun loadNextChunk() {
            val nextIndex = currentChunkIndex + 1
            if (nextIndex >= totalChunkCount) {
                currentPlaintext = null
                return
            }

            val chunk = chunkFetcher(nextIndex)
            if (chunk == null) {
                currentPlaintext = null
                return
            }

            currentPlaintext = try {
                decryptChunk(dek, chunk.nonce, chunk.ciphertext, chunk.aad)
            } catch (e: Exception) {
                null  // integrity failure → treat as EOF
            }
            currentChunkIndex = nextIndex
        }
    }

    // =========================================================================
    // Internal helpers
    // =========================================================================

    private fun generateRsaKeypair(ks: KeyStore) {
        val generator = java.security.KeyPairGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_RSA, KEYSTORE_TYPE
        )
        val spec = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_DECRYPT)
            .setKeySize(RSA_KEY_SIZE)
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setRandomizedEncryptionRequired(true)
            // Require user authentication on API 23+ if hardware supports it
            .setUserAuthenticationRequired(false)  // v0.1: optional for convenience
            .build()
        generator.initialize(spec)
        generator.generateKeyPair()
    }

}
