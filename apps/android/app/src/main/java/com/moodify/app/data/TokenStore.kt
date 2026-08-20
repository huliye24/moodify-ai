package com.moodify.app.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Pair token storage backed by Android Keystore (AES/GCM).
 *
 * The token never leaves the device in plaintext: only the ciphertext lives
 * in SharedPreferences; the key is hardware-backed by the Keystore.
 */
class TokenStore(context: Context) {

    private val prefs = context.getSharedPreferences("moodify_pair", Context.MODE_PRIVATE)
    private val alias = "moodify_pair_token_key"

    private fun key(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (keyStore.getKey(alias, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                alias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()
        )
        return generator.generateKey()
    }

    fun save(token: String, tokenId: String) {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val encrypted = cipher.doFinal(token.toByteArray(Charsets.UTF_8))
        val iv = cipher.iv
        prefs.edit()
            .putString("token_iv", Base64.encodeToString(iv, Base64.NO_WRAP))
            .putString("token_ct", Base64.encodeToString(encrypted, Base64.NO_WRAP))
            .putString("token_id", tokenId)
            .apply()
    }

    fun token(): String? {
        val iv = prefs.getString("token_iv", null) ?: return null
        val ct = prefs.getString("token_ct", null) ?: return null
        return try {
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(
                Cipher.DECRYPT_MODE,
                key(),
                GCMParameterSpec(128, Base64.decode(iv, Base64.NO_WRAP)),
            )
            String(cipher.doFinal(Base64.decode(ct, Base64.NO_WRAP)), Charsets.UTF_8)
        } catch (_: Exception) {
            clear()
            null
        }
    }

    fun tokenId(): String? = prefs.getString("token_id", null)

    fun clear() {
        prefs.edit().clear().apply()
    }
}
