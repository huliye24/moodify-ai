package com.moodify.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.*

@Composable
fun DataCenterScreen(onBack: () -> Unit) {
    var range by remember { mutableIntStateOf(1) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(12.dp)); Row(verticalAlignment = Alignment.CenterVertically) { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回") }; Text("数据中心", Modifier.weight(1f), color = MoodifyNavy, fontSize = 22.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center); IconButton(onClick = {}) { Icon(Icons.Outlined.CalendarMonth, "日期") } }
        Spacer(Modifier.height(12.dp)); ProfileRange(range) { range = it }; Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { Metric(Icons.Outlined.PlayCircle, "总播放量", "128.6万", "↑ 18.6%", Modifier.weight(1f)); Metric(Icons.Outlined.Group, "新增粉丝", "1,284", "↑ 12.4%", Modifier.weight(1f)); Metric(Icons.Outlined.FavoriteBorder, "点赞数", "24.7K", "↑ 16.2%", Modifier.weight(1f)); Metric(Icons.Outlined.ChatBubbleOutline, "评论数", "3,426", "↑ 8.7%", Modifier.weight(1f)) }
        Spacer(Modifier.height(13.dp)); TrendCard(); Spacer(Modifier.height(13.dp)); Audience(); Spacer(Modifier.height(13.dp)); PopularTable(); Spacer(Modifier.height(13.dp)); Interaction(); Spacer(Modifier.height(13.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { BottomAction(Icons.Outlined.Description, "导出报表", "下载数据报告", Modifier.weight(1f)); BottomAction(Icons.Outlined.BarChart, "作品分析", "深度解析作品表现", Modifier.weight(1f)); BottomAction(Icons.Outlined.Group, "粉丝增长", "粉丝趋势与来源", Modifier.weight(1f)) }
        Spacer(Modifier.height(22.dp))
    }
}

@Composable private fun ProfileRange(selected: Int, change: (Int) -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(56.dp).background(Color(0xFFD3CCFF), CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = MoodifyNavy, modifier = Modifier.size(38.dp)) }; Column(Modifier.padding(start = 12.dp).weight(1f)) { Text("泫榛  ✦", color = MoodifyNavy, fontSize = 18.sp, fontWeight = FontWeight.Bold); Text("近 30 天表现总览", color = MoodifyMuted, fontSize = 10.sp) }; Row(Modifier.background(Color(0xFFF5F6FA), RoundedCornerShape(16.dp))) { listOf("7天","30天","90天").forEachIndexed { i, text -> Surface(onClick = { change(i) }, color = if(selected==i) MoodifyPurple else Color.Transparent, shape = RoundedCornerShape(13.dp)) { Text(text, color = if(selected==i) Color.White else MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 13.dp, vertical = 8.dp)) } } } } } }
@Composable private fun Metric(icon: ImageVector, label: String, value: String, change: String, modifier: Modifier) { Card(modifier, shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Column(Modifier.padding(11.dp)) { Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(21.dp)); Text(label, color = MoodifyMuted, fontSize = 8.sp, modifier = Modifier.padding(top = 6.dp)); Text(value, color = MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold); Text("较上期  $change", color = MoodifyGreen, fontSize = 7.sp) } } }
@Composable private fun TrendCard() { Section("播放趋势") { Text("较上期  ↑ 18.6%", color = MoodifyGreen, fontSize = 9.sp); Spacer(Modifier.height(8.dp)); LineChart(Modifier.fillMaxWidth().height(150.dp)) } }
@Composable private fun LineChart(modifier: Modifier) { Canvas(modifier) { repeat(4){i->val y=size.height*i/4;drawLine(MoodifyOutline,Offset(0f,y),Offset(size.width,y),1f)};val vs=listOf(.15f,.2f,.28f,.62f,.45f,.7f,.38f,.4f,.12f,.35f,.3f,.76f,.29f,.68f,.35f,.58f,.4f,.62f,.55f,.82f);val p=Path();vs.forEachIndexed{i,v->val o=Offset(size.width*i/(vs.size-1),size.height*(1-v));if(i==0)p.moveTo(o.x,o.y)else p.lineTo(o.x,o.y);drawCircle(MoodifyPurple,2.5.dp.toPx(),o)};drawPath(p,MoodifyPurple,style=androidx.compose.ui.graphics.drawscope.Stroke(2.dp.toPx(),cap=StrokeCap.Round)) } }
@Composable private fun Audience() { Section("受众画像") { Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) { Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) { Text("听众来源", color = MoodifyNavy, fontSize = 11.sp); Donut(Modifier.size(112.dp)); Text("推荐 62.4%  ·  搜索 18.7%", color = MoodifyMuted, fontSize = 8.sp) }; Column(Modifier.weight(1f)) { Text("听众地区 Top 4", color = MoodifyNavy, fontSize = 11.sp); Region("深圳",.78f,"24.3%");Region("上海",.61f,"18.7%");Region("北京",.48f,"14.5%");Region("广州",.34f,"9.8%") } } } }
@Composable private fun Donut(modifier: Modifier) { Canvas(modifier) { drawArc(MoodifyOutline,-90f,360f,false,style=androidx.compose.ui.graphics.drawscope.Stroke(16.dp.toPx()));drawArc(MoodifyPurple,-90f,225f,false,style=androidx.compose.ui.graphics.drawscope.Stroke(16.dp.toPx()));drawArc(MoodifyGreen,135f,67f,false,style=androidx.compose.ui.graphics.drawscope.Stroke(16.dp.toPx()));drawArc(MoodifyOrange,202f,43f,false,style=androidx.compose.ui.graphics.drawscope.Stroke(16.dp.toPx())) } }
@Composable private fun Region(city: String, progress: Float, percent: String) { Row(Modifier.padding(top = 10.dp), verticalAlignment = Alignment.CenterVertically) { Text(city, color = MoodifyMuted, fontSize = 9.sp, modifier = Modifier.width(34.dp)); LinearProgressIndicator(progress={progress},modifier=Modifier.weight(1f).height(6.dp),color=MoodifyPurple,trackColor=MoodifyOutline);Text(percent,color=MoodifyMuted,fontSize=8.sp,modifier=Modifier.padding(start=6.dp)) } }
@Composable private fun PopularTable() { Section("热门作品") { HeaderRow(); TrackRow("Dreamscape","32.4万","6,342","48.7%",Color(0xFF5630B8)); HorizontalDivider(color=MoodifyOutline);TrackRow("Sunset Drive","21.8万","4,521","46.2%",Color(0xFFFF8351));HorizontalDivider(color=MoodifyOutline);TrackRow("Midnight Walk","15.6万","2,981","42.9%",Color(0xFF269B84)) } }
@Composable private fun HeaderRow() { Row(Modifier.fillMaxWidth().background(Color(0xFFF5F6FA),RoundedCornerShape(7.dp)).padding(7.dp)) { Text("作品",Modifier.weight(1.5f),color=MoodifyMuted,fontSize=8.sp);Text("播放量",Modifier.weight(1f),color=MoodifyMuted,fontSize=8.sp);Text("点赞数",Modifier.weight(1f),color=MoodifyMuted,fontSize=8.sp);Text("完播率",Modifier.weight(.7f),color=MoodifyMuted,fontSize=8.sp) } }
@Composable private fun TrackRow(name:String,plays:String,likes:String,rate:String,color:Color){Row(Modifier.padding(vertical=8.dp),verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(35.dp).background(color,RoundedCornerShape(6.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.PlayArrow,null,tint=Color.White,modifier=Modifier.size(17.dp))};Text(name,Modifier.padding(start=8.dp).weight(1.2f),color=MoodifyNavy,fontSize=10.sp);Text(plays,Modifier.weight(.8f),color=MoodifyNavy,fontSize=9.sp);Text(likes,Modifier.weight(.8f),color=MoodifyNavy,fontSize=9.sp);Text(rate,Modifier.weight(.6f),color=MoodifyPurple,fontSize=9.sp)} }
@Composable private fun Interaction(){Section("互动表现"){Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){MiniMetric(Icons.Outlined.StarBorder,"收藏率","8.7%",Modifier.weight(1f));MiniMetric(Icons.Outlined.Share,"分享率","5.3%",Modifier.weight(1f));MiniMetric(Icons.Outlined.PlayCircle,"完播率","46.2%",Modifier.weight(1f))}}}
@Composable private fun MiniMetric(icon:ImageVector,label:String,value:String,modifier:Modifier){OutlinedCard(modifier,shape=RoundedCornerShape(13.dp)){Column(Modifier.padding(11.dp)){Icon(icon,null,tint=MoodifyPurple);Text(label,color=MoodifyMuted,fontSize=9.sp);Text(value,color=MoodifyNavy,fontSize=16.sp,fontWeight=FontWeight.Bold);Text("较上期 ↑ 9.8%",color=MoodifyGreen,fontSize=7.sp)}}}
@Composable private fun BottomAction(icon:ImageVector,title:String,sub:String,modifier:Modifier){Card(onClick={},modifier=modifier,shape=RoundedCornerShape(13.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Row(Modifier.padding(10.dp)){Icon(icon,null,tint=MoodifyPurple);Column(Modifier.padding(start=7.dp)){Text(title,color=MoodifyNavy,fontSize=10.sp,fontWeight=FontWeight.Bold);Text(sub,color=MoodifyMuted,fontSize=7.sp)}}}}
@Composable private fun Section(title:String,content:@Composable ColumnScope.()->Unit){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White),elevation=CardDefaults.cardElevation(3.dp)){Column(Modifier.padding(13.dp)){Text(title,color=MoodifyNavy,fontSize=17.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(8.dp));content()}}}
