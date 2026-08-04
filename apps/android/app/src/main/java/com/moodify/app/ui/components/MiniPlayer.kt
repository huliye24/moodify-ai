package com.moodify.app.ui.components

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.AnimationVector1D
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.util.VelocityTracker
import androidx.compose.ui.layout.layout
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.PlaybackState
import com.moodify.app.data.QueueItem
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.roundToInt

/**
 * Owns drag/offset state of the mini player. Collapsing the player is a pure UI
 * operation — audio playback lives in [PlaybackManager] and is never touched here.
 */
class MiniPlayerGestureController(
    private val scope: CoroutineScope,
    private val offsetAnim: Animatable<Float, AnimationVector1D>,
    private val heightAnim: Animatable<Float, AnimationVector1D>,
    private val peekHeightPx: Float,
    private val onVisibilityChange: (MiniPlayerVisibility) -> Unit,
) {
    /** Natural measured height of the player content; kept in sync during composition. */
    var contentHeightPx: Float = 0f

    var isDragging by mutableStateOf(false)
        private set

    /** Animated container height in px; read from layout so animation drives re-layout. */
    val heightPx: Float get() = heightAnim.value

    private val snapTween =
        tween<Float>(MiniPlayerGestureConstants.SNAP_DURATION_MS, easing = FastOutSlowInEasing)

    /** Called once a real drag (past touch slop) starts; expands layout for the drag. */
    fun dragStart() {
        if (!isDragging) isDragging = true
        scope.launch { heightAnim.snapTo(contentHeightPx) }
    }

    /** Follows the finger; the offset is clamped between the visible and hidden bounds. */
    fun dragUpdate(deltaY: Float) {
        scope.launch {
            offsetAnim.snapTo(clampedMiniPlayerOffset(offsetAnim.value, deltaY, contentHeightPx))
        }
    }

    /** Finger released; settles by distance/velocity thresholds. */
    fun dragEnd(totalDelta: Float, velocityYPxS: Float) {
        finish(resolveSnapTarget(offsetAnim.value, contentHeightPx, totalDelta, velocityYPxS).toVisibility())
    }

    /** Gesture cancelled (e.g. by the system); settles to the nearer end. */
    fun dragCancel() {
        finish(resolveSnapTarget(offsetAnim.value, contentHeightPx, 0f, 0f).toVisibility())
    }

    /** Tap on the hidden peek strip reveals the player. */
    fun snapToVisible() = finish(MiniPlayerVisibility.VISIBLE)

    fun snapToHidden() = finish(MiniPlayerVisibility.HIDDEN_PEEK)

    /** Jump without animation; used on first layout so restored state never flashes. */
    fun snapTo(target: MiniPlayerVisibility) {
        if (contentHeightPx <= 0f) return
        scope.launch {
            launch { offsetAnim.snapTo(targetOffset(target)) }
            launch { heightAnim.snapTo(targetHeight(target)) }
        }
    }

    /** Animated settle used whenever the target visibility changes. */
    fun settle(target: MiniPlayerVisibility) {
        if (contentHeightPx <= 0f) return
        scope.launch {
            launch { offsetAnim.animateTo(targetOffset(target), snapTween) }
            launch { heightAnim.animateTo(targetHeight(target), snapTween) }
        }
    }

    private fun finish(target: MiniPlayerVisibility) {
        isDragging = false
        onVisibilityChange(target)
        settle(target)
    }

    private fun targetOffset(target: MiniPlayerVisibility): Float =
        if (target == MiniPlayerVisibility.VISIBLE) 0f else contentHeightPx

    private fun targetHeight(target: MiniPlayerVisibility): Float =
        if (target == MiniPlayerVisibility.VISIBLE) contentHeightPx else peekHeightPx
}

/**
 * Global mini player pinned above the bottom navigation bar.
 *
 * Vertically draggable between [MiniPlayerVisibility.VISIBLE] and
 * [MiniPlayerVisibility.HIDDEN_PEEK]: dragging down slides the player away
 * (music keeps playing), the peek strip remains above the nav bar, and
 * dragging the strip up reveals the player again.
 */
@Composable
fun MiniPlayer(
    visibility: MiniPlayerVisibility,
    onVisibilityChange: (MiniPlayerVisibility) -> Unit,
    onOpen: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val state by PlaybackManager.state.collectAsStateWithLifecycle()
    val current = state.current ?: return

    LaunchedEffect(state.url) {
        while (true) {
            PlaybackManager.tick()
            delay(500)
        }
    }

    val density = LocalDensity.current
    val scope = rememberCoroutineScope()
    val offsetAnim = remember { Animatable(0f) }
    val heightAnim = remember { Animatable(0f) }
    val peekHeightPx = with(density) { MiniPlayerGestureConstants.PEEK_TOUCH_HEIGHT_DP.dp.toPx() }
    val controller = remember {
        MiniPlayerGestureController(scope, offsetAnim, heightAnim, peekHeightPx, onVisibilityChange)
    }
    var contentHeightPx by remember { mutableFloatStateOf(0f) }
    controller.contentHeightPx = contentHeightPx
    var initialSynced by remember { mutableStateOf(false) }

    // First layout must snap (no flash on restore); later visibility/height changes settle.
    LaunchedEffect(visibility, contentHeightPx) {
        if (contentHeightPx <= 0f || controller.isDragging) return@LaunchedEffect
        if (!initialSynced) {
            controller.snapTo(visibility)
            initialSynced = true
        } else {
            controller.settle(visibility)
        }
    }

    BoxWithAnimatedHeight(
        controller = controller,
        modifier = modifier.testTag("mini_player"),
    ) {
        MiniPlayerPeekHandle(controller, Modifier.align(Alignment.BottomCenter))
        Box(
            Modifier
                .fillMaxWidth()
                .testTag("mini_player_drag")
                .onSizeChanged { contentHeightPx = it.height.toFloat() }
                .graphicsLayer { translationY = offsetAnim.value }
                .miniPlayerDragGesture(controller),
        ) {
            MiniPlayerContent(state = state, current = current, onOpen = onOpen)
        }
    }
}

/**
 * Measures the player content at its natural (unconstrained) height and reports
 * the animated height (full height while visible, peek height while hidden).
 */
@Composable
private fun BoxWithAnimatedHeight(
    controller: MiniPlayerGestureController,
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit,
) {
    Box(
        modifier
            .fillMaxWidth()
            .clipToBounds()
            .layout { measurable, constraints ->
                val child = measurable.measure(constraints.copy(maxHeight = Constraints.Infinity))
                val h = controller.heightPx.coerceIn(0f, child.height.toFloat())
                layout(constraints.maxWidth, h.roundToInt()) { child.place(0, 0) }
            },
        content = content,
    )
}

@Composable
private fun MiniPlayerPeekHandle(
    controller: MiniPlayerGestureController,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier
            .fillMaxWidth()
            .height(MiniPlayerGestureConstants.PEEK_TOUCH_HEIGHT_DP.dp)
            .clickable(onClick = { controller.snapToVisible() })
            .miniPlayerDragGesture(controller)
            .testTag("mini_player_peek"),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            Modifier
                .width(34.dp)
                .height(MiniPlayerGestureConstants.PEEK_VISUAL_HEIGHT_DP.dp)
                .background(Color(0x40000000), RoundedCornerShape(2.dp)),
        )
    }
}

@Composable
private fun MiniPlayerContent(
    state: PlaybackState,
    current: QueueItem,
    onOpen: () -> Unit,
) {
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 6.dp),
        shape = RoundedCornerShape(18.dp),
        color = Color.Transparent,
        shadowElevation = 0.dp,
    ) {
        Box(
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onOpen)
                .background(
                    Brush.linearGradient(listOf(Color(0xFF7B61FF), Color(0xFF4A9BFF))),
                    RoundedCornerShape(18.dp),
                )
                .padding(horizontal = 12.dp, vertical = 8.dp),
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        Modifier.size(40.dp).background(Color.White.copy(0.18f), RoundedCornerShape(11.dp)),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(Icons.Outlined.MusicNote, null, tint = Color.White, modifier = Modifier.size(22.dp))
                    }
                    Column(Modifier.weight(1f).padding(start = 10.dp)) {
                        Text(
                            current.title,
                            color = Color.White,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                        Text(
                            current.subtitle.ifEmpty { current.preset },
                            color = Color.White.copy(alpha = 0.75f),
                            fontSize = 10.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                    IconButton(onClick = { PlaybackManager.toggle() }, modifier = Modifier.testTag("mini_player_play")) {
                        Icon(
                            if (state.playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow,
                            contentDescription = if (state.playing) "暂停" else "播放",
                            tint = Color.White,
                            modifier = Modifier.size(26.dp),
                        )
                    }
                }
                MiniPlayerProgress(state)
            }
        }
    }
}

@Composable
private fun MiniPlayerProgress(state: PlaybackState) {
    if (state.durationMs > 0) {
        LinearProgressIndicator(
            progress = { if (state.durationMs > 0) state.positionMs.toFloat() / state.durationMs else 0f },
            modifier = Modifier.fillMaxWidth().padding(top = 4.dp).height(3.dp),
            color = Color.White,
            trackColor = Color.White.copy(alpha = 0.25f),
        )
    }
}

/**
 * Vertical drag that only takes over after touch slop, so taps on the player
 * (play button, open Now Playing) keep working. Tracks release velocity for
 * fling-based snapping.
 */
private fun Modifier.miniPlayerDragGesture(controller: MiniPlayerGestureController): Modifier =
    pointerInput(Unit) {
        val touchSlop = viewConfiguration.touchSlop
        awaitEachGesture {
            val down = awaitFirstDown(requireUnconsumed = false)
            val velocityTracker = VelocityTracker()
            var passedSlop = false
            var dragStarted = false
            var cancelled = false
            var totalDelta = 0f
            velocityTracker.addPosition(down.uptimeMillis, down.position)
            while (true) {
                val event = awaitPointerEvent()
                val change = event.changes.firstOrNull { it.id == down.id } ?: break
                val dy = change.position.y - change.previousPosition.y
                if (dy != 0f) {
                    totalDelta += dy
                    velocityTracker.addPosition(change.uptimeMillis, change.position)
                    if (!passedSlop && abs(totalDelta) > touchSlop) passedSlop = true
                    if (passedSlop && !change.isConsumed) {
                        change.consume()
                        if (!dragStarted) {
                            dragStarted = true
                            controller.dragStart()
                        }
                        controller.dragUpdate(dy)
                    }
                }
                if (!change.pressed && change.previousPressed) {
                    cancelled = change.isConsumed
                    break
                }
            }
            if (!passedSlop) return@awaitEachGesture
            val velocityY = velocityTracker.calculateVelocity().y
            if (cancelled || !velocityY.isFinite()) controller.dragCancel()
            else controller.dragEnd(totalDelta, velocityY)
        }
    }
