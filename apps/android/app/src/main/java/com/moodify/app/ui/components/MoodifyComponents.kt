package com.moodify.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.MoodifyBlue
import com.moodify.app.ui.theme.MoodifyGradient
import com.moodify.app.ui.theme.MoodifyPurple

@Composable
fun MoodifyMark(modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val points = listOf(
            Offset(size.width * .04f, size.height * .53f),
            Offset(size.width * .18f, size.height * .53f),
            Offset(size.width * .27f, size.height * .25f),
            Offset(size.width * .38f, size.height * .78f),
            Offset(size.width * .5f, size.height * .12f),
            Offset(size.width * .62f, size.height * .73f),
            Offset(size.width * .73f, size.height * .35f),
            Offset(size.width * .82f, size.height * .53f),
            Offset(size.width * .96f, size.height * .53f),
        )
        for (i in 0 until points.lastIndex) {
            drawLine(
                brush = MoodifyGradient,
                start = points[i],
                end = points[i + 1],
                strokeWidth = 3.2.dp.toPx(),
                cap = StrokeCap.Round,
            )
        }
    }
}

@Composable
fun GradientButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().height(52.dp),
        colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(),
        shape = RoundedCornerShape(26.dp),
    ) {
        Box(
            Modifier.fillMaxWidth().height(52.dp).background(MoodifyGradient, RoundedCornerShape(26.dp)),
            contentAlignment = Alignment.Center,
        ) {
            Text(text, color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
fun ProgressRing(progress: Float, modifier: Modifier = Modifier) {
    Canvas(modifier) {
        drawArc(Color(0xFFE6EAF4), 0f, 360f, false, style = Stroke(2.5.dp.toPx(), cap = StrokeCap.Round))
        drawArc(
            brush = androidx.compose.ui.graphics.Brush.sweepGradient(listOf(MoodifyBlue, MoodifyPurple)),
            startAngle = -90f,
            sweepAngle = 360f * progress,
            useCenter = false,
            style = Stroke(2.5.dp.toPx(), cap = StrokeCap.Round),
        )
    }
}
