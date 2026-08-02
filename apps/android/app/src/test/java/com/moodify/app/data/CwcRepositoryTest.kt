package com.moodify.app.data

import com.moodify.app.model.CwcValidationState
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CwcRepositoryTest {

    private fun repo(): CwcRepository {
        // Pure-logic tests: validation/normalize do not touch Android prefs.
        return CwcRepository(android.app.Application())
    }

    @Test
    fun normalizeFormatsRawAndPastedInput() {
        val repo = repo()
        assertEquals("CWC-XZ7M-42KP", repo.normalize("CWCXZ7M42KP"))
        assertEquals("CWC-XZ7M-42KP", repo.normalize("CWC-XZ7M-42KP"))
        assertEquals("CWC-XZ7M-42KP", repo.normalize("  cwc-xz7m-42kp "))
        assertEquals("CWC-XZ7M-42KP", repo.normalize("CWC XZ7M 42KP"))
        assertEquals("CWC-XZ7M-42KP", repo.normalize("cwc.xz7m.42kp"))
    }

    @Test
    fun validateAvailableCode() = runBlocking {
        val result = repo().validate("CWC-XZ7M-42KP")
        assertTrue(result is CwcValidationState.Valid)
        assertEquals("CWC-XZ7M-42KP", (result as CwcValidationState.Valid).pass.code)
    }

    @Test
    fun validateRedeemedCode() = runBlocking {
        val result = repo().validate("CWC-USED-0001")
        assertTrue(result is CwcValidationState.Error)
    }

    @Test
    fun validateExpiredCode() = runBlocking {
        val result = repo().validate("CWC-OLD0-0001")
        assertTrue(result is CwcValidationState.Error)
    }

    @Test
    fun validateUnknownCode() = runBlocking {
        val result = repo().validate("CWC-AAAA-0001")
        assertTrue(result is CwcValidationState.Error)
    }
}
