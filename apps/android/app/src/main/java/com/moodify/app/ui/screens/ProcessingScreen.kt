package com.moodify.app.ui.screens

import android.net.Uri
import androidx.compose.foundation.background
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
import androidx.compose.material.icons.outlined.ErrorOutline
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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.data.BaseUrlStore
import com.moodify.app.data.ConnectionError
import com.moodify.app.data.DemoJobStatus
import com.moodify.app.data.DemoProcessRepository
import com.moodify.app.data.DemoResultSummary
import com.moodify.app.data.MoodifyApiClient
import com.moodify.app.data.TokenStore
import com.moodify.app.data.WorkLibrary
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.ProgressRing
import com.moodify.app.ui.theme.MoodifyBlue
import com.moodify.app.ui.theme.MoodifyMuted
import com.moodify.app.ui.theme.MoodifyNavy
import com.moodify.app.ui.theme.MoodifyOutline

private sealed interface DemoProcessState {
    data object Uploading : DemoProcessState
    data class Processing(val stage: String, val progress: Float) : DemoProcessState
    data class Done(val summary: DemoResultSummary) : DemoProcessState
    data class Failed(val message: String) : DemoProcessState
}

private data class StageStep(val key: String, val title: String, val icon: ImageVector)

private val stageSteps = listOf(
    StageStep("scan", "扫描音频", Icons.Outlined.MusicNote),
    StageStep("analyze", "特征分析", Icons.Outlined.GraphicEq),
    StageStep("diagnose", "智能诊断", Icons.Outlined.GraphicEq),
    StageStep("process", "DSP 处理", Icons.Outlined.Tune),
    StageStep("validate", "质量验证", Icons.Outlined.CheckCircle),
    StageStep("report", "报告生成", Icons.Outlined.CheckCircle),
    StageStep("generate", "交付打包", Icons.Outlined.PhoneAndroid),
)

private fun stageIndex(stage: String): Int = stageSteps.indexOfFirst { it.key == stage }

private fun stageLabel(stage: String): String = when (stage) {
    "scan" -> "正在扫描音频…"
    "analyze" -> "正在提取特征与频谱…"
    "diagnose" -> "正在诊断音质问题…"
    "process" -> "正在执行 DSP 处理…"
    "validate" -> "正在验证处理质量…"
    "report" -> "正在生成分析报告…"
    "generate" -> "正在打包交付产物…"
    "upload" -> "正在上传音频…"
    "done" -> "处理完成"
    else -> "处理中…"
}

@Composable
fun ProcessingScreen(uri: Uri?, onBackHome: () -> Unit, onDone: (DemoResultSummary) -> Unit) {
    val context = LocalContext.current
    val tokenStore = remember { TokenStore(context) }
    val baseUrlStore = remember { BaseUrlStore(context) }
    val repo = remember {
        DemoProcessRepository(
            client = MoodifyApiClient(baseUrlProvider = { baseUrlStore.baseUrl }),
            tokenProvider = { tokenStore.token() },
        )
    }
    val workLibrary = remember { WorkLibrary(context) }
    var state by remember { mutableStateOf<DemoProcessState>(DemoProcessState.Uploading) }
    var lastJob by remember { mutableStateOf<DemoJobStatus?>(null) }

    LaunchedEffect(uri) {
        if (uri == null) {
            state = DemoProcessState.Failed("未选择音频文件")
            return@LaunchedEffect
        }
        try {
            val (uploadId, filename) = repo.uploadFromUri(context, uri)
            val project = repo.startProject(filename, uploadId)
            val job = repo.pollJob(project.jobId) { status ->
                lastJob = status
                state = DemoProcessState.Processing(status.stage, status.progress)
            }
            when (job.status) {
                "done" -> {
                    val summary = repo.result(project.jobId)
                    workLibrary.add(summary)
                    state = DemoProcessState.Done(summary)
                }
                "failed" -> state = DemoProcessState.Failed(job.errorCode ?: "处理失败，请检查音频文件")
                else -> state = DemoProcessState.Failed("任务已取消")
            }
        } catch (e: ConnectionError) {
            state = DemoProcessState.Failed(e.message ?: "连接失败")
        } catch (e: Exception) {
            state = DemoProcessState.Failed(e.message ?: "发生错误")
        }
    }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("音乐处理", fontSize = 21.sp, fontWeight = FontWeight.Bold, color = MoodifyNavy)
        when (val s = state) {
            is DemoProcessState.Uploading -> {
                Text("正在上传音频…", fontSize = 12.sp, color = MoodifyMuted)
                Spacer(Modifier.height(18.dp))
                SurfaceCard {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(76.dp).background(Color(0xFFF0F3FA), RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) {
                            Icon(Icons.Outlined.MusicNote, null, tint = Color(0xFF98A5C4), modifier = Modifier.size(42.dp))
                        }
                        Column(Modifier.padding(start = 16.dp).weight(1f)) {
                            Text(fileName(uri), fontSize = 17.sp, fontWeight = FontWeight.SemiBold, color = MoodifyNavy)
                            Text("正在上传到电脑端…", color = MoodifyMuted, fontSize = 13.sp)
                            Spacer(Modifier.height(10.dp))
                            LinearProgressIndicator(progress = { 0.1f }, modifier = Modifier.fillMaxWidth().height(5.dp), color = MoodifyBlue, trackColor = Color(0xFFE8ECF5), strokeCap = StrokeCap.Round)
                        }
                    }
                }
                Spacer(Modifier.height(14.dp))
                SurfaceCard { Text("上传完成后将自动开始真实处理", color = MoodifyMuted, fontSize = 13.sp) }
            }
            is DemoProcessState.Processing -> {
                val progress = s.progress
                val idx = stageIndex(s.stage)
                Text(stageLabel(s.stage), fontSize = 12.sp, color = MoodifyMuted)
                Spacer(Modifier.height(18.dp))
                SurfaceCard {
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text("处理中", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = MoodifyNavy)
                        Text(" ${(progress * 100).toInt()}%", fontSize = 18.sp, color = MoodifyNavy)
                    }
                    Spacer(Modifier.height(12.dp))
                    LinearProgressIndicator(
                        progress = { progress },
                        modifier = Modifier.fillMaxWidth().height(5.dp),
                        color = MoodifyBlue,
                        trackColor = Color(0xFFE8ECF5),
                        strokeCap = StrokeCap.Round,
                    )
                    Spacer(Modifier.height(10.dp))
                    Text("正在由电脑端真实处理引擎执行…", color = MoodifyMuted, fontSize = 13.sp)
                }
                Spacer(Modifier.height(14.dp))
                SurfaceCard {
                    stageSteps.forEachIndexed { i, step ->
                        val stepState = when {
                            idx < 0 -> StepState.Pending
                            i < idx -> StepState.Complete
                            i == idx -> StepState.Active
                            else -> StepState.Pending
                        }
                        ProcessingStep(step.icon, step.title, stepState, showDivider = i < stageSteps.size - 1)
                    }
                }
                Spacer(Modifier.height(20.dp))
                Text("处理完成后将自动保存到作品", color = MoodifyBlue, fontSize = 13.sp)
            }
            is DemoProcessState.Done -> {
                Text("真实处理完成", fontSize = 12.sp, color = Color(0xFF31A35E))
                Spacer(Modifier.height(18.dp))
                SurfaceCard {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(76.dp).background(Color(0xFFE8F8EE), RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) {
                            Icon(Icons.Outlined.CheckCircle, null, tint = Color(0xFF31A35E), modifier = Modifier.size(42.dp))
                        }
                        Column(Modifier.padding(start = 16.dp).weight(1f)) {
                            Text(s.summary.filename, fontSize = 17.sp, fontWeight = FontWeight.SemiBold, color = MoodifyNavy)
                            Text("${s.summary.preset} · 已保存到作品库", color = MoodifyMuted, fontSize = 13.sp)
                            Spacer(Modifier.height(10.dp))
                            Text("MRS 质量分 ${fmt(s.summary.mrsBefore)} → ${fmt(s.summary.mrsAfter)} (Δ${fmt(s.summary.mrsDelta)})", color = MoodifyBlue, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                        }
                    }
                }
                Spacer(Modifier.height(14.dp))
                SurfaceCard {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyBlue, modifier = Modifier.size(22.dp))
                        Text("质量门：${if (s.summary.gatePassed) "通过" else "未通过"}", Modifier.padding(start = 12.dp), color = MoodifyNavy, fontSize = 14.sp)
                    }
                    if (s.summary.issues.isNotEmpty()) {
                        s.summary.issues.take(3).forEach { issue ->
                            Spacer(Modifier.height(6.dp))
                            Text("• $issue", color = MoodifyMuted, fontSize = 12.sp)
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
                val doneSummary = s.summary
                GradientButton("查看作品库", onClick = { onDone(doneSummary) })
            }
            is DemoProcessState.Failed -> {
                Text("处理失败", fontSize = 12.sp, color = Color(0xFFE05B5B))
                Spacer(Modifier.height(18.dp))
                SurfaceCard {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Outlined.ErrorOutline, null, tint = Color(0xFFE05B5B), modifier = Modifier.size(26.dp))
                        Text(s.message, Modifier.padding(start = 12.dp), color = MoodifyNavy, fontSize = 14.sp)
                    }
                }
                Spacer(Modifier.height(20.dp))
                GradientButton("返回", onBackHome)
            }
        }
    }
}

private fun fileName(uri: Uri?): String =
    uri?.lastPathSegment?.substringAfterLast('/')?.substringBefore('?') ?: "音频文件"

private fun fmt(v: Double?): String = if (v == null) "—" else "%.1f".format(v)

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

