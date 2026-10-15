function result = study006_lalal_preprocessing_diagnostic(ctx)
%STUDY006_LALAL_PREPROCESSING_DIAGNOSTIC Post-processing readiness report for the LALAL master.
%
%   Purpose: measure everything a post-processing engineer needs BEFORE touching
%   the file, and point at the specific times/frequencies that are likely to
%   need attention. This study MEASURES ONLY. It does not filter, limit,
%   normalise, or write any processed audio.
%
%   What it answers:
%     - how much headroom is left, and is anything already clipped
%     - where the loudness and dynamics sit, and how wide the range is
%     - which bands sit above the song's own median (boom / harsh / dull)
%     - which narrow tones persist (resonance / repair candidates)
%     - how the stereo image behaves and whether it survives a mono fold
%     - a timestamped list of candidate problem spots, ranked
%
%   What it does NOT answer: whether the track sounds good, or what the "right"
%   fix is. Thresholds below are engineering defaults, not calibrated targets.

fprintf('[S006] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
targetPath = fullfile(root, "LALAL重制版_vs_Suno分轨重制版_20261011", ...
                      "自己的神话_LALAL分轨重制_48k24.wav");

% Engineering defaults. Named here so they can be argued with, not buried.
clipThreshold = 0.999;      % |x| at or above this counts as clipped
clipMinRun = 3;             % consecutive samples needed to call it a clip
bandEdges = [20 60; 60 125; 125 250; 250 500; 500 1000; ...
             1000 2000; 2000 4000; 4000 8000; 8000 16000; 16000 20000];
bandLabels = ["20-60"; "60-125"; "125-250"; "250-500"; "500-1k"; ...
              "1k-2k"; "2k-4k"; "4k-8k"; "8k-16k"; "16k-20k"];
balanceWarnDb = 3.0;        % |band - median| above this is flagged
narrowStereoCorr = 0.95;    % sustained L/R correlation above this = narrow
tonalProminenceDb = 6.0;    % peak above local median to count as tonal

failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: load and describe -----------------------------------------
fprintf('[S006] stage 1: load\n');
stageTimer = tic;
[audio, fs] = audioread(targetPath);
if size(audio, 2) < 2
    error('MoodifyLab:S006:NotStereo', 'Expected a stereo master.');
end
audio = audio(:, 1:2);
frameCount = size(audio, 1);
durationSeconds = frameCount / fs;
metrics.source = struct('path', targetPath, 'frames', frameCount, ...
    'sampleRate', fs, 'channels', size(audio, 2), 'durationSeconds', durationSeconds);
fprintf('[S006]   %d frames @ %d Hz = %.3f s\n', frameCount, fs, durationSeconds);
fprintf('[S006]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: headroom, peaks, clipping ---------------------------------
fprintf('[S006] stage 2: headroom / clipping\n');
stageTimer = tic;
mono = mean(audio, 2);
samplePeak = max(abs(audio(:)));
samplePeakDb = 20 * log10(samplePeak + eps);

% True peak via 4x polyphase oversampling (ITU-R BS.1770-4 style). This is an
% approximation of the standard's specified interpolation filter, adequate for
% a headroom check but not a certification measurement.
%
% Oversample one channel at a time: doing both at once allocates ~620 MB for a
% 9.7M-frame master, which is wasteful when the peak is all we keep.
truePeak = 0;
for channel = 1:size(audio, 2)
    upsampled = resample(audio(:, channel), 4, 1);
    truePeak = max(truePeak, max(abs(upsampled)));
    clear upsampled;
end
truePeakDb = 20 * log10(truePeak + eps);

[clipSampleCount, clipRunCount, clipTimes] = ...
    detectClipping(audio, clipThreshold, clipMinRun, fs);
clippedSeconds = 100 * clipSampleCount / numel(audio);

metrics.headroom = struct( ...
    'samplePeakDbfs', samplePeakDb, 'truePeakDbtp', truePeakDb, ...
    'trueMinusSampleDb', truePeakDb - samplePeakDb, ...
    'headroomTo0DbfsDb', -truePeakDb, ...
    'headroomToMinus1DbtpDb', -1 - truePeakDb, ...
    'clipThreshold', clipThreshold, 'clipMinRun', clipMinRun, ...
    'clippedSampleCount', clipSampleCount, 'clippedRunCount', clipRunCount, ...
    'clippedPercent', clippedSeconds, 'firstClipTimes', clipTimes(1:min(5, numel(clipTimes))));
fprintf('[S006]   sample peak %.2f dBFS, true peak %.2f dBTP, headroom to -1 dBTP %.2f dB\n', ...
    samplePeakDb, truePeakDb, -1 - truePeakDb);
fprintf('[S006]   clipped runs %d (%d samples, %.4f%%)\n', ...
    clipRunCount, clipSampleCount, clippedSeconds);
if clipRunCount > 0
    failures(end + 1) = "CLIPPING_PRESENT"; %#ok<AGROW>
end
fprintf('[S006]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: loudness, range, dynamics ---------------------------------
fprintf('[S006] stage 3: loudness / dynamics\n');
stageTimer = tic;
[integratedLufs, loudDetail] = moodifylab.loudnessBs1770(audio, fs);
[~, shortTermDetail] = moodifylab.loudnessBs1770(audio, fs, ...
    'BlockSeconds', 3.0, 'HopSeconds', 1.0);
shortTerm = shortTermDetail.blockLoudness;
[loudnessRange, lraDetail] = ebuLoudnessRange(shortTerm, -70, -20);
plrDb = samplePeakDb - integratedLufs;

shortRms = rmsEnvelopeDb(mono, fs, 1.0);
crestDb = 20*log10(max(abs(mono)) + eps) - 20*log10(sqrt(mean(mono.^2)) + eps);

metrics.loudness = struct( ...
    'integratedLufs', integratedLufs, 'loudnessRangeLu', loudnessRange, ...
    'peakToLoudnessRatioDb', plrDb, ...
    'shortTermMinLufs', min(shortTerm), 'shortTermMaxLufs', max(shortTerm), ...
    'shortTermMedianLufs', median(shortTerm), ...
    'lraAbsoluteGate', lraDetail.absoluteGate, ...
    'lraRelativeGate', lraDetail.relativeGate, ...
    'lraUsedBlocks', lraDetail.usedBlocks);
metrics.dynamics = struct('overallCrestDb', crestDb, ...
    'shortRmsMinDbfs', min(shortRms), 'shortRmsMaxDbfs', max(shortRms), ...
    'shortRmsMedianDbfs', median(shortRms));
fprintf('[S006]   %.2f LUFS, LRA %.2f LU, PLR %.2f dB, crest %.2f dB\n', ...
    integratedLufs, loudnessRange, plrDb, crestDb);
fprintf('[S006]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: spectral balance ------------------------------------------
fprintf('[S006] stage 4: spectral balance\n');
stageTimer = tic;
[lalalBand, ~] = bandPowerPerSecond(audio, fs, bandEdges);
medianBand = median(lalalBand, 1);
bandDeviation = medianBand - median(medianBand);   % relative to the song's own median
[~, worstBand] = max(abs(bandDeviation));

metrics.spectralBalance = struct( ...
    'bandLabels', bandLabels, 'medianBandDb', medianBand, ...
    'deviationFromOwnMedianDb', bandDeviation, ...
    'worstBand', bandLabels(worstBand), ...
    'worstBandDeviationDb', bandDeviation(worstBand), ...
    'warnThresholdDb', balanceWarnDb);
for index = 1:numel(bandLabels)
    flag = "";
    if abs(bandDeviation(index)) >= balanceWarnDb
        flag = "  <-- flagged";
    end
    fprintf('[S006]   %-8s median %7.2f dB  dev %+6.2f dB%s\n', ...
        bandLabels(index), medianBand(index), bandDeviation(index), flag);
end
fprintf('[S006]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: persistent tonal peaks (repair candidates) ----------------
fprintf('[S006] stage 5: tonal peaks\n');
stageTimer = tic;
[tonalFreqs, tonalProminence] = findTonalPeaks(mono, fs, tonalProminenceDb);
metrics.tonalPeaks = struct('count', numel(tonalFreqs), ...
    'frequenciesHz', tonalFreqs, 'prominenceDb', tonalProminence, ...
    'prominenceThresholdDb', tonalProminenceDb);
fprintf('[S006]   %d tonal peak(s) above %.1f dB prominence\n', ...
    numel(tonalFreqs), tonalProminenceDb);
for index = 1:min(8, numel(tonalFreqs))
    fprintf('[S006]     %8.1f Hz  +%.2f dB\n', tonalFreqs(index), tonalProminence(index));
end
fprintf('[S006]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: stereo field and mono compatibility -----------------------
fprintf('[S006] stage 6: stereo / mono\n');
stageTimer = tic;
stereo = perSecondStereo(audio, fs);
monoFoldLossDb = monoCompatibilityDb(audio);
narrowSeconds = sum(stereo.correlation > narrowStereoCorr);
metrics.stereo = struct( ...
    'meanCorrelation', mean(stereo.correlation), ...
    'minCorrelation', min(stereo.correlation), ...
    'maxCorrelation', max(stereo.correlation), ...
    'meanSideMidDb', mean(stereo.sideMidDb), ...
    'secondsAboveNarrowThreshold', narrowSeconds, ...
    'narrowThreshold', narrowStereoCorr, ...
    'monoFoldLossDb', monoFoldLossDb);
fprintf('[S006]   correlation mean %.4f (min %.4f), side/mid %.2f dB\n', ...
    mean(stereo.correlation), min(stereo.correlation), mean(stereo.sideMidDb));
fprintf('[S006]   mono fold loss %.2f dB, %d s above %.2f correlation\n', ...
    monoFoldLossDb, narrowSeconds, narrowStereoCorr);
if narrowSeconds > 5
    failures(end + 1) = "NARROW_STEREO_SPANS"; %#ok<AGROW>
end
fprintf('[S006]   stage 6 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 7: problem spots --------------------------------------------
% One row per second, combining every indicator, so the post-processing pass
% has a timestamped work list instead of a single global verdict.
fprintf('[S006] stage 7: problem spots\n');
stageTimer = tic;
nSeconds = min([size(lalalBand, 1), numel(shortRms), numel(stereo.correlation)]);
bandHeat = abs(lalalBand(1:nSeconds, :) - medianBand);
perSecondBand = max(bandHeat, [], 2);
nearPeakDb = 20*log10(localPeakPerSecond(mono, fs, nSeconds) + eps);

spots = table();
spots.second = (1:nSeconds)';
spots.time_s = (1:nSeconds)';
spots.near_peak_dbfs = nearPeakDb;
spots.short_rms_dbfs = shortRms(1:nSeconds);
spots.lr_correlation = stereo.correlation(1:nSeconds);
spots.side_mid_db = stereo.sideMidDb(1:nSeconds);
spots.max_band_deviation_db = perSecondBand;
spots.flag_hot = nearPeakDb > -1.0;
spots.flag_narrow = stereo.correlation(1:nSeconds) > narrowStereoCorr;
spots.flag_band = perSecondBand > balanceWarnDb;
spots.flag_count = spots.flag_hot + spots.flag_narrow + spots.flag_band;

% Keep a time-ordered copy BEFORE sorting. The figure plots flags against
% seconds, so using the sorted table there would draw rank order as if it were
% a timeline.
flagCountBySecond = spots.flag_count;

spots = sortrows(spots, 'flag_count', 'descend');
writetable(spots, fullfile(ctx.outputDir, 's006_problem_spots.csv'));

flaggedSeconds = sum(spots.flag_count > 0);
metrics.problemSpots = struct( ...
    'totalSeconds', nSeconds, 'flaggedSeconds', flaggedSeconds, ...
    'hotSeconds', sum(spots.flag_hot), 'narrowSeconds', sum(spots.flag_narrow), ...
    'bandSeconds', sum(spots.flag_band), ...
    'worstSecond', spots.second(1), 'worstFlagCount', spots.flag_count(1), ...
    'nearPeakThresholdDbfs', -1.0);
fprintf('[S006]   %d / %d s flagged; worst at %d s with %d flags\n', ...
    flaggedSeconds, nSeconds, spots.second(1), spots.flag_count(1));
fprintf('[S006]   stage 7 done in %.1f s\n', toc(stageTimer));

%% ---- Figures -------------------------------------------------------------
fprintf('[S006] figures\n');
stageTimer = tic;

% fig12 - headroom and clipping
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
[peakEnvelopeDb, peakTimeSec] = peakEnvelope(mono, fs, 0.020);
plot(peakTimeSec, peakEnvelopeDb, 'LineWidth', 0.9);
hold on;
yline(-1, 'k:', 'LineWidth', 0.7);
grid on; xlabel('Time (s)'); ylabel('Peak (dBFS, 20 ms)');
legend('Peak envelope', '-1 dBFS', 'Location', 'southeast');
title(sprintf('Peak envelope. Sample peak %.2f dBFS, true peak %.2f dBTP', ...
    samplePeakDb, truePeakDb));
nexttile;
plot(peakTimeSec, peakEnvelopeDb, 'LineWidth', 0.9); hold on;
if ~isempty(clipTimes)
    plot(clipTimes, interp1(peakTimeSec, peakEnvelopeDb, clipTimes, 'nearest', 'extrap'), ...
        'v', 'MarkerSize', 4, 'LineStyle', 'none');
end
xlim([0, min(60, peakTimeSec(end))]);
grid on; xlabel('Time (s, first 60 s shown)'); ylabel('Peak (dBFS, 20 ms)');
legend('Peak envelope', 'Clipped run', 'Location', 'southeast');
title(sprintf('Clipping detail: %d run(s), %.4f%% of samples', clipRunCount, clippedSeconds));
contract = moodifylab.figureContract("S006-headroom-clipping", ...
    Conclusion="How much headroom remains and whether any samples are already clipped.", ...
    EvidenceRole="measurement", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["dBFS", "dBTP", "seconds", "percent"], ...
    CalibrationStatus="TRUE PEAK IS 4x POLYPHASE OVERSAMPLING, not the BS.1770 certification filter", ...
    Uncertainty="Deterministic given the file.", ...
    Limitations="A clip detector sees flat-topped samples; it cannot tell an intentional mastered ceiling from a defect. Sample peak is not true peak and vice versa.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig12_headroom_clipping", contract);

% fig13 - spectral balance
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 1, 2, 'TileSpacing', 'compact');
nexttile;
barh(medianBand);
set(gca, 'YTick', 1:numel(bandLabels), 'YTickLabel', cellstr(bandLabels));
xlabel('Median band power (dB, uncalibrated)'); ylabel('Band (Hz)');
grid on; title('Median band level');
nexttile;
barh(bandDeviation);
set(gca, 'YTick', 1:numel(bandLabels), 'YTickLabel', cellstr(bandLabels));
hold on; xline(0, 'k:', 'LineWidth', 0.7);
xline(balanceWarnDb, 'k--', 'LineWidth', 0.7); xline(-balanceWarnDb, 'k--', 'LineWidth', 0.7);
xlabel('Deviation from the song''s own median (dB)'); ylabel('Band (Hz)');
grid on; title(sprintf('Band deviation; dashed = +/-%.1f dB flag', balanceWarnDb));
contract = moodifylab.figureContract("S006-spectral-balance", ...
    Conclusion="Which bands sit above or below this song's own median, i.e. where tonal balance may need attention.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["hertz", "decibels, relative to the song's own median band level"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT", ...
    Uncertainty="NOT_REPORTED_ACROSS_RENDERS: n=1.", ...
    Limitations="Deviation from the song's own median is NOT a target curve. A band far from the median may be exactly what the arrangement needs. Thresholds are engineering defaults.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig13_spectral_balance", contract);

% fig14 - loudness and dynamics over time
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
plot((shortTermDetail.blockStarts - 1)/fs, shortTerm, 'LineWidth', 1.0);
hold on; yline(integratedLufs, 'k--', 'LineWidth', 0.8);
grid on; xlabel('Time (s)'); ylabel('Short-term loudness (LUFS)');
legend('Short-term (3 s)', 'Integrated', 'Location', 'southeast');
title(sprintf('Loudness. Integrated %.2f LUFS, LRA %.2f LU, PLR %.2f dB', ...
    integratedLufs, loudnessRange, plrDb));
nexttile;
histogram(shortTerm, 30);
xlabel('Short-term loudness (LUFS)'); ylabel('Count');
grid on; title('Distribution of 3 s loudness');
contract = moodifylab.figureContract("S006-loudness-dynamics", ...
    Conclusion="The loudness level, how wide its range is, and how much peak-to-loudness margin exists for a limiter.", ...
    EvidenceRole="measurement", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["LUFS", "LU", "decibels", "seconds"], ...
    CalibrationStatus="ITU-R BS.1770-4 + EBU Tech 3342 implemented in this bundle", ...
    Uncertainty="Gate thresholds are the standard defaults (-70 LUFS absolute, -20 LU relative).", ...
    Limitations="LRA and PLR describe the existing master; they do not prescribe a target. A wide LRA is not better than a narrow one.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig14_loudness_dynamics", contract);

% fig15 - stereo field and mono compatibility
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
plot(stereo.correlation, 'LineWidth', 1.0); hold on;
yline(narrowStereoCorr, 'k--', 'LineWidth', 0.7);
ylim([-0.2, 1.02]);
grid on; xlabel('Window (1 s)'); ylabel('L/R correlation');
legend('Correlation', sprintf('%.2f narrow threshold', narrowStereoCorr), 'Location', 'southeast');
title(sprintf('Stereo correlation; %d s above threshold', narrowSeconds));
nexttile;
plot(stereo.sideMidDb, 'LineWidth', 1.0);
grid on; xlabel('Window (1 s)'); ylabel('Side / mid (dB)');
title(sprintf('Stereo width; mono fold loses %.2f dB', monoFoldLossDb));
contract = moodifylab.figureContract("S006-stereo-mono", ...
    Conclusion="How the stereo image behaves over time and how much is lost when the mix is folded to mono.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["dimensionless correlation", "decibels", "seconds"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT", ...
    Uncertainty="1 s windows; n=1.", ...
    Limitations="High correlation is not automatically a defect -- mono-leaning material is often intentional. The mono fold comparison is a level change, not a phase-cancellation measurement.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig15_stereo_mono", contract);

% fig16 - problem map
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
imagesc(1:nSeconds, 1:numel(bandLabels), bandHeat.');
set(gca, 'YTick', 1:numel(bandLabels), 'YTickLabel', cellstr(bandLabels));
xlabel('Time (s)'); ylabel('Band (Hz)');
cb = colorbar; cb.Label.String = '|band - median| (dB)';
colormap(gca, hot(256)); caxis([0, max(6, balanceWarnDb * 2)]);
title('Per-second band deviation magnitude');
nexttile;
stem(1:nSeconds, flagCountBySecond, 'Marker', 'none');
ylim([0, max(3, max(flagCountBySecond) + 1)]);
grid on; xlabel('Time (s)'); ylabel('Flags per second');
title(sprintf('Flag counts by second (%d of %d s flagged)', flaggedSeconds, nSeconds));
contract = moodifylab.figureContract("S006-problem-map", ...
    Conclusion="A time-anchored map of where the diagnostic indicators concentrate, for planning a post-processing pass.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["seconds", "hertz", "decibels", "flag count"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT; thresholds are engineering defaults", ...
    Uncertainty="1 s / one-band resolution; n=1.", ...
    Limitations="Flags mark statistical outliers within this song, not defects. Nothing here says what to change or by how much.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig16_problem_map", contract);
fprintf('[S006]   figures done in %.1f s\n', toc(stageTimer));

%% ---- Persist -------------------------------------------------------------
writetable(table(bandLabels, medianBand(:), bandDeviation(:), ...
    'VariableNames', {'band_hz', 'median_db', 'deviation_from_median_db'}), ...
    fullfile(ctx.outputDir, 's006_band_balance.csv'));
if ~isempty(tonalFreqs)
    writetable(table(tonalFreqs(:), tonalProminence(:), ...
        'VariableNames', {'frequency_hz', 'prominence_db'}), ...
        fullfile(ctx.outputDir, 's006_tonal_peaks.csv'));
end

scalars = {
    'source_frames', frameCount; 'sample_rate_hz', fs; 'duration_s', durationSeconds;
    'sample_peak_dbfs', samplePeakDb; 'true_peak_dbtp', truePeakDb;
    'headroom_to_minus1_dbtp_db', -1 - truePeakDb;
    'clip_run_count', clipRunCount; 'clipped_percent', clippedSeconds;
    'integrated_lufs', integratedLufs; 'loudness_range_lu', loudnessRange;
    'plr_db', plrDb; 'overall_crest_db', crestDb;
    'mean_lr_correlation', mean(stereo.correlation);
    'min_lr_correlation', min(stereo.correlation);
    'mean_side_mid_db', mean(stereo.sideMidDb);
    'mono_fold_loss_db', monoFoldLossDb;
    'narrow_seconds', narrowSeconds; 'flagged_seconds', flaggedSeconds;
    'tonal_peak_count', numel(tonalFreqs);
    };
writetable(cell2table(scalars, 'VariableNames', {'metric', 'value'}), ...
    fullfile(ctx.outputDir, 's006_diagnostics.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S006";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "This is a pre-processing MEASUREMENT of one file. It does not judge " ...
    "quality, does not prescribe a fix, and applies no processing."];
result.limitations = [ ...
    "Thresholds are engineering defaults, not calibrated targets. Band " ...
    "deviation is measured against the song's own median, which is not a " ...
    "target curve. True peak uses 4x polyphase oversampling rather than the " ...
    "BS.1770 certification filter."];
fprintf('[S006] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S006] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function [sampleCount, runCount, runTimesSeconds] = detectClipping(audio, threshold, minRun, fs)
% Count flat-topped runs at or above the threshold, on the louder channel.
% Run times are returned in SECONDS so they can be plotted against time axes;
% returning raw sample indices here previously mismatched every time axis.
magnitude = max(abs(audio), [], 2);
isClipped = magnitude >= threshold;
runCount = 0;
runTimesSeconds = [];
sampleCount = 0;
index = 1;
total = numel(isClipped);
while index <= total
    if isClipped(index)
        runStart = index;
        while index <= total && isClipped(index)
            index = index + 1;
        end
        runLength = index - runStart;
        sampleCount = sampleCount + runLength;
        if runLength >= minRun
            runCount = runCount + 1;
            runTimesSeconds(end + 1) = (runStart - 1) / fs; %#ok<AGROW>
        end
    else
        index = index + 1;
    end
end
end

% -------------------------------------------------------------------------
function [rangeLu, detail] = ebuLoudnessRange(shortTermLufs, absoluteGate, relativeGate)
% EBU Tech 3342 loudness range.
values = shortTermLufs(isfinite(shortTermLufs));
aboveAbsolute = values(values > absoluteGate);
if numel(aboveAbsolute) < 2
    rangeLu = 0;
    detail = struct('absoluteGate', absoluteGate, 'relativeGate', NaN, 'usedBlocks', 0);
    return;
end
meanPowerDb = 10 * log10(mean(10.^(aboveAbsolute / 10)) + eps);
relativeThreshold = meanPowerDb + relativeGate;
kept = aboveAbsolute(aboveAbsolute > relativeThreshold);
if numel(kept) < 2
    kept = aboveAbsolute;
end
rangeLu = prctile(kept, 95) - prctile(kept, 10);
detail = struct('absoluteGate', absoluteGate, ...
    'relativeGate', relativeThreshold, 'usedBlocks', numel(kept));
end

% -------------------------------------------------------------------------
function [dbMatrix, seconds] = bandPowerPerSecond(audio, fs, edges, windowSeconds)
if nargin < 4
    windowSeconds = 1.0;
end
window = round(windowSeconds * fs);
total = size(audio, 1);
segments = floor(total / window);
nBands = size(edges, 1);
taper = hann(window);
frequencies = (0:window-1)' * fs / window;
half = (1:floor(window/2))';
masks = false(numel(half), nBands);
for band = 1:nBands
    masks(:, band) = frequencies(half) >= edges(band,1) & frequencies(half) < edges(band,2);
end
mono = mean(audio, 2);
dbMatrix = zeros(segments, nBands);
for index = 1:segments
    segment = mono((index-1)*window + (1:window)) .* taper;
    halfPower = abs(fft(segment)).^2;
    halfPower = halfPower(half);
    for band = 1:nBands
        dbMatrix(index, band) = 10*log10(sum(halfPower(masks(:, band))) + eps);
    end
end
seconds = (1:segments)';
end

% -------------------------------------------------------------------------
function [freqs, prominence] = findTonalPeaks(mono, fs, prominenceDb)
% Persistent narrow peaks in the long-term spectrum: resonance / repair hints.
[power, freqs] = pwelch(mono, hann(16384), 8192, 16384, fs);
spectrumDb = 10 * log10(power + eps);
window = 41;
localMedian = movmedian(spectrumDb, window);
deviation = spectrumDb - localMedian;
isPeak = false(size(deviation));
for index = (window+1):(numel(deviation) - window)
    neighbourhood = deviation(index-window:index+window);
    if deviation(index) == max(neighbourhood) && deviation(index) >= prominenceDb
        isPeak(index) = true;
    end
end
isPeak(freqs < 40) = false;          % ignore the K-weighting / DC region
candidateIndex = find(isPeak);
prominence = deviation(candidateIndex);
freqs = freqs(candidateIndex);
[freqs, order] = sort(freqs);
prominence = prominence(order);
end

% -------------------------------------------------------------------------
function d = perSecondStereo(audio, fs)
window = round(1.0 * fs);
segments = floor(size(audio, 1) / window);
d = struct();
d.correlation = zeros(segments, 1);
d.sideMidDb = zeros(segments, 1);
for index = 1:segments
    span = (index-1)*window + (1:window);
    left = audio(span, 1);
    right = audio(span, 2);
    mid = 0.5 * (left + right);
    side = 0.5 * (left - right);
    if std(left) < eps || std(right) < eps
        d.correlation(index) = 1;
    else
        matrix = corrcoef(left, right);
        d.correlation(index) = matrix(1, 2);
    end
    d.sideMidDb(index) = 10*log10((mean(side.^2) + eps) / (mean(mid.^2) + eps));
end
end

% -------------------------------------------------------------------------
function lossDb = monoCompatibilityDb(audio)
% Level change when both channels are summed to mono, relative to the louder
% channel. A pure level comparison, not a phase-cancellation test.
monoFold = 0.5 * (audio(:, 1) + audio(:, 2));
stereoRms = sqrt(mean(audio(:).^2));
monoRms = sqrt(mean(monoFold.^2));
lossDb = 20*log10(monoRms / (stereoRms + eps) + eps);
end

% -------------------------------------------------------------------------
function y = rmsEnvelopeDb(mono, fs, windowSeconds)
window = round(windowSeconds * fs);
segments = floor(numel(mono) / window);
y = zeros(segments, 1);
for index = 1:segments
    span = (index-1)*window + (1:window);
    y(index) = 20*log10(sqrt(mean(mono(span).^2)) + eps);
end
end

% -------------------------------------------------------------------------
function [envelopeDb, timeSec] = peakEnvelope(mono, fs, windowSeconds)
window = round(windowSeconds * fs);
hop = window;
segments = floor(numel(mono) / window);
envelopeDb = zeros(segments, 1);
for index = 1:segments
    span = (index-1)*hop + (1:window);
    envelopeDb(index) = 20*log10(max(abs(mono(span))) + eps);
end
timeSec = ((1:segments)' - 0.5) * windowSeconds;
end

% -------------------------------------------------------------------------
function peaks = localPeakPerSecond(mono, fs, nSeconds)
window = round(1.0 * fs);
peaks = zeros(nSeconds, 1);
for index = 1:nSeconds
    span = (index-1)*window + (1:window);
    if span(end) > numel(mono)
        break;
    end
    peaks(index) = max(abs(mono(span)));
end
end

% -------------------------------------------------------------------------
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end
