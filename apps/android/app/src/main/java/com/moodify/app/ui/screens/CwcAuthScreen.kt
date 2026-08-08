package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import androidx.lifecycle.viewmodel.compose.viewModel
import com.moodify.app.data.CwcRepository
import com.moodify.app.model.AuthMode
import com.moodify.app.model.CwcValidationState
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun CwcAuthScreen(
    mode: AuthMode,
    prefilledCode: String? = null,
    onBack: () -> Unit,
    onShowIntro: () -> Unit,
    onActivated: () -> Unit,
    onLoggedIn: () -> Unit,
) {
    val appContext = androidx.compose.ui.platform.LocalContext.current
    val repository = remember(appContext) { CwcRepository(appContext) }
    var authMode by remember { mutableStateOf(mode) }
    var phone by rememberSaveable { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var cwcCode by rememberSaveable { mutableStateOf(prefilledCode?.let { repository.normalize(it) } ?: "") }
    var validation by remember { mutableStateOf<CwcValidationState>(CwcValidationState.Idle) }
    var showSuccess by remember { mutableStateOf(false) }
    val validating = validation is CwcValidationState.Loading

    // Live validation with debounce while typing.
    LaunchedEffect(cwcCode) {
        if (authMode == AuthMode.Onboarding && cwcCode.length >= 8) {
            validation = CwcValidationState.Loading
            kotlinx.coroutines.delay(450)
            validation = repository.validate(cwcCode)
        } else {
            validation = CwcValidationState.Idle
        }
    }

    fun switchMode(newMode: AuthMode) {
        authMode = newMode
        validation = CwcValidationState.Idle
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back)) }
            Spacer(Modifier.weight(1f))
            Row(verticalAlignment = Alignment.CenterVertically) { MoodifyMark(Modifier.size(38.dp, 27.dp)); Spacer(Modifier.width(6.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold) }
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.width(48.dp))
        }
        Spacer(Modifier.height(22.dp))
        if (authMode == AuthMode.Onboarding) {
            Text(stringResource(R.string.auth_onboarding_title), color = MoodifyNavy, fontSize = 23.sp, fontWeight = FontWeight.Bold)
            Text(stringResource(R.string.auth_onboarding_subtitle), color = MoodifyMuted, fontSize = 13.sp, modifier = Modifier.padding(top = 6.dp))
            Spacer(Modifier.height(20.dp))
            OutlinedTextField(phone, { phone = it }, Modifier.fillMaxWidth(), label = { Text(stringResource(R.string.auth_phone_email)) }, singleLine = true, shape = RoundedCornerShape(16.dp))
            Spacer(Modifier.height(11.dp))
            OutlinedTextField(password, { password = it }, Modifier.fillMaxWidth(), label = { Text(stringResource(R.string.auth_password)) }, singleLine = true, visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(), shape = RoundedCornerShape(16.dp))
            Spacer(Modifier.height(11.dp))
            OutlinedTextField(
                cwcCode,
                { raw -> cwcCode = repository.normalize(raw) },
                Modifier.fillMaxWidth(),
                label = { Text(stringResource(R.string.auth_cwc_code)) },
                placeholder = { Text("CWC-XZ7M-42KP") },
                singleLine = true,
                shape = RoundedCornerShape(16.dp),
                isError = validation is CwcValidationState.Error,
            )
            Spacer(Modifier.height(6.dp))
            ValidationHint(validation)
            Spacer(Modifier.height(4.dp))
            TextButton(onClick = onShowIntro) { Text(stringResource(R.string.auth_what_is_cwc), color = MoodifyPurple, fontSize = 12.sp) }
            Spacer(Modifier.height(10.dp))
            val validPass = (validation as? CwcValidationState.Valid)?.pass
            val canSubmit = phone.isNotBlank() && password.isNotBlank() && validPass != null && !validating
            Button(
                onClick = {
                    if (canSubmit) {
                        repository.activate(validPass!!.code)
                        showSuccess = true
                    }
                },
                enabled = canSubmit,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(26.dp),
                colors = ButtonDefaults.buttonColors(containerColor = if (canSubmit) MoodifyBlue else Color(0xFFC9CFE0)),
            ) { Text(stringResource(R.string.auth_verify_cwc), color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.SemiBold) }
            Spacer(Modifier.height(8.dp))
            TextButton(onClick = { switchMode(AuthMode.Login) }, modifier = Modifier.fillMaxWidth()) {
                Text(stringResource(R.string.auth_have_account), color = MoodifyMuted, fontSize = 13.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            }
        } else {
            Text(stringResource(R.string.auth_welcome_back), color = MoodifyNavy, fontSize = 23.sp, fontWeight = FontWeight.Bold)
            Text(stringResource(R.string.auth_account_synced), color = MoodifyMuted, fontSize = 13.sp, modifier = Modifier.padding(top = 6.dp))
            Spacer(Modifier.height(16.dp))
            QuickAccountCard()
            Spacer(Modifier.height(14.dp))
            OutlinedTextField(phone, { phone = it }, Modifier.fillMaxWidth(), label = { Text(stringResource(R.string.auth_phone_email)) }, singleLine = true, shape = RoundedCornerShape(16.dp))
            Spacer(Modifier.height(11.dp))
            OutlinedTextField(password, { password = it }, Modifier.fillMaxWidth(), label = { Text(stringResource(R.string.auth_password)) }, singleLine = true, visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(), shape = RoundedCornerShape(16.dp))
            Spacer(Modifier.height(18.dp))
            GradientButton(stringResource(R.string.auth_login_create), onClick = onLoggedIn, enabled = phone.isNotBlank() && password.isNotBlank())
            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedButton(onClick = {}, modifier = Modifier.weight(1f), shape = RoundedCornerShape(16.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) {
                    Icon(Icons.Outlined.Chat, null, tint = MoodifyGreen, modifier = Modifier.size(17.dp)); Spacer(Modifier.width(6.dp)); Text(stringResource(R.string.auth_wechat_login), color = MoodifyNavy, fontSize = 12.sp)
                }
                OutlinedButton(onClick = {}, modifier = Modifier.weight(1f), shape = RoundedCornerShape(16.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) {
                    Icon(Icons.Outlined.Sms, null, tint = MoodifyBlue, modifier = Modifier.size(17.dp)); Spacer(Modifier.width(6.dp)); Text(stringResource(R.string.auth_code_login), color = MoodifyNavy, fontSize = 12.sp)
                }
            }
            Spacer(Modifier.height(12.dp))
            TextButton(onClick = { switchMode(AuthMode.Onboarding) }, modifier = Modifier.fillMaxWidth()) {
                Text(stringResource(R.string.auth_no_account), color = MoodifyMuted, fontSize = 13.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            }
        }
        Spacer(Modifier.height(20.dp))
    }

    if (showSuccess) {
        AlertDialog(
            onDismissRequest = { },
            shape = RoundedCornerShape(24.dp),
            title = { Text(stringResource(R.string.auth_activation_success), color = MoodifyNavy, fontWeight = FontWeight.Bold) },
            text = {
                Column {
                    Text(stringResource(R.string.auth_welcome, "泫榛"), color = MoodifyNavy, fontSize = 14.sp)
                    Spacer(Modifier.height(10.dp))
                    BenefitDot("首个作品免费入驻")
                    BenefitDot("基础版权建档")
                    BenefitDot("创作者主页开启")
                    BenefitDot("1 张标准处理 8 折券")
                    Spacer(Modifier.height(8.dp))
                    Text("免费入驻与建档不包含 DSP 标准处理费用", color = MoodifyMuted, fontSize = 10.sp)
                }
            },
            confirmButton = {
                Button(onClick = { showSuccess = false; onActivated() }, colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(14.dp)) {
                    Text(stringResource(R.string.auth_enter_processing), color = Color.White)
                }
            },
        )
    }
}

@Composable
private fun BenefitDot(text: String) {
    Row(Modifier.padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyGreen, modifier = Modifier.size(16.dp))
        Spacer(Modifier.width(8.dp))
        Text(text, color = MoodifyNavy, fontSize = 13.sp)
    }
}

@Composable
private fun ValidationHint(state: CwcValidationState) {
    val (color, label) = when (state) {
        CwcValidationState.Idle -> MoodifyMuted to stringResource(R.string.auth_hint_idle)
        CwcValidationState.Loading -> MoodifyBlue to stringResource(R.string.auth_hint_checking)
        is CwcValidationState.Valid -> MoodifyGreen to stringResource(R.string.auth_hint_valid)
        is CwcValidationState.Error -> Color(0xFFE05B5B) to state.message
    }
    Text(label, color = color, fontSize = 12.sp)
}

@Composable
private fun QuickAccountCard() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color(0xFFF0FBFF))) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.size(44.dp).background(Brush.linearGradient(listOf(Color(0xFFC9C5FF), Color(0xFFEBD6FF))), RoundedCornerShape(12.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color(0xFF29206D)) }
            Column(Modifier.padding(start = 12.dp).weight(1f)) {
                Text("泫榛 · ${stringResource(R.string.auth_activated_badge)}", color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                Text("@moodify_xzhen", color = MoodifyMuted, fontSize = 11.sp)
            }
            Surface(color = Color(0xFFE3F8EC), shape = RoundedCornerShape(9.dp)) { Text(stringResource(R.string.auth_activated), color = MoodifyGreen, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp)) }
        }
    }
}
