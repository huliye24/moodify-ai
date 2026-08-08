package com.moodify.app.i18n

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import javax.xml.parsers.DocumentBuilderFactory

/**
 * Enforces the DSK-MFY-I18N-001 parity contract: all six strings.xml files must
 * have identical key sets, and every value must match the reference package's
 * locale catalogs (test/resources/i18n snapshots), modulo interpolation syntax
 * ({{name}} -> %1$s) and the app_name special case.
 */
class StringKeyParityTest {

    private val moduleRoot = File(System.getProperty("user.dir"))
    private val resDir = File(moduleRoot, "src/main/res")
    private val snapshotDir = File(moduleRoot, "src/test/resources/i18n")

    private val locales = listOf(
        "values" to "en-US",
        "values-zh-rCN" to "zh-CN",
        "values-zh-rTW" to "zh-TW",
        "values-ja" to "ja-JP",
        "values-ko" to "ko-KR",
        "values-fr" to "fr-FR",
    )

    @Test
    fun allSixXmlFilesHaveIdenticalKeySets() {
        val keySets = locales.map { (dir, _) -> readXmlStrings(File(resDir, dir)).keys }
        val reference = keySets.first()
        keySets.forEachIndexed { i, keys ->
            assertEquals("key set of ${locales[i].first}", reference.sorted(), keys.sorted())
        }
    }

    @Test
    fun everyXmlContainsTheReferenceSnapshotKeys() {
        locales.forEach { (dir, tag) ->
            val xml = readXmlStrings(File(resDir, dir))
            val snapshot = readSnapshot(tag)
            val snapshotKeys = snapshot.keys.map(::flattenKey).toSortedSet()
            assertTrue(
                "snapshot keys missing for $tag: ${snapshotKeys - xml.keys}",
                xml.keys.containsAll(snapshotKeys),
            )
        }
    }

    @Test
    fun everySnapshotValueMatchesItsXml() {
        locales.forEach { (dir, tag) ->
            val xml = readXmlStrings(File(resDir, dir))
            val snapshot = readSnapshot(tag)
            snapshot.forEach { (jsonKey, jsonValue) ->
                val xmlKey = flattenKey(jsonKey)
                val expected = convertInterpolation(jsonValue)
                val actual = xml[xmlKey]
                assertEquals("value of $jsonKey in $tag", expected, actual)
            }
        }
    }

    private fun readXmlStrings(dir: File): Map<String, String> {
        val file = File(dir, "strings.xml")
        assertTrue("missing $file", file.exists())
        val doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(file)
        val result = LinkedHashMap<String, String>()
        val nodes = doc.getElementsByTagName("string")
        for (i in 0 until nodes.length) {
            val el = nodes.item(i) as org.w3c.dom.Element
            result[el.getAttribute("name")] = el.textContent
        }
        return result
    }

    private fun readSnapshot(tag: String): Map<String, String> {
        val file = File(snapshotDir, "$tag.json")
        assertTrue("missing snapshot $file", file.exists())
        val root = JSONObject(file.readText())
        val result = LinkedHashMap<String, String>()
        val sections = root.keys()
        while (sections.hasNext()) {
            val section = sections.next()
            if (section == "meta") continue
            val body = root.getJSONObject(section)
            val keys = body.keys()
            while (keys.hasNext()) {
                val leaf = keys.next()
                result["$section.$leaf"] = body.getString(leaf)
            }
        }
        return result
    }

    private fun flattenKey(jsonKey: String): String = when (jsonKey) {
        "common.appName" -> "app_name"
        else -> jsonKey.replace('.', '_').camelToSnake()
    }

    private fun convertInterpolation(value: String): String =
        value.replace(Regex("""\{\{\s*[\w.-]+\s*\}\}"""), Regex.escapeReplacement("%1\$s"))

    private fun String.camelToSnake(): String =
        replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}
