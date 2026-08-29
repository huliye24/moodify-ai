package com.moodify.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import com.moodify.app.ui.components.MoodifyMark

@Composable
fun LaunchScreen() {
    Box(Modifier.fillMaxSize().background(Color.Black)) {
        Box(
            Modifier
                .align(Alignment.Center)
                .padding(bottom = 92.dp)
                .size(340.dp, 310.dp)
                .background(
                    Brush.radialGradient(
                        listOf(Color(0x241C84FF), Color(0x16102A72), Color.Transparent),
                        center = Offset.Unspecified,
                        radius = 430f,
                    )
                ),
            contentAlignment = Alignment.Center,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                MoodifyMark(Modifier.size(270.dp, 182.dp))
                Text(
                    "好听的音乐，由 AI 创作",
                    color = Color.White,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 22.dp),
                )
            }
        }
        Column(
            Modifier.align(Alignment.BottomCenter).padding(bottom = 54.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("Moodify Music", color = Color.White, fontSize = 20.sp, letterSpacing = .8.sp)
            Text("音乐播放器", color = Color(0xFF969696), fontSize = 13.sp, modifier = Modifier.padding(top = 7.dp))
        }
    }
}
