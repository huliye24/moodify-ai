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
        setContent {
            MoodifyTheme {
                MoodifyApp()
            }
        }
    }
}

