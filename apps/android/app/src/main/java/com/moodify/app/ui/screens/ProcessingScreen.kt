package com.moodify.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.PhoneAndroid
import androidx.compose.material.icons.outlined.Tune
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.ProgressRing
import com.moodify.app.ui.theme.MoodifyBlue
import com.moodify.app.ui.theme.MoodifyMuted
import com.moodify.app.ui.theme.MoodifyNavy
import com.moodify.app.ui.theme.MoodifyOutline

@Composable
fun ProcessingScreen(onBackHome: () -> Unit) {
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("音乐处理", fontSize = 21.sp, fontWeight = FontWeight.Bold, color = MoodifyNavy)
        Text("阶段 1 为界面演示，尚未启动真实 DSP", fontSize = 12.sp, color = MoodifyMuted)
        Spacer(Modifier.height(18.dp))
        SurfaceCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(76.dp).background(Color(0xFFF0F3FA), RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) {
                    Icon(Icons.Outlined.MusicNote, null, tint = Color(0xFF98A5C4), modifier = Modifier.size(42.dp))
                }
                Column(Modifier.padding(start = 16.dp).weight(1f)) {
                    Text("AI Demo Track", fontSize = 17.sp, fontWeight = FontWeight.SemiBold, color = MoodifyNavy)
                    Text("03:24 · 演示音频", color = MoodifyMuted, fontSize = 13.sp)
                    Spacer(Modifier.height(10.dp))
                    Waveform(Modifier.fillMaxWidth().height(24.dp))
                }
            }
        }
        Spacer(Modifier.height(14.dp))
        SurfaceCard {
            Row(verticalAlignment = Alignment.Bottom) {
                Text("处理中", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = MoodifyNavy)
                Text(" 68%", fontSize = 18.sp, color = MoodifyNavy)
            }
            Spacer(Modifier.height(12.dp))
            LinearProgressIndicator(
                progress = { .68f },
                modifier = Modifier.fillMaxWidth().height(5.dp),
                color = MoodifyBlue,
                trackColor = Color(0xFFE8ECF5),
                strokeCap = StrokeCap.Round,
            )
            Spacer(Modifier.height(10.dp))
            Text("正在构建可试听版本…", color = MoodifyMuted, fontSize = 13.sp)
        }
        Spacer(Modifier.height(14.dp))
        SurfaceCard {
            ProcessingStep(Icons.Outlined.GraphicEq, "响度标准化", StepState.Complete)
            ProcessingStep(Icons.Outlined.GraphicEq, "True Peak 控制", StepState.Complete)
            ProcessingStep(Icons.Outlined.Tune, "频段平衡", StepState.Active)
            ProcessingStep(Icons.Outlined.PhoneAndroid, "平台适配", StepState.Pending, showDivider = false)
        }
        Spacer(Modifier.height(20.dp))
        GradientButton("完成处理并查看结果", onBackHome)
        Spacer(Modifier.height(12.dp))
        Text("处理完成后将自动保存到作品", color = MoodifyBlue, fontSize = 13.sp)
    }
}

private enum class StepState { Complete, Active, Pending }

@Composable
private fun ProcessingStep(icon: ImageVector, title: String, state: StepState, showDivider: Boolean = true) {
    Column {
        Row(Modifier.fillMaxWidth().height(52.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null, tint = MoodifyMuted, modifier = Modifier.size(22.dp))
            Text(title, Modifier.padding(start = 14.dp).weight(1f), color = MoodifyMuted, fontSize = 14.sp)
            when (state) {
                StepState.Complete -> Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyBlue, modifier = Modifier.size(22.dp))
                StepState.Active -> ProgressRing(.72f, Modifier.size(22.dp))
                StepState.Pending -> ProgressRing(0f, Modifier.size(22.dp))
            }
        }
        if (showDivider) Box(Modifier.fillMaxWidth().height(1.dp).background(MoodifyOutline))
    }
}

@Composable
private fun SurfaceCard(content: @Composable ColumnScope.() -> Unit) {
    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline),
    ) { Column(Modifier.padding(18.dp), content = content) }
}

@Composable
private fun Waveform(modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val heights = listOf(.18f,.36f,.58f,.25f,.7f,.42f,.3f,.65f,.82f,.38f,.28f,.55f,.74f,.33f,.47f,.22f,.61f,.36f,.76f,.31f,.5f,.24f,.64f,.44f,.2f,.38f,.57f,.29f,.48f,.18f)
        val gap = size.width / heights.size
        heights.forEachIndexed { index, value ->
            val x = gap * index + gap / 2
            val half = size.height * value / 2
            drawLine(Color(0xFFCBD3E7), Offset(x, size.height / 2 - half), Offset(x, size.height / 2 + half), 1.4.dp.toPx(), StrokeCap.Round)
        }
    }
}
