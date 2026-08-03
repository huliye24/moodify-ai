package com.moodify.app.ui.screens

import android.net.Uri
import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.theme.*
import java.io.File

private data class PickedFile(val uri: Uri, val name: String, val sizeLabel: String)

/** Demo audio folder inside app-specific storage: files/demo/ */
fun demoAudioDir(context: android.content.Context): File =
    File(context.getExternalFilesDir(null), "demo").apply { mkdirs() }

private fun listDemoAudio(context: android.content.Context): List<File> =
    demoAudioDir(context).listFiles { f ->
        f.isFile && f.extension.lowercase() in setOf("wav", "mp3", "flac", "m4a", "aac")
    }?.sortedBy { it.name } ?: emptyList()

@Composable
fun UploadFlowScreen(startPage: Int = 0, onExit: () -> Unit, onProcess: (List<Uri>) -> Unit, onLibrary: () -> Unit) {
    val context = LocalContext.current
    var page by remember { mutableIntStateOf(startPage) }
    var selected by remember { mutableStateOf<List<Uri>>(emptyList()) }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
        if (uris.isNotEmpty()) { selected = uris; page = 2 }
    }
    val files = remember(selected) { selected.map { toPickedFile(context, it) } }
    val demoFiles = remember { listDemoAudio(context) }
    val pickDemo: (File) -> Unit = { file ->
        selected = listOf(Uri.fromFile(file)); page = 2
    }
    when (page) {
        0 -> UploadEntry(onExit, { picker.launch(arrayOf("audio/*")) }, { picker.launch(arrayOf("audio/*")) }, { picker.launch(arrayOf("audio/*")) }, { page = 2 }, demoFiles, pickDemo)
        1 -> WeChatImport({ page = 0 }, { picker.launch(arrayOf("audio/*")) })
        2 -> BatchUpload({ page = 0 }, files, { picker.launch(arrayOf("audio/*")) }, { if (files.isNotEmpty()) onProcess(files.map { it.uri }) }, onLibrary)
        else -> UploadEntry(onExit, { picker.launch(arrayOf("audio/*")) }, { picker.launch(arrayOf("audio/*")) }, { picker.launch(arrayOf("audio/*")) }, { page = 2 }, demoFiles, pickDemo)
    }
}

private fun toPickedFile(context: android.content.Context, uri: Uri): PickedFile {
    var name = "audio"
    var size = -1L
    context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
        val nameIdx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
        val sizeIdx = cursor.getColumnIndex(OpenableColumns.SIZE)
        if (cursor.moveToFirst()) {
            if (nameIdx >= 0) name = cursor.getString(nameIdx) ?: name
            if (sizeIdx >= 0 && !cursor.isNull(sizeIdx)) size = cursor.getLong(sizeIdx)
        }
    }
    val sizeLabel = when {
        size < 0 -> "未知大小"
        size >= 1024 * 1024 -> "%.1f MB".format(size / (1024.0 * 1024.0))
        else -> "%.0f KB".format(size / 1024.0)
    }
    return PickedFile(uri, name, sizeLabel)
}

@Composable private fun UploadEntry(back: () -> Unit, pick: () -> Unit, record: () -> Unit, cloud: () -> Unit, batch: () -> Unit, demoFiles: List<File>, pickDemo: (File) -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)) {
        Spacer(Modifier.height(12.dp));Header("上传音频",back,Icons.Outlined.HelpOutline);Spacer(Modifier.height(18.dp))
        OutlinedCard(onClick=pick,modifier=Modifier.fillMaxWidth().height(205.dp),shape=RoundedCornerShape(22.dp),border=androidx.compose.foundation.BorderStroke(1.5.dp,MoodifyPurple.copy(.5f))){Column(Modifier.fillMaxSize().background(Color(0xFFF9F8FF)),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Box(Modifier.size(66.dp).background(Brush.linearGradient(listOf(MoodifyPurple,MoodifyBlue)),RoundedCornerShape(18.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.FileUpload,null,tint=Color.White,modifier=Modifier.size(38.dp))};Text("选择音频文件",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold,modifier=Modifier.padding(top=18.dp));Text("支持 WAV / MP3 / FLAC / AAC / M4A，单个不超过 50MB",color=MoodifyMuted,fontSize=10.sp,modifier=Modifier.padding(top=9.dp))}}
        if (demoFiles.isNotEmpty()) {
            Spacer(Modifier.height(22.dp));Text("演示音频",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(9.dp))
            Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Column(Modifier.padding(horizontal=14.dp)){demoFiles.forEachIndexed{i,f->DemoAudioRow(f.name,"%.1f MB".format(f.length()/(1024.0*1024.0))){pickDemo(f)};if(i<demoFiles.size-1)HorizontalDivider(color=MoodifyOutline)}}}
            Spacer(Modifier.height(22.dp));Text("推荐来源",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(11.dp));Row(horizontalArrangement=Arrangement.spacedBy(9.dp)){Source(Icons.Outlined.Folder,"本地文件","从手机存储选择",Modifier.weight(1f),pick);Source(Icons.Outlined.Mic,"录音导入","直接录制高质量音频",Modifier.weight(1f),record);Source(Icons.Outlined.Cloud,"微信 / 云端","从微信或云盘导入",Modifier.weight(1f),cloud)}
        } else {
            Spacer(Modifier.height(24.dp));Text("推荐来源",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(11.dp));Row(horizontalArrangement=Arrangement.spacedBy(9.dp)){Source(Icons.Outlined.Folder,"本地文件","从手机存储选择",Modifier.weight(1f),pick);Source(Icons.Outlined.Mic,"录音导入","直接录制高质量音频",Modifier.weight(1f),record);Source(Icons.Outlined.Cloud,"微信 / 云端","从微信或云盘导入",Modifier.weight(1f),cloud)}
        }
        Spacer(Modifier.height(23.dp));Text("上传设置",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(9.dp));Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(17.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Setting(Icons.Outlined.Tune,"默认处理方式","标准处理");HorizontalDivider(color=MoodifyOutline);Setting(Icons.Outlined.Image,"自动生成封面","开启");HorizontalDivider(color=MoodifyOutline);Setting(Icons.Outlined.ArrowCircleRight,"上传后下一步","进入作品详情")}
        Spacer(Modifier.height(22.dp));Text("你将获得",color=MoodifyNavy,fontSize=18.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(9.dp));Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Benefit(Icons.Outlined.GraphicEq,"波形预览","可视化音频内容",Modifier.weight(1f));Benefit(Icons.Outlined.AudioFile,"格式识别","自动识别音频格式",Modifier.weight(1f));Benefit(Icons.Outlined.VerifiedUser,"版权归档支持","提供版权存证服务",Modifier.weight(1f))}
        Spacer(Modifier.height(20.dp));GradientButton("选择音频文件",pick);TextButton(onClick=batch){Text("批量上传",color=MoodifyPurple,modifier=Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.Center)};Spacer(Modifier.height(20.dp))
    }
}

@Composable private fun WeChatImport(back:()->Unit, import:()->Unit){
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)){Spacer(Modifier.height(12.dp));Header("从微信导入",back,Icons.Outlined.HelpOutline);Spacer(Modifier.height(15.dp));Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp),colors=CardDefaults.cardColors(containerColor=Color(0xFFF0FBF2))){Row(Modifier.padding(22.dp),verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text("快速导入微信传输的\n音频与工程文件",color=MoodifyNavy,fontSize=20.sp,fontWeight=FontWeight.Bold);Text("✓ 支持聊天文件\n✓ 支持微信收藏\n✓ 支持批量导入",color=Color(0xFF38B35B),fontSize=11.sp,lineHeight=25.sp,modifier=Modifier.padding(top=15.dp))};Icon(Icons.Outlined.Chat,null,tint=Color(0xFF42C85A),modifier=Modifier.size(86.dp))}}
        Spacer(Modifier.height(12.dp));Row(Modifier.fillMaxWidth().background(Color.White,RoundedCornerShape(14.dp))){listOf("最近接收","聊天文件","微信收藏").forEachIndexed{i,s->Surface(modifier=Modifier.weight(1f),color=if(i==0)Color(0xFFF0FBF2)else Color.Transparent,shape=RoundedCornerShape(13.dp)){Text(s,color=if(i==0)Color(0xFF32A852)else MoodifyMuted,textAlign=androidx.compose.ui.text.style.TextAlign.Center,modifier=Modifier.padding(12.dp))}}};Row(Modifier.padding(vertical=12.dp),horizontalArrangement=Arrangement.spacedBy(7.dp)){TagGreen("全部");FilterButton("仅显示音频");FilterButton("仅显示工程文件")}
        Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Column(Modifier.padding(16.dp),horizontalAlignment=Alignment.CenterHorizontally){Icon(Icons.Outlined.FolderOpen,null,tint=MoodifyPurple,modifier=Modifier.size(40.dp));Text("演示版请从系统文件选择器导入",color=MoodifyNavy,fontSize=14.sp,fontWeight=FontWeight.SemiBold,modifier=Modifier.padding(top=10.dp));Text("点击下方按钮打开微信收到的音频文件",color=MoodifyMuted,fontSize=11.sp,modifier=Modifier.padding(top=6.dp))}};Spacer(Modifier.height(16.dp));GradientButton("从文件选择器选择",import);TextButton(onClick=back){Text("返回上传入口",color=MoodifyPurple,modifier=Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.Center)};Spacer(Modifier.height(20.dp))}
}

@Composable private fun BatchUpload(back:()->Unit,files:List<PickedFile>,pick:()->Unit,start:()->Unit,library:()->Unit){Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)){Spacer(Modifier.height(12.dp));Header("批量上传",back,Icons.Outlined.FolderOpen);Spacer(Modifier.height(15.dp));Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp),colors=CardDefaults.cardColors(containerColor=Color(0xFFF3F1FF))){Row(Modifier.padding(20.dp),verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(54.dp).background(MoodifyPurple,RoundedCornerShape(14.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.FileCopy,null,tint=Color.White)};Column(Modifier.padding(start=14.dp)){Text("已选择 ${files.size} 个音频",color=MoodifyNavy,fontSize=20.sp,fontWeight=FontWeight.Bold);Text("处理第 1 个文件后将自动保存到作品库",color=MoodifyPurple,fontSize=13.sp,modifier=Modifier.padding(top=13.dp))}}};Spacer(Modifier.height(14.dp));if(files.isEmpty()){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Column(Modifier.padding(20.dp),horizontalAlignment=Alignment.CenterHorizontally){Icon(Icons.Outlined.FolderOpen,null,tint=MoodifyMuted,modifier=Modifier.size(36.dp));Text("尚未选择文件",color=MoodifyNavy,fontSize=14.sp,modifier=Modifier.padding(top=8.dp));TextButton(onClick=pick){Text("去选择音频",color=MoodifyPurple)}}}} else {files.forEachIndexed{i,file->BatchRow(i+1,file.name,file.sizeLabel);if(i<files.size-1)Spacer(Modifier.height(9.dp))}};Spacer(Modifier.height(18.dp));GradientButton(if(files.isEmpty())"选择音频文件" else "开始处理",if(files.isEmpty())pick else start);TextButton(onClick=library){Text("仅保存到作品库",color=MoodifyPurple,modifier=Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.Center)};TextButton(onClick=back){Text("返回上传入口",color=MoodifyMuted,modifier=Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.Center)};Spacer(Modifier.height(20.dp))}}

@Composable private fun Header(title:String,back:()->Unit,icon:ImageVector){Row(verticalAlignment=Alignment.CenterVertically){IconButton(onClick=back){Icon(Icons.AutoMirrored.Outlined.ArrowBackIos,"返回")};Text(title,Modifier.weight(1f),color=MoodifyNavy,fontSize=22.sp,fontWeight=FontWeight.Bold,textAlign=androidx.compose.ui.text.style.TextAlign.Center);IconButton(onClick={}){Icon(icon,null)}}}

@Composable private fun DemoAudioRow(name:String,size:String,click:()->Unit){Row(Modifier.fillMaxWidth().clickable(onClick=click).padding(vertical=12.dp),verticalAlignment=Alignment.CenterVertically){Icon(Icons.Outlined.MusicNote,null,tint=MoodifyPurple,modifier=Modifier.size(36.dp));Column(Modifier.padding(start=12.dp).weight(1f)){Text(name,color=MoodifyNavy,fontSize=13.sp,fontWeight=FontWeight.Medium);Text(size,color=MoodifyMuted,fontSize=10.sp,modifier=Modifier.padding(top=3.dp))};Icon(Icons.Outlined.AddCircle,null,tint=MoodifyBlue,modifier=Modifier.size(22.dp))}}
@Composable private fun Source(icon:ImageVector,title:String,sub:String,modifier:Modifier,click:()->Unit){Card(onClick=click,modifier=modifier.height(138.dp),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White),elevation=CardDefaults.cardElevation(3.dp)){Column(Modifier.padding(14.dp)){Icon(icon,null,tint=MoodifyPurple,modifier=Modifier.size(36.dp));Spacer(Modifier.weight(1f));Text(title,color=MoodifyNavy,fontSize=14.sp,fontWeight=FontWeight.Bold);Text(sub,color=MoodifyMuted,fontSize=9.sp)}}}
@Composable private fun Setting(icon:ImageVector,title:String,value:String){Row(Modifier.fillMaxWidth().padding(14.dp),verticalAlignment=Alignment.CenterVertically){Icon(icon,null,tint=MoodifyPurple);Text(title,Modifier.padding(start=11.dp).weight(1f),color=MoodifyNavy,fontSize=13.sp);Text(value,color=MoodifyMuted,fontSize=11.sp);Icon(Icons.Outlined.ChevronRight,null,tint=MoodifyMuted)}}
@Composable private fun Benefit(icon:ImageVector,title:String,sub:String,modifier:Modifier){Card(modifier,shape=RoundedCornerShape(15.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Row(Modifier.padding(11.dp)){Icon(icon,null,tint=MoodifyPurple);Column(Modifier.padding(start=8.dp)){Text(title,color=MoodifyNavy,fontSize=10.sp,fontWeight=FontWeight.Bold);Text(sub,color=MoodifyMuted,fontSize=7.sp)}}}}
@Composable private fun BatchRow(n:Int,name:String,meta:String){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(17.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Row(Modifier.padding(13.dp),verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(70.dp).background(Brush.linearGradient(listOf(MoodifyPurple,MoodifyBlue)),RoundedCornerShape(10.dp)),contentAlignment=Alignment.TopStart){Text("$n",color=Color.White,modifier=Modifier.padding(5.dp))};Column(Modifier.padding(start=14.dp).weight(1f)){Text(name,color=MoodifyNavy,fontSize=17.sp,fontWeight=FontWeight.Bold);Text("$meta · 待处理",color=MoodifyMuted,fontSize=10.sp,modifier=Modifier.padding(top=7.dp))};Icon(Icons.Outlined.AudioFile,null,tint=MoodifyMuted)}}}
@Composable private fun TagGreen(text:String){Surface(color=Color(0xFFE8F8EC),shape=RoundedCornerShape(15.dp)){Text(text,color=Color(0xFF35A953),modifier=Modifier.padding(horizontal=12.dp,vertical=7.dp))}}
@Composable private fun FilterButton(text:String){OutlinedButton(onClick={},shape=RoundedCornerShape(15.dp),contentPadding=PaddingValues(horizontal=11.dp)){Text(text,color=MoodifyMuted,fontSize=9.sp)}}
