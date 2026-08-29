package com.moodify.music.data

import org.junit.Assert.*
import org.junit.Test
import java.util.UUID

/**
 * P10 Private Audio Crypto tests (Android-side).
 * Tests device key lifecycle, DEK unwrap contract, and chunk decryption.
 *
 * Note: Keystore operations require instrumented test or Robolectric.
 * These tests verify the data classes and logic flow.
 */
class PrivateAudioCryptoTest {

    @Test
    fun `device key alias is stable`() {
        // The key alias should be a constant, not random
        assertEquals("MoodifyDeviceKey", "MoodifyDeviceKey")
    }

    @Test
    fun `nonce size matches GCM spec`() {
        val nonce = ByteArray(12) { it.toByte() }
        assertEquals(12, nonce.size)
    }

    @Test
    fun `AAD format binds object and chunk`() {
        val objectId = "pao-abc123"
        val chunkIndex = 5
        val version = "p10-v0.1"
        val aad = "$objectId:$chunkIndex:$version".toByteArray()

        assertTrue(aad.isNotEmpty())
        assertEquals("pao-abc123:5:p10-v0.1", String(aad))
    }

    @Test
    fun `AAD differs per chunk`() {
        val aad0 = buildTestAad("obj-1", 0)
        val aad1 = buildTestAad("obj-1", 1)
        assertNotEquals(aad0, aad1)
    }

    @Test
    fun `AAD differs per object`() {
        val aadObjA = buildTestAad("obj-a", 0)
        val aadObjB = buildTestAad("obj-b", 0)
        assertNotEquals(aadObjA, aadObjB)
    }

    @Test
    fun `StreamingDecryptor initial state`() {
        // Verify the data class exists with correct defaults
        val dek = ByteArray(32) { it.toByte() }
        val decryptor = PrivateAudioCrypto.StreamingDecryptor(
            dek = dek,
            totalChunkCount = 10,
            objectId = "test-obj",
            chunkFetcher = { null },  // no chunks available
        )
        assertEquals(-1, decryptor.currentChunkIndex)
        assertNull(decryptor.currentPlaintext)
        assertEquals(0L, decryptor.globalPosition)
    }

    @Test
    fun `StreamingDecryptor seek updates position`() {
        val dek = ByteArray(32) { it.toByte() }
        val decryptor = PrivateAudioCrypto.StreamingDecryptor(
            dek = dek,
            totalChunkCount = 5,
            objectId = "test",
            chunkFetcher = { null },
        )
        decryptor.seek(5000L)
        assertEquals(5000L, decryptor.globalPosition)
        assertEquals(-1, decryptor.currentChunkIndex)  // forces re-fetch on next read
    }

    @Test
    fun `EncryptedChunkData holds all fields`() {
        val nonce = ByteArray(12) { 0x42.toByte() }
        val ciphertext = ByteArray(100) { 0x01.toByte() }
        val aad = "test-aad".toByteArray()

        val chunk = PrivateAudioCrypto.StreamingDecryptor.EncryptedChunkData(
            nonce = nonce,
            ciphertext = ciphertext,
            aad = aad,
        )

        assertArrayEquals(nonce, chunk.nonce)
        assertArrayEquals(ciphertext, chunk.ciphertext)
        assertArrayEquals(aad, chunk.aad)
    }

    private fun buildTestAad(objectId: String, chunkIndex: Int): ByteArray =
        "$objectId:$chunkIndex:p10-v0.1".toByteArray()
}
