package com.moodify.app.ui.components

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipe
import androidx.compose.ui.test.swipeDown
import androidx.compose.ui.test.swipeUp
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.QueueItem
import com.moodify.app.ui.theme.MoodifyTheme
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Instrumented gesture tests for the draggable mini player
 * (spec DSK-MFY-MINI-PLAYER-SWIPE-001). Runs on a real device via
 * instrumentation, which bypasses the adb input-injection limitations.
 */
@RunWith(AndroidJUnit4::class)
class MiniPlayerGestureTest {

    @get:Rule
    val composeRule = createComposeRule()

    /** Launches the mini player with seeded playback state (no backend needed). */
    private fun launchMiniPlayer() {
        composeRule.setContent {
            MoodifyTheme {
                val context = LocalContext.current
                LaunchedEffect(Unit) {
                    PlaybackManager.init(context)
                    // Unreachable path on purpose: playback settles into a stable
                    // error state instead of depending on a live server.
                    PlaybackManager.play("/catalog/mini-player-test/download", "测试曲目")
                }
                var visibility by remember { mutableStateOf(MiniPlayerVisibility.VISIBLE) }
                Box(Modifier.fillMaxSize()) {
                    Column(Modifier.align(Alignment.BottomCenter)) {
                        MiniPlayer(
                            visibility = visibility,
                            onVisibilityChange = { visibility = it },
                            onOpen = {},
                        )
                    }
                }
            }
        }
        composeRule.waitUntil(timeoutMillis = 8_000) {
            PlaybackManager.state.value.error != null
        }
        composeRule.waitForIdle()
    }

    private fun dragNodeTop(): Float {
        composeRule.waitForIdle()
        return composeRule.onNodeWithTag("mini_player_drag")
            .fetchSemanticsNode()
            .boundsInRoot.top
    }

    // Spec test 1: 下滑超过阈值后，播放栏收起。
    @Test
    fun swipeDownBeyondThreshold_collapsesPlayer() {
        launchMiniPlayer()
        val before = dragNodeTop()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
        composeRule.waitForIdle()
        val after = dragNodeTop()
        assertTrue("player should slide down by at least half its height", after > before + 100f)
    }

    // Spec test 2: 下滑未超过阈值时，播放栏回弹。
    @Test
    fun swipeDownBelowThreshold_springsBack() {
        launchMiniPlayer()
        val before = dragNodeTop()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput {
            swipe(start = center, end = center + Offset(0f, 40f), durationMillis = 200)
        }
        composeRule.waitForIdle()
        assertEquals("player springs back to visible", before, dragNodeTop(), 1f)
    }

    // Spec test 3: 上滑超过阈值后，播放栏出现。
    @Test
    fun swipeUpFromPeek_revealsPlayer() {
        launchMiniPlayer()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
        composeRule.waitForIdle()
        val hiddenTop = dragNodeTop()
        assertTrue("player is hidden", hiddenTop > 100f)
        composeRule.onNodeWithTag("mini_player_peek").performTouchInput { swipeUp() }
        composeRule.waitForIdle()
        val revealed = dragNodeTop()
        assertTrue("player slides back up", revealed < hiddenTop - 100f)
    }

    // Spec test 4: 上滑未超过阈值时，播放栏保持隐藏。
    @Test
    fun swipeUpBelowThreshold_staysHidden() {
        launchMiniPlayer()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
        composeRule.waitForIdle()
        val hiddenTop = dragNodeTop()
        composeRule.onNodeWithTag("mini_player_peek").performTouchInput {
            swipe(start = center, end = center - Offset(0f, 40f), durationMillis = 200)
        }
        composeRule.waitForIdle()
        assertTrue("stays hidden", dragNodeTop() > hiddenTop - 1f)
    }

    // Spec test 5: 快速下甩可以收起。
    @Test
    fun fastFlingDown_collapses() {
        launchMiniPlayer()
        val before = dragNodeTop()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput {
            down(center)
            repeat(4) { moveBy(Offset(0f, 120f)) }
            up()
        }
        composeRule.waitForIdle()
        assertTrue("fling collapses", dragNodeTop() > before + 100f)
    }

    // Spec test 6: 快速上甩可以唤出。
    @Test
    fun fastFlingUp_reveals() {
        launchMiniPlayer()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput {
            down(center)
            repeat(4) { moveBy(Offset(0f, 120f)) }
            up()
        }
        composeRule.waitForIdle()
        val hiddenTop = dragNodeTop()
        composeRule.onNodeWithTag("mini_player_peek").performTouchInput {
            down(center)
            repeat(4) { moveBy(Offset(0f, -120f)) }
            up()
        }
        composeRule.waitForIdle()
        assertTrue("fling reveals", dragNodeTop() < hiddenTop - 100f)
    }

    // Spec test 7: 点击播放按钮不会触发拖动。
    @Test
    fun tapPlayButton_doesNotDrag() {
        launchMiniPlayer()
        val before = dragNodeTop()
        val playingBefore = PlaybackManager.state.value.playing
        composeRule.onNodeWithTag("mini_player_play").performClick()
        composeRule.waitForIdle()
        assertEquals("no drag from tap", before, dragNodeTop(), 1f)
        assertTrue("playback toggled", PlaybackManager.state.value.playing != playingBefore)
    }

    // Spec test 8: 收起播放栏后音乐继续播放（播放状态完全不受影响）。
    @Test
    fun collapse_doesNotTouchPlaybackState() {
        launchMiniPlayer()
        val snapshot = PlaybackManager.state.value
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
        composeRule.waitForIdle()
        assertTrue(dragNodeTop() > 100f)
        assertEquals("playback state untouched by hiding", snapshot, PlaybackManager.state.value)
    }

    // Spec test 9: 收起状态下切换歌曲，重新展开后信息正确。
    @Test
    fun trackSwitchWhileHidden_updatesContent() {
        launchMiniPlayer()
        composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
        composeRule.waitForIdle()
        composeRule.runOnUiThread {
            PlaybackManager.playQueue(
                listOf(QueueItem(title = "第二首测试曲目", subtitle = "创作者B", path = "/catalog/two/download")),
                0,
            )
        }
        composeRule.waitForIdle()
        composeRule.onNodeWithTag("mini_player_peek").performTouchInput { swipeUp() }
        composeRule.waitForIdle()
        composeRule.onNodeWithText("第二首测试曲目").assertIsDisplayed()
        composeRule.onNodeWithText("创作者B").assertIsDisplayed()
    }

    // Spec test 12: 快速连续拖动不会造成动画状态错乱。
    @Test
    fun rapidConsecutiveDrags_settleStably() {
        launchMiniPlayer()
        repeat(3) {
            composeRule.onNodeWithTag("mini_player_drag").performTouchInput { swipeDown() }
            composeRule.waitForIdle()
            composeRule.onNodeWithTag("mini_player_peek").performTouchInput { swipeUp() }
            composeRule.waitForIdle()
        }
        val top = dragNodeTop()
        assertTrue("settles back to visible", top < 50f)
    }
}
