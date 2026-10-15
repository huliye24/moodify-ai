function result = study008_localized_candidate_audition(ctx)
%STUDY008_LOCALIZED_CANDIDATE_AUDITION Locate local candidates and export them for listening.
%
%   WHY THIS EXISTS
%   The S006/S007 metrics were built to find LOCAL problems. Auditing them
%   against the material disqualified most of what they flagged:
%
%     * S006's 12 "persistent tonal peaks" are musical notes, not resonances.
%       Each is within 6 dB of its maximum in only 1-5% of seconds, and the
%       strongest form a harmonic series (700.2 / 1400.4 / 2097.7 Hz), so they
%       appear when a note is PLAYED, not persistently.
%     * S006's only local band flag (8k-16k, +6.44 dB vs the line through its
%       neighbours) is a metric artifact. The LALAL master and the original
%       agree within 0.03/0.02/0.15 dB across 4k-8k / 8k-16k / 16k-20k, and the
%       -15 dB drop into 16k-20k is present in the ORIGINAL too (the recording's
%       anti-alias rolloff). Comparing 8k-16k against a midpoint that includes
%       the rolloff band inflates it into a false anomaly.
%
%   What survives is the time-anchored stereo finding. Everything else needs
%   EARS, and this study cannot supply ears -- so it supplies the material for
%   someone else's ears instead of more thresholds.
%
%   This study MEASURES AND EXPORTS ONLY. It applies no EQ, no compression, no
%   widening, and does not write any processed master. The excerpts it writes
%   are copies of existing material plus the same window from the original.
%
%   Disqualified candidates are recorded in the output too, with the reason,
%   so a later pass does not re-open them.

fprintf('[S008] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
originalPath = fullfile(root, "自己的神话3.wav");
masterPath = fullfile(root, "LALAL重制版_vs_Suno分轨重制版_20261011", ...
                      "自己的神话_LALAL分轨重制_48k24.wav");

% Engineering defaults. Every one of these is a knob, and the sensitivity
% panel reports how the candidate count moves when they change.
narrowCorrHigh = 0.95;      % sustained L/R correlation above this = narrow
wideCorrLow    = 0.55;      % sustained below this = unusually wide / phase-risky
hotWithinDb    = 3.0;       % peak envelope within this of the file max
minSegmentSeconds = 2;      % ignore anything shorter than this
mergeGapSeconds   = 2;      % join candidates separated by less than this
contextSeconds    = 2.0;    % extra audio either side of a candidate
maxExportsPerType = 8;      % hard cap; the cap is reported, never silent
fadeSeconds       = 0.050;

bandEdges = [20 60; 60 125; 125 250; 250 500; 500 1000; ...
             1000 2000; 2000 4000; 4000 8000; 8000 16000; 16000 20000];
bandLabels = ["20-60"; "60-125"; "125-250"; "250-500"; "500-1k"; ...
              "1k-2k"; "2k-4k"; "4k-8k"; "8k-16k"; "16k-20k"];

auditionDir = fullfile(ctx.outputDir, 'audition');
if ~isfolder(auditionDir)
    mkdir(auditionDir);
end

failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: load -------------------------------------------------------
fprintf('[S008] stage 1: load\n');
stageTimer = tic;
[original, fs] = audioread(originalPath);
[master, fsMaster] = audioread(masterPath);
if fsMaster ~= fs
    error('MoodifyLab:S008:RateMismatch', 'Sample rates differ.');
end
frames = min(size(original, 1), size(master, 1));
original = original(1:frames, 1:2);
master = master(1:frames, 1:2);
seconds = floor(frames / fs);
fprintf('[S008]   %d frames @ %d Hz = %.2f s (%d whole seconds)\n', ...
    frames, fs, frames/fs, seconds);
metrics.source = struct('frames', frames, 'sampleRate', fs, ...
    'wholeSeconds', seconds, 'masterPath', masterPath, 'originalPath', originalPath);
fprintf('[S008]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: per-second evidence (validated metrics only) --------------
fprintf('[S008] stage 2: per-second evidence\n');
stageTimer = tic;
monoMaster = mean(master, 2);
correlation = zeros(seconds, 1);
sideMidDb = zeros(seconds, 1);
peakDb = zeros(seconds, 1);
for index = 1:seconds
    span = (index-1)*fs + (1:fs);
    left = master(span, 1);
    right = master(span, 2);
    mid = 0.5 * (left + right);
    side = 0.5 * (left - right);
    if std(left) < eps || std(right) < eps
        correlation(index) = 1;
    else
        matrix = corrcoef(left, right);
        correlation(index) = matrix(1, 2);
    end
    sideMidDb(index) = 10*log10((mean(side.^2) + eps) / (mean(mid.^2) + eps));
    peakDb(index) = 20*log10(max(abs(monoMaster(span))) + eps);
end
filePeakDb = 20*log10(max(abs(monoMaster)) + eps);
metrics.perSecond = struct('narrowCorrHigh', narrowCorrHigh, ...
    'wideCorrLow', wideCorrLow, 'hotWithinDb', hotWithinDb, ...
    'filePeakDbfs', filePeakDb, ...
    'narrowSeconds', sum(correlation > narrowCorrHigh), ...
    'wideSeconds', sum(correlation < wideCorrLow), ...
    'hotSeconds', sum(peakDb > filePeakDb - hotWithinDb));
fprintf('[S008]   file peak %.2f dBFS; narrow %d s, wide %d s, hot %d s\n', ...
    filePeakDb, metrics.perSecond.narrowSeconds, ...
    metrics.perSecond.wideSeconds, metrics.perSecond.hotSeconds);
fprintf('[S008]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: same-render band delta vs the original --------------------
% Only meaningful because LALAL and the original ARE the same render: a
% -60 dB stem round-trip means the two share a timebase, so a per-band
% difference here is the mastering chain's actual change.
fprintf('[S008] stage 3: same-render band delta\n');
stageTimer = tic;
windowSeconds = 4;
bandMaster = bandPowerPerWindow(master, fs, bandEdges, windowSeconds);
bandOriginal = bandPowerPerWindow(original, fs, bandEdges, windowSeconds);
windows = min(size(bandMaster, 1), size(bandOriginal, 1));
bandDelta = bandMaster(1:windows, :) - bandOriginal(1:windows, :);
maxBandDelta = max(abs(bandDelta), [], 2);
metrics.sameRenderDelta = struct('windowSeconds', windowSeconds, ...
    'medianAbsBandDeltaDb', median(maxBandDelta), ...
    'p95AbsBandDeltaDb', prctile(maxBandDelta, 95), ...
    'maxAbsBandDeltaDb', max(maxBandDelta));
fprintf('[S008]   max |band delta| per %d s window: median %.2f dB, p95 %.2f dB, max %.2f dB\n', ...
    windowSeconds, median(maxBandDelta), prctile(maxBandDelta, 95), max(maxBandDelta));
fprintf('[S008]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: candidates -------------------------------------------------
fprintf('[S008] stage 4: candidates\n');
stageTimer = tic;
narrowSegments = segmentsFromMask(correlation > narrowCorrHigh, minSegmentSeconds, mergeGapSeconds);
wideSegments   = segmentsFromMask(correlation < wideCorrLow, minSegmentSeconds, mergeGapSeconds);
hotSegments    = segmentsFromMask(peakDb > filePeakDb - hotWithinDb, minSegmentSeconds, mergeGapSeconds);

fprintf('[S008]   narrow stereo : %d segment(s)\n', size(narrowSegments, 1));
fprintf('[S008]   wide stereo   : %d segment(s)\n', size(wideSegments, 1));
fprintf('[S008]   peak-dense    : %d segment(s)\n', size(hotSegments, 1));

% Threshold sensitivity: shows the candidate count is not the product of one
% convenient threshold.
sensitivity = struct();
sensitivity.narrowCorr = [0.90 0.93 0.95 0.97 0.99];
sensitivity.narrowSegments = zeros(size(sensitivity.narrowCorr));
for index = 1:numel(sensitivity.narrowCorr)
    found = segmentsFromMask(correlation > sensitivity.narrowCorr(index), ...
        minSegmentSeconds, mergeGapSeconds);
    sensitivity.narrowSegments(index) = size(found, 1);
end
sensitivity.wideCorr = [0.65 0.60 0.55 0.50 0.45];
sensitivity.wideSegments = zeros(size(sensitivity.wideCorr));
for index = 1:numel(sensitivity.wideCorr)
    found = segmentsFromMask(correlation < sensitivity.wideCorr(index), ...
        minSegmentSeconds, mergeGapSeconds);
    sensitivity.wideSegments(index) = size(found, 1);
end
metrics.thresholdSensitivity = sensitivity;
fprintf('[S008]   narrow 阈值 0.90..0.99 -> 段数 %s\n', mat2str(sensitivity.narrowSegments));
fprintf('[S008]   wide   阈值 0.65..0.45 -> 段数 %s\n', mat2str(sensitivity.wideSegments));
fprintf('[S008]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: export audition excerpts ----------------------------------
fprintf('[S008] stage 5: audition exports\n');
stageTimer = tic;
candidates = table();
candidates = appendExports(candidates, narrowSegments, "narrow_stereo", ...
    correlation, master, original, fs, auditionDir, contextSeconds, ...
    fadeSeconds, maxExportsPerType);
candidates = appendExports(candidates, wideSegments, "wide_stereo", ...
    correlation, master, original, fs, auditionDir, contextSeconds, ...
    fadeSeconds, maxExportsPerType);
candidates = appendExports(candidates, hotSegments, "peak_dense", ...
    peakDb, master, original, fs, auditionDir, contextSeconds, ...
    fadeSeconds, maxExportsPerType);
exportedCount = height(candidates);

% The same-render band delta is per window, not per second; report its worst
% windows as a frequency-anchored pointer rather than an audio excerpt, since
% the whole song is already the A/B for this one.
[~, worstWindow] = max(maxBandDelta);
worstWindowSeconds = worstWindow * windowSeconds;
writetable(table((1:windows)', (1:windows)'*windowSeconds, maxBandDelta, ...
    'VariableNames', {'window_index', 'start_s', 'max_abs_band_delta_db'}), ...
    fullfile(ctx.outputDir, 's008_same_render_delta.csv'));

fprintf('[S008]   exported %d excerpt pair(s) to audition\\\n', exportedCount);
fprintf('[S008]   worst same-render window at %.0f s (%.2f dB)\n', ...
    worstWindowSeconds, maxBandDelta(worstWindow));
fprintf('[S008]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: disqualification record -----------------------------------
% Recorded so a later pass does not re-open findings that were audited and
% rejected. This is evidence about the METRICS, not about the audio.
disqualified = [
    struct('finding', "S006 12 persistent tonal peaks (resonance candidates)", ...
           'metric', "narrow peak in long-term average spectrum", ...
           'reason', "Musical notes, not resonances: each is within 6 dB of its own maximum in only 1-5% of seconds, and the strongest form a harmonic series (700.2 / 1400.4 / 2097.7 Hz). A resonance would be excited persistently.", ...
           'evidence', "per-second level at each peak frequency, measured 2026-10-11", ...
           'verdict', "DISQUALIFIED"), ...
    struct('finding', "S006 local band flag: 8k-16k +6.44 dB", ...
           'metric', "band minus the line through its two neighbouring bands", ...
           'reason', "Metric artifact. LALAL and the original agree within 0.03 / 0.02 / 0.15 dB across 4k-8k / 8k-16k / 16k-20k, and the -15 dB drop into 16k-20k exists in the original too (recording anti-alias rolloff). The lower neighbour sits in the rolloff, dragging the midpoint down and inflating 8k-16k.", ...
           'evidence', "band comparison LALAL vs original, 8 s windows and 4 s windows, measured 2026-10-11", ...
           'verdict', "DISQUALIFIED")];
writetable(struct2table(disqualified), ...
    fullfile(ctx.outputDir, 's008_disqualified.csv'));
writetable(candidates, fullfile(ctx.outputDir, 's008_candidates.csv'));
fprintf('[S008]   %d disqualification(s) recorded\n', numel(disqualified));

%% ---- Figures -------------------------------------------------------------
fprintf('[S008] figures\n');
stageTimer = tic;

% fig19 - where the candidates sit, and how the count moves with thresholds
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 3, 1, 'TileSpacing', 'compact');
nexttile;
plot(correlation, 'LineWidth', 1.0); hold on;
yline(narrowCorrHigh, 'k--', 'LineWidth', 0.7);
yline(wideCorrLow, 'k:', 'LineWidth', 0.7);
ylim([-0.3, 1.05]); grid on;
xlabel('Second'); ylabel('L/R correlation');
legend('Correlation', sprintf('%.2f narrow', narrowCorrHigh), ...
    sprintf('%.2f wide', wideCorrLow), 'Location', 'southeast');
title(sprintf('Stereo correlation; %d s narrow, %d s wide', ...
    metrics.perSecond.narrowSeconds, metrics.perSecond.wideSeconds));

nexttile;
plot(peakDb, 'LineWidth', 1.0); hold on;
yline(filePeakDb, 'k-', 'LineWidth', 0.8);
yline(filePeakDb - hotWithinDb, 'k--', 'LineWidth', 0.7);
grid on; xlabel('Second'); ylabel('Peak (dBFS)');
legend('Per-second peak', 'File maximum', ...
    sprintf('-%.0f dB', hotWithinDb), 'Location', 'southeast');
title(sprintf('Peak envelope; %d s within %.0f dB of the maximum', ...
    metrics.perSecond.hotSeconds, hotWithinDb));

nexttile;
plot(sensitivity.narrowCorr, sensitivity.narrowSegments, 'o-', 'LineWidth', 1.1);
hold on;
plot(sensitivity.wideCorr, sensitivity.wideSegments, 's-', 'LineWidth', 1.1);
grid on; xlabel('Threshold'); ylabel('Segments found');
legend('Narrow (correlation above)', 'Wide (correlation below)', ...
    'Location', 'north');
title('Threshold sensitivity: candidate count vs cutoff');
contract = moodifylab.figureContract("S008-candidate-map", ...
    Conclusion="Where the surviving time-anchored candidates are, and how sensitive the count is to the chosen thresholds.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["seconds", "dimensionless correlation", "dBFS", "segment count"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT; thresholds are engineering defaults", ...
    Uncertainty="1 s resolution; n=1. The sensitivity panel exists because a single threshold would hide how arbitrary the count is.", ...
    Limitations="These are candidates for LISTENING, not defects. Narrow stereo is frequently intentional. The excerpt set is capped per type and the cap is reported in result.json, never applied silently.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig19_candidate_map", contract);
fprintf('[S008]   figures done in %.1f s\n', toc(stageTimer));

%% ---- Persist -------------------------------------------------------------
metrics.candidates = struct('exportedPairs', exportedCount, ...
    'narrowSegments', size(narrowSegments, 1), ...
    'wideSegments', size(wideSegments, 1), ...
    'hotSegments', size(hotSegments, 1), ...
    'maxExportsPerType', maxExportsPerType, ...
    'capApplied', exportedCount < (size(narrowSegments,1) + size(wideSegments,1) + size(hotSegments,1)), ...
    'auditionDir', auditionDir);
if metrics.candidates.capApplied
    failures(end + 1) = "EXPORT_CAP_APPLIED"; %#ok<AGROW>
end

scalars = {
    'duration_s', frames/fs;
    'file_peak_dbfs', filePeakDb;
    'narrow_seconds', metrics.perSecond.narrowSeconds;
    'wide_seconds', metrics.perSecond.wideSeconds;
    'hot_seconds', metrics.perSecond.hotSeconds;
    'narrow_segments', size(narrowSegments, 1);
    'wide_segments', size(wideSegments, 1);
    'hot_segments', size(hotSegments, 1);
    'exported_pairs', exportedCount;
    'median_abs_band_delta_db', metrics.sameRenderDelta.medianAbsBandDeltaDb;
    'p95_abs_band_delta_db', metrics.sameRenderDelta.p95AbsBandDeltaDb;
    'max_abs_band_delta_db', metrics.sameRenderDelta.maxAbsBandDeltaDb;
    'worst_same_render_window_s', worstWindowSeconds;
    'disqualified_count', numel(disqualified);
    'cap_applied', double(metrics.candidates.capApplied);
    };
writetable(cell2table(scalars, 'VariableNames', {'metric', 'value'}), ...
    fullfile(ctx.outputDir, 's008_summary.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S008";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "This study locates candidates and exports them for human listening. " ...
    "It does not decide what is audible, and it applies no processing."];
result.limitations = [ ...
    "Objective metrics have produced false candidates twice in this project " ...
    "(musical notes read as resonances; a rolloff-band artifact read as a " ...
    "band anomaly), so results here are material for listening, not findings. " ...
    "n=1 per version; the excerpt cap is reported, never silent."];
fprintf('[S008] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S008] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function segments = segmentsFromMask(mask, minSeconds, mergeGapSeconds)
% Turn a per-second logical mask into [start end] second segments, dropping
% anything shorter than minSeconds and joining gaps under mergeGapSeconds.
segments = zeros(0, 2);
count = numel(mask);
index = 1;
while index <= count
    if mask(index)
        startIndex = index;
        while index <= count && mask(index)
            index = index + 1;
        end
        segments(end + 1, :) = [startIndex, index - 1]; %#ok<AGROW>
    else
        index = index + 1;
    end
end
if isempty(segments)
    return;
end
merged = segments(1, :);
for index = 2:size(segments, 1)
    if (segments(index, 1) - merged(end, 2)) <= mergeGapSeconds
        merged(end, 2) = segments(index, 2);
    else
        merged(end + 1, :) = segments(index, :); %#ok<AGROW>
    end
end
durations = merged(:, 2) - merged(:, 1) + 1;
segments = merged(durations >= minSeconds, :);
end

% -------------------------------------------------------------------------
function tableOut = appendExports(tableOut, segments, kind, trace, master, original, fs, outDir, contextSeconds, fadeSeconds, cap)
% Write one audition pair per segment: the master excerpt and the same window
% from the original, faded at both ends so an excerpt never starts on a click.
for index = 1:size(segments, 1)
    if index > cap
        return;
    end
    startSecond = max(1, segments(index, 1) - contextSeconds);
    endSecond = min(size(master, 1) / fs, segments(index, 2) + contextSeconds);
    first = round((startSecond - 1) * fs) + 1;
    last = round(endSecond * fs);
    last = min(last, size(master, 1));
    if last <= first
        continue;
    end
    span = first:last;
    masterExcerpt = applyFades(master(span, :), fs, fadeSeconds);
    originalExcerpt = applyFades(original(span, :), fs, fadeSeconds);
    stem = sprintf('%02d_%s_%05.1f-%05.1f', index, kind, startSecond, endSecond);
    masterName = stem + "_master.wav";
    originalName = stem + "_original.wav";
    audiowrite(fullfile(outDir, char(masterName)), masterExcerpt, fs, 'BitsPerSample', 24);
    audiowrite(fullfile(outDir, char(originalName)), originalExcerpt, fs, 'BitsPerSample', 24);
    traceValue = mean(trace(segments(index, 1):segments(index, 2)));
    row = table(kind, segments(index, 1), segments(index, 2), ...
        segments(index, 2) - segments(index, 1) + 1, traceValue, ...
        string(masterName), string(originalName), ...
        'VariableNames', {'type', 'start_s', 'end_s', 'duration_s', ...
        'mean_trace_value', 'master_excerpt', 'original_excerpt'});
    if isempty(tableOut)
        tableOut = row;
    else
        tableOut = [tableOut; row]; %#ok<AGROW>
    end
end
end

% -------------------------------------------------------------------------
function y = applyFades(x, fs, fadeSeconds)
fadeSamples = min(round(fadeSeconds * fs), floor(size(x, 1) / 2));
if fadeSamples < 1
    y = x;
    return;
end
ramp = (0:(fadeSamples - 1))' / (fadeSamples - 1);
y = x;
y(1:fadeSamples, :) = y(1:fadeSamples, :) .* ramp;
y(end - fadeSamples + 1:end, :) = y(end - fadeSamples + 1:end, :) .* flipud(ramp);
end

% -------------------------------------------------------------------------
function [dbMatrix, starts] = bandPowerPerWindow(audio, fs, edges, windowSeconds)
window = round(windowSeconds * fs);
total = size(audio, 1);
count = floor(total / window);
nBands = size(edges, 1);
taper = hann(window);
frequencies = (0:window-1)' * fs / window;
half = (1:floor(window/2))';
masks = false(numel(half), nBands);
for band = 1:nBands
    masks(:, band) = frequencies(half) >= edges(band,1) & frequencies(half) < edges(band,2);
end
mono = mean(audio, 2);
dbMatrix = zeros(count, nBands);
for index = 1:count
    segment = mono((index-1)*window + (1:window)) .* taper;
    halfPower = abs(fft(segment)).^2;
    halfPower = halfPower(half);
    for band = 1:nBands
        dbMatrix(index, band) = 10*log10(sum(halfPower(masks(:, band))) + eps);
    end
end
starts = ((1:count)' - 1) * windowSeconds;
end

% -------------------------------------------------------------------------
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end
