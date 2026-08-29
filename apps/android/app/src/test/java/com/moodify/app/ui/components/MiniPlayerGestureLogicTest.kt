package com.moodify.app.ui.components

import org.junit.Assert.assertEquals
import org.junit.Test

class MiniPlayerGestureLogicTest {

    private val height = 100f

    // Spec test 1: 下滑超过阈值后，播放栏收起。
    @Test
    fun dragDownBeyondQuarter_hides() {
        assertEquals(SnapDecision.HIDDEN_PEEK, resolveSnapTarget(30f, height, 30f, 0f))
    }

    // Spec test 2: 下滑未超过阈值时，播放栏回弹。
    @Test
    fun dragDownBelowQuarter_springsBack() {
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(10f, height, 10f, 0f))
    }

    // Spec test 3: 上滑超过阈值后，播放栏出现。
    @Test
    fun dragUpBeyondFifth_shows() {
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(75f, height, -25f, 0f))
    }

    // Spec test 4: 上滑未超过阈值时，播放栏保持隐藏。
    @Test
    fun dragUpBelowFifth_staysHidden() {
        assertEquals(SnapDecision.HIDDEN_PEEK, resolveSnapTarget(92f, height, -8f, 0f))
    }

    // Spec test 5: 快速下甩可以收起（即使拖动距离很小）。
    @Test
    fun fastDownFling_hidesEvenBelowDistanceThreshold() {
        assertEquals(SnapDecision.HIDDEN_PEEK, resolveSnapTarget(4f, height, 4f, 900f))
    }

    // Spec test 6: 快速上甩可以唤出（即使拖动距离很小）。
    @Test
    fun fastUpFling_showsEvenBelowDistanceThreshold() {
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(96f, height, -4f, -800f))
    }

    // 精确边界：恰好 25% 下滑收起、恰好 20% 上滑唤出。
    @Test
    fun exactDistanceThresholds_resolve() {
        assertEquals(SnapDecision.HIDDEN_PEEK, resolveSnapTarget(25f, height, 25f, 0f))
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(80f, height, -20f, 0f))
    }

    // 中间区域小幅抖动：吸附到最近一端，不出现悬停状态。
    @Test
    fun middleZone_smallJiggle_settlesToNearestEnd() {
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(45f, height, 2f, 0f))
        assertEquals(SnapDecision.HIDDEN_PEEK, resolveSnapTarget(60f, height, -2f, 0f))
    }

    // 高度未知（未测量完成）时永不隐藏。
    @Test
    fun unknownContentHeight_staysVisible() {
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(0f, 0f, 0f, 0f))
        assertEquals(SnapDecision.VISIBLE, resolveSnapTarget(50f, -1f, 10f, 1000f))
    }

    // 拖动偏移被限制在 [0, 播放栏高度] 内，不能弹飞。
    @Test
    fun clamp_neverLeavesPlayerBounds() {
        assertEquals(0f, clampedMiniPlayerOffset(10f, -50f, height), 0.001f)
        assertEquals(height, clampedMiniPlayerOffset(80f, 50f, height), 0.001f)
        assertEquals(70f, clampedMiniPlayerOffset(50f, 20f, height), 0.001f)
    }

    // 吸附决策映射到 UI 可见状态。
    @Test
    fun snapDecisionMapsToVisibility() {
        assertEquals(MiniPlayerVisibility.VISIBLE, SnapDecision.VISIBLE.toVisibility())
        assertEquals(MiniPlayerVisibility.HIDDEN_PEEK, SnapDecision.HIDDEN_PEEK.toVisibility())
    }

    // 规格常量保持可读语义：隐藏阈值高于唤出阈值。
    @Test
    fun thresholdConstants_areSane() {
        assertEquals(0.25f, MiniPlayerGestureConstants.HIDE_DISTANCE_FRACTION, 0.001f)
        assertEquals(0.20f, MiniPlayerGestureConstants.SHOW_DISTANCE_FRACTION, 0.001f)
        assertEquals(700f, MiniPlayerGestureConstants.HIDE_FLING_VELOCITY_PX_S, 0.001f)
        assertEquals(650f, MiniPlayerGestureConstants.SHOW_FLING_VELOCITY_PX_S, 0.001f)
        assertEquals(220, MiniPlayerGestureConstants.SNAP_DURATION_MS)
    }
}
