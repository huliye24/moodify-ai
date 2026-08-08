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
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun CwcIntroScreen(onBack: () -> Unit, onStart: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back)) }
            Text(stringResource(R.string.cwc_what_is), Modifier.weight(1f), color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            Surface(color = MoodifyLavender, shape = RoundedCornerShape(10.dp)) { Text("CWC", color = MoodifyPurple, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)) }
        }
        Spacer(Modifier.height(14.dp))
        HeroCard()
        Spacer(Modifier.height(14.dp))
        GroupCard(stringResource(R.string.cwc_understand_as)) {
            BenefitLine(Icons.Outlined.CardGiftcard, stringResource(R.string.cwc_benefit_gift), stringResource(R.string.cwc_benefit_gift_desc))
            BenefitLine(Icons.Outlined.ConfirmationNumber, stringResource(R.string.cwc_benefit_pass), stringResource(R.string.cwc_benefit_pass_desc))
            BenefitLine(Icons.Outlined.WorkspacePremium, stringResource(R.string.cwc_benefit_package), stringResource(R.string.cwc_benefit_package_desc))
        }
        Spacer(Modifier.height(12.dp))
        GroupCard(stringResource(R.string.cwc_after_activation)) {
            BenefitLine(Icons.Outlined.CloudUpload, stringResource(R.string.cwc_benefit_first_work), stringResource(R.string.cwc_benefit_first_work_desc))
            BenefitLine(Icons.Outlined.Inventory2, stringResource(R.string.cwc_benefit_catalog), stringResource(R.string.cwc_benefit_catalog_desc))
            BenefitLine(Icons.Outlined.PersonAdd, stringResource(R.string.cwc_benefit_profile), stringResource(R.string.cwc_benefit_profile_desc))
            BenefitLine(Icons.Outlined.LocalOffer, stringResource(R.string.cwc_benefit_discount), stringResource(R.string.cwc_benefit_discount_desc))
        }
        Spacer(Modifier.height(12.dp))
        GroupCard(stringResource(R.string.cwc_steps)) {
            StepLine(1, stringResource(R.string.cwc_step1), stringResource(R.string.cwc_step1_desc))
            StepLine(2, stringResource(R.string.cwc_step2), stringResource(R.string.cwc_step2_desc))
            StepLine(3, stringResource(R.string.cwc_step3), stringResource(R.string.cwc_step3_desc))
            StepLine(4, stringResource(R.string.cwc_step4), stringResource(R.string.cwc_step4_desc))
        }
        Spacer(Modifier.height(18.dp))
        GradientButton(stringResource(R.string.cwc_start), onStart)
        TextButton(onClick = {}) { Text(stringResource(R.string.cwc_rules), color = MoodifyPurple, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun HeroCard() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) {
        Row(Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFFF6F3FF), Color(0xFFEAF2FF))), RoundedCornerShape(22.dp)).padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) { MoodifyMark(Modifier.size(40.dp, 28.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold) }
                Text(stringResource(R.string.cwc_creator_pass_title), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 10.dp))
                Text(stringResource(R.string.cwc_creator_pass_sub), color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 6.dp))
            }
            Box(Modifier.size(86.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(22.dp)), contentAlignment = Alignment.Center) {
                Icon(Icons.Outlined.ConfirmationNumber, null, tint = Color.White, modifier = Modifier.size(44.dp))
            }
        }
    }
}

@Composable
private fun GroupCard(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
        Column(Modifier.padding(14.dp)) {
            Text(title, color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            content()
        }
    }
}

@Composable
private fun BenefitLine(icon: androidx.compose.ui.graphics.vector.ImageVector, title: String, sub: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(38.dp).background(Color(0xFFF4F2FF), RoundedCornerShape(11.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(21.dp)) }
        Text(title, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 12.dp))
        Spacer(Modifier.weight(1f))
        Text(sub, color = MoodifyMuted, fontSize = 10.sp)
    }
}

@Composable
private fun StepLine(step: Int, title: String, sub: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(34.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) { Text("$step", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
        Text(title, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 12.dp))
        Spacer(Modifier.weight(1f))
        Text(sub, color = MoodifyMuted, fontSize = 10.sp)
    }
}
