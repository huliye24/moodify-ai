package com.moodify.app.data

import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Before
import org.junit.Test
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket

/**
 * JVM fake server (plain ServerSocket) that speaks just enough HTTP for
 * MoodifyApiClient tests — no Android runtime needed.
 */
class FakeHttpServer {
    val serverSocket = ServerSocket()
    var handler: (request: String) -> Pair<Int, String> = { _ -> 404 to "{}" }
    val port: Int

    init {
        serverSocket.reuseAddress = true
        serverSocket.bind(InetSocketAddress("127.0.0.1", 0))
        port = serverSocket.localPort
    }

    fun start() {
        thread("fake-http") {
            while (!serverSocket.isClosed) {
                val socket = try { serverSocket.accept() } catch (_: Exception) { return@thread }
                handle(socket)
            }
        }
    }

    private fun handle(socket: Socket) {
        try {
            socket.use { s ->
                val reader = BufferedReader(InputStreamReader(s.getInputStream(), Charsets.UTF_8))
                val requestLine = reader.readLine() ?: return
                val body = StringBuilder()
                var contentLength = 0
                while (true) {
                    val line = reader.readLine() ?: break
                    if (line.isEmpty()) break
                    if (line.lowercase().startsWith("content-length:")) {
                        contentLength = line.substringAfter(":").trim().toInt()
                    }
                }
                if (contentLength > 0) {
                    val buf = CharArray(contentLength)
                    var read = 0
                    while (read < contentLength) {
                        val n = reader.read(buf, read, contentLength - read)
                        if (n < 0) break
                        read += n
                    }
                    body.append(buf, 0, read)
                }
                val (status, response) = handler(requestLine + "\n" + body)
                val bytes = response.toByteArray(Charsets.UTF_8)
                val out = s.getOutputStream()
                out.write(
                    ("HTTP/1.1 $status OK\r\nContent-Type: application/json\r\n" +
                        "Content-Length: ${bytes.size}\r\nConnection: close\r\n\r\n").toByteArray(Charsets.UTF_8)
                )
                out.write(bytes)
                out.flush()
            }
        } catch (_: Exception) {
            // test-only server; connection teardown is expected
        }
    }

    fun stop() {
        try { serverSocket.close() } catch (_: Exception) {}
    }

    private fun thread(name: String, block: () -> Unit) {
        Thread(block, name).apply { isDaemon = true; start() }
    }
}

class MoodifyApiClientTest {

    private lateinit var server: FakeHttpServer

    private fun client(connectTimeoutMs: Int = 5000, readTimeoutMs: Int = 10000) =
        MoodifyApiClient(
            baseUrlProvider = { "http://127.0.0.1:${server.port}" },
            connectTimeoutMs = connectTimeoutMs,
            readTimeoutMs = readTimeoutMs,
        )

    @Before
    fun setUp() {
        server = FakeHttpServer()
        server.start()
    }

    @After
    fun tearDown() {
        server.stop()
    }

    private fun respond(status: Int, body: String) {
        server.handler = { _ -> status to body }
    }

    @Test
    fun healthParses() {
        respond(200, """{"status":"ok","api_version":"0.1.0","min_client_version":"0.1.0","mode":"mobile-v1","server_time":"2026-08-02T12:00:00"}""")
        val health = client().health()
        assertEquals("0.1.0", health.apiVersion)
        assertEquals("mobile-v1", health.mode)
    }

    @Test
    fun pairParsesAndSendsDevice() {
        var received = ""
        server.handler = { request ->
            received = request
            200 to """{"token":"abc123","token_id":"tid-1","api_version":"0.1.0"}"""
        }
        val result = client().pair("android-uuid", "Xiaomi 10")
        assertEquals("abc123", result.token)
        assertEquals("tid-1", result.tokenId)
        assertTrue(received.contains("device_id"))
        assertTrue(received.contains("device_name"))
    }

    @Test
    fun unauthorizedClassified() {
        respond(401, """{"error":{"code":"UNAUTHORIZED","message":"missing bearer token","request_id":"r1"}}""")
        try {
            client().revoke("bad-token")
            fail("expected Unauthorized")
        } catch (e: ConnectionError.Unauthorized) {
            assertEquals("UNAUTHORIZED", e.code)
        }
    }

    @Test
    fun notImplementedClassified() {
        respond(501, """{"error":{"code":"NOT_IMPLEMENTED","message":"later","request_id":"r2"}}""")
        try {
            client().pair("d", "n")
            fail("expected NotImplemented")
        } catch (e: ConnectionError.NotImplemented) {
            assertEquals("NOT_IMPLEMENTED", e.code)
        }
    }

    @Test
    fun offlineClassifiedWhenNothingListening() {
        val dead = FakeHttpServer().also { it.stop() }
        val deadClient = MoodifyApiClient(
            baseUrlProvider = { "http://127.0.0.1:${dead.port}" },
            connectTimeoutMs = 2000,
            readTimeoutMs = 2000,
        )
        try {
            deadClient.health()
            fail("expected Offline")
        } catch (e: ConnectionError.Offline) {
            assertEquals("OFFLINE", e.code)
        }
    }

    @Test
    fun timeoutClassifiedWhenServerSlow() {
        server.handler = { _ ->
            Thread.sleep(3000)
            200 to "{}"
        }
        val slow = MoodifyApiClient(
            baseUrlProvider = { "http://127.0.0.1:${server.port}" },
            connectTimeoutMs = 1000,
            readTimeoutMs = 1000,
        )
        try {
            slow.health()
            fail("expected Timeout")
        } catch (e: ConnectionError.Timeout) {
            assertEquals("TIMEOUT", e.code)
        }
    }

    @Test
    fun serverErrorClassifiedWithoutTracebackLeak() {
        respond(500, """{"error":{"code":"SERVER_ERROR","message":"boom","request_id":"r3"}}""")
        try {
            client().health()
            fail("expected ServerError")
        } catch (e: ConnectionError.ServerError) {
            assertTrue(!e.message.orEmpty().contains("Traceback"))
        }
    }

    @Test
    fun errorBodyParsed() {
        val parsed = MoodifyApiClient.parseErrorBody(
            """{"error":{"code":"VALIDATION","message":"device_id is required","request_id":"r4"}}"""
        )
        assertEquals("VALIDATION", parsed?.code)
        assertEquals("r4", parsed?.requestId)
    }

    @Test
    fun capabilitiesParsed() {
        respond(200, """{"api_version":"0.1.0","endpoints":{"health":"live"},"presets":["auto","clean_master"],"max_upload_bytes":52428800,"auth":"bearer-token","server_time":"2026-08-02T12:00:00"}""")
        val caps = client().capabilities()
        assertEquals("0.1.0", caps.apiVersion)
        assertEquals(2, caps.presets.size)
        assertEquals(52428800L, caps.maxUploadBytes)
    }
}
