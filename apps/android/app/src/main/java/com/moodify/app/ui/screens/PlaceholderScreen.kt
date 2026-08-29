package com.moodify.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.MoodifyMuted
import com.moodify.app.ui.theme.MoodifyNavy

@Composable
fun PlaceholderScreen(title: String, description: String) {
    Column(
        Modifier.fillMaxSize().padding(28.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(title, color = MoodifyNavy, fontSize = 24.sp, fontWeight = FontWeight.Bold)
        Text(description, color = MoodifyMuted, fontSize = 14.sp, modifier = Modifier.padding(top = 8.dp))
    }
}

