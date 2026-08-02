package com.moodify.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.moodify.app.ui.MoodifyApp
import com.moodify.app.ui.theme.MoodifyTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val deepLinkCode = parseDeepLink(intent?.dataString)
        setContent {
            MoodifyTheme {
                MoodifyApp(pendingCwcCode = deepLinkCode)
            }
        }
    }

    /** Deep link reserved: moodify://cwc/CWC-XZ7M-42KP → gift landing page. */
    private fun parseDeepLink(data: String?): String? {
        if (data == null || !data.startsWith("moodify://cwc/")) return null
        return data.removePrefix("moodify://cwc/")
    }
}

