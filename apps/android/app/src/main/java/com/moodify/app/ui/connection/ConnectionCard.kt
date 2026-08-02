package com.moodify.app.ui.connection

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CloudDone
import androidx.compose.material.icons.outlined.CloudOff
import androidx.compose.material.icons.outlined.Link
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.moodify.app.data.ConnectionError
import com.moodify.app.data.ConnectionState
import com.moodify.app.ui.theme.*

/** Connect / pair / revoke card for the "我的" tab (ANDROID-003 Stage B/D). */
@Composable
fun ConnectionCard(viewModel: ConnectionViewModel = viewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val paired by viewModel.paired.collectAsStateWithLifecycle()
    val baseUrl by viewModel.baseUrl.collectAsStateWithLifecycle()

    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(4.dp),
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("电脑端连接", Modifier.weight(1f), color = MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                ConnectionBadge(state, paired)
            }
            Spacer(Modifier.height(6.dp))
            Text(
                baseUrl,
                color = MoodifyMuted,
                fontSize = 11.sp,
            )
            Spacer(Modifier.height(10.dp))
            when (state) {
                is ConnectionState.Connected -> {
                    Text("已连接 · API v${(state as ConnectionState.Connected).health.apiVersion} · 模式 ${(state as ConnectionState.Connected).health.mode}", color = MoodifyGreen, fontSize = 12.sp)
                    Spacer(Modifier.height(10.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (!paired) {
                            Button(onClick = { viewModel.pair() }, modifier = Modifier.weight(1f), colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(16.dp)) {
                                Icon(Icons.Outlined.Lock, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(6.dp)); Text("配对")
                            }
                        } else {
                            OutlinedButton(onClick = { viewModel.revoke() }, modifier = Modifier.weight(1f), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline), shape = RoundedCornerShape(16.dp)) {
                                Text("撤销配对", color = MoodifyMuted)
                            }
                        }
                        OutlinedButton(onClick = { viewModel.connect() }, modifier = Modifier.weight(1f), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline), shape = RoundedCornerShape(16.dp)) {
                            Icon(Icons.Outlined.Refresh, null, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(6.dp)); Text("重连", color = MoodifyMuted)
                        }
                    }
                }
                is ConnectionState.Connecting -> {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = MoodifyBlue)
                        Spacer(Modifier.width(10.dp))
                        Text("正在连接…", color = MoodifyMuted, fontSize = 13.sp)
                    }
                }
                is ConnectionState.Error -> {
                    val err = (state as ConnectionState.Error).error
                    Text(err.message ?: "连接失败", color = Color(0xFFE05B5B), fontSize = 12.sp)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = { viewModel.connect() }, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(16.dp)) {
                        Text("重新连接")
                    }
                    if (err is ConnectionError.NotImplemented) {
                        Text("该功能尚在开发（ANDROID-004/005 实现）", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp))
                    }
                }
                else -> {
                    Button(onClick = { viewModel.connect() }, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(16.dp)) {
                        Text("连接电脑端")
                    }
                    Text("需要先在电脑端启动 Moodify API 服务", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp))
                }
            }
        }
    }
}

@Composable
private fun ConnectionBadge(state: ConnectionState, paired: Boolean) {
    val (bg, tint, label) = when (state) {
        is ConnectionState.Connected -> Triple(Color(0xFFE8F8EE), Color(0xFF31A35E), "已连接")
        is ConnectionState.Error -> Triple(Color(0xFFFFE9EA), Color(0xFFE05B5B), "连接失败")
        is ConnectionState.Connecting -> Triple(Color(0xFFE9F0FF), MoodifyBlue, "连接中")
        else -> Triple(Color(0xFFF1F3F8), MoodifyMuted, "未连接")
    }
    Surface(color = bg, shape = RoundedCornerShape(10.dp)) {
        Row(Modifier.padding(horizontal = 9.dp, vertical = 5.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(
                when (state) {
                    is ConnectionState.Connected -> Icons.Outlined.CloudDone
                    is ConnectionState.Error -> Icons.Outlined.CloudOff
                    else -> Icons.Outlined.Link
                },
                null,
                tint = tint,
                modifier = Modifier.size(14.dp),
            )
            Spacer(Modifier.width(4.dp))
            Text(label, color = tint, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}
