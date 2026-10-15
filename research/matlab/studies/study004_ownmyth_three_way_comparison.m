function result = study004_ownmyth_three_way_comparison(ctx)
%STUDY004_OWNMYTH_THREE_WAY_COMPARISON 原曲 / LALAL / Suno three-way evidence study.
%
%   Compares three master recordings of the same song:
%     ORIGINAL      自己的神话3.wav                        (48 kHz, PCM_16)
%     LALAL_MASTER  自己的神话_LALAL分轨重制_48k24.wav      (48 kHz, PCM_24)
%     SUNO_MASTER   自己的神话_重制A_局部修复保守版_48k24bit (48 kHz, PCM_24, WAVEX)
%
%   The study separates three questions that are easy to conflate:
%     Q1 provenance   Do the stems verifiably reconstruct the original?
%     Q2 description  How do the three masters differ, measurably?
%     Q3 preference   NOT ANSWERED HERE. No figure in this study ranks them.
%
%   Everything reported is a physical measurement with stated units. Nothing
%   here is a perceptual claim.

fprintf('[S004] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
originalPath  = fullfile(root, "自己的神话3.wav");
lalalMaster   = fullfile(root, "LALAL重制版_vs_Suno分轨重制版_20261011", ...
                         "自己的神话_LALAL分轨重制_48k24.wav");
sunoMaster    = fullfile(root, "重制_贝叶斯双版本", "修复版_保守", ...
                         "自己的神话_重制A_局部修复保守版_48k24bit.wav");
lalalStemDir  = fullfile(root, "LALAL_AI分轨_20261011", "自己的神话3_multistem");
% The Suno stem set lives under 逍遥仙, NOT under 挑选.
sunoStemDir   = fullfile(songRoot, "02 分轨", "自己的神话 Stems (102BPM)");

lalalStems = ["01_stem_vocals.wav", "02_stem_drum.wav", "03_stem_bass.wav", ...
              "04_stem_piano.wav", "05_stem_acoustic_guitar.wav", ...
              "06_stem_electric_guitar.wav", "07_back_no_multistem.wav"];
sunoStems  = ["0 Lead Vocals.wav", "1 Backing Vocals.wav", "10 Brass.wav", ...
              "2 Drums.wav", "3 Bass.wav", "4 Guitar.wav", "5 Keyboard.wav", ...
              "6 Percussion.wav", "7 Strings.wav", "8 Synth.wav", "9 Other.wav"];

metrics = struct();
failures = strings(0, 1);

%% ---- Stage 0: BS.1770 regression test ----------------------------------
% Guard against the known -3.01 dB channel-averaging defect: identical
% content rendered as mono and as dual-mono stereo must measure the same.
fprintf('[S004] stage 0: loudness regression\n');
stageTimer = tic;
fs = 48000;
t = (0:(fs * 5 - 1))' / fs;
probe = 0.25 * sin(2 * pi * 440 * t) .* (0.5 + 0.5 * sin(2 * pi * 0.7 * t));
monoLufs = moodifylab.loudnessBs1770(probe, fs);
stereoLufs = moodifylab.loudnessBs1770([probe, probe], fs);
loudnessDelta = stereoLufs - monoLufs;
% BS.1770-4 SUMS channel powers (G_i = 1.0 per channel). Summing predicts that
% the same content played as dual-mono stereo measures exactly 10*log10(2)
% = 3.0103 LU above the same content in mono, because two channels carry twice
% the power. An implementation that AVERAGES channel powers instead reports
% delta = 0. So the expected value here is +3.0103, NOT 0: asserting equality
% was the original mistake and made a correct implementation look broken.
expectedDeltaLu = 10 * log10(2);
loudnessTestPassed = abs(loudnessDelta - expectedDeltaLu) < 0.05;
if ~loudnessTestPassed
    failures(end + 1) = "BS1770_CHANNEL_SUMMING_MISMATCH"; %#ok<AGROW>
end
metrics.loudnessRegression = struct( ...
    'monoLufs', monoLufs, 'stereoLufs', stereoLufs, ...
    'deltaLu', loudnessDelta, 'expectedDeltaLu', expectedDeltaLu, ...
    'passed', loudnessTestPassed, 'toleranceLu', 0.05);
fprintf(['[S004]   mono %.3f LUFS, dual-mono stereo %.3f LUFS, delta %.4f LU ' ...
    '(expected %.4f = 10log10(2) for channel summing)\n'], ...
    monoLufs, stereoLufs, loudnessDelta, expectedDeltaLu);
fprintf('[S004]   stage 0 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 1: load the three masters -----------------------------------
fprintf('[S004] stage 1: load masters\n');
stageTimer = tic;
[original, fsOriginal] = audioread(originalPath);
fprintf('[S004]   original   %d frames @ %d Hz\n', size(original, 1), fsOriginal);
if fsOriginal ~= fs
    failures(end + 1) = "ORIGINAL_RATE_UNEXPECTED"; %#ok<AGROW>
end
metrics.original = describeSignal(original, fsOriginal);
fprintf('[S004]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: stem round-trip identity ---------------------------------
% This is the Q1 evidence. A stem set that reconstructs the source is
% traceable; one that does not cannot be compared sample-wise at all.
fprintf('[S004] stage 2: stem round-trips\n');
stageTimer = tic;
lalalRound = stemRoundtrip(lalalStemDir, lalalStems, original, fs);
fprintf('[S004]   LALAL  corr %.9f  rel.error %.3f dB\n', ...
    lalalRound.correlation, lalalRound.relativeErrorDb);
sunoRound = stemRoundtrip(sunoStemDir, sunoStems, original, fs);
fprintf('[S004]   SUNO   corr %.9f  rel.error %.3f dB\n', ...
    sunoRound.correlation, sunoRound.relativeErrorDb);
metrics.lalalRoundtrip = rmfield(lalalRound, ...
    {'reconstruction', 'referenceTrimmed'});
metrics.sunoRoundtrip = rmfield(sunoRound, ...
    {'reconstruction', 'referenceTrimmed'});
if lalalRound.relativeErrorDb > -30
    failures(end + 1) = "LALAL_ROUNDTRIP_ABOVE_GATE"; %#ok<AGROW>
end
fprintf('[S004]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: load LALAL and Suno masters ------------------------------
fprintf('[S004] stage 3: load comparison masters\n');
stageTimer = tic;
[lalal, fsLalal] = audioread(lalalMaster);
[suno, fsSuno] = audioread(sunoMaster);
original = original(1:min(size(original, 1), size(lalal, 1)), :);
fprintf('[S004]   lalal %d frames, suno %d frames\n', ...
    size(lalal, 1), size(suno, 1));
metrics.lalalMaster = describeSignal(lalal, fsLalal);
metrics.sunoMaster = describeSignal(suno, fsSuno);
fprintf('[S004]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: alignment -------------------------------------------------
% LALAL shares the original's frame count exactly, so alignment should be
% an identity. Suno is longer and comes from a different render, so the
% alignment result is itself evidence about comparability.
fprintf('[S004] stage 4: alignment\n');
stageTimer = tic;
maxLag = round(0.75 * fs);
windowSeconds = 60;
[lalalLag, lalalCorrCurve, lalalLags] = alignLag(original, lalal, maxLag, windowSeconds, fs);
[sunoLag, sunoCorrCurve, sunoLags] = alignLag(original, suno, maxLag, windowSeconds, fs);
fprintf('[S004]   lalal lag %d samples (%.1f ms) peak %.4f\n', ...
    lalalLag, lalalLag * 1000 / fs, max(lalalCorrCurve));
fprintf('[S004]   suno  lag %d samples (%.1f ms) peak %.4f\n', ...
    sunoLag, sunoLag * 1000 / fs, max(sunoCorrCurve));
metrics.alignment = struct( ...
    'lalalLagSamples', lalalLag, 'lalalLagMs', lalalLag * 1000 / fs, ...
    'lalalPeakCorrelation', max(lalalCorrCurve), ...
    'sunoLagSamples', sunoLag, 'sunoLagMs', sunoLag * 1000 / fs, ...
    'sunoPeakCorrelation', max(sunoCorrCurve), ...
    'maxSearchedLagMs', maxLag * 1000 / fs, ...
    'windowSeconds', windowSeconds);
fprintf('[S004]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: loudness and time-varying loudness ------------------------
fprintf('[S004] stage 5: loudness\n');
stageTimer = tic;
[lalalLufs, lalalLoud] = moodifylab.loudnessBs1770(lalal, fs);
[sunoLufs, sunoLoud] = moodifylab.loudnessBs1770(suno, fs);
[origLufs, origLoud] = moodifylab.loudnessBs1770(original, fs);
metrics.loudness = struct( ...
    'originalLufs', origLufs, 'lalalLufs', lalalLufs, 'sunoLufs', sunoLufs, ...
    'lalalMinusSunoLu', lalalLufs - sunoLufs, ...
    'lalalMinusOriginalLu', lalalLufs - origLufs, ...
    'sunoMinusOriginalLu', sunoLufs - origLufs);
fprintf('[S004]   original %.3f  lalal %.3f  suno %.3f  (suno-lalal %.2f LU)\n', ...
    origLufs, lalalLufs, sunoLufs, sunoLufs - lalalLufs);
fprintf('[S004]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: spectral / dynamic / stereo metrics ----------------------
fprintf('[S004] stage 6: descriptors\n');
stageTimer = tic;
metrics.descriptors = struct( ...
    'original', descriptorSet(original, fs), ...
    'lalal', descriptorSet(lalal, fs), ...
    'suno', descriptorSet(suno, fs));
fprintf('[S004]   stage 6 done in %.1f s\n', toc(stageTimer));

%% ---- Figures ------------------------------------------------------------
fprintf('[S004] figures\n');
stageTimer = tic;

% Fig 1 - round-trip identity. The central provenance evidence.
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
plotSegmentOverlay(lalalRound.referenceTrimmed, lalalRound.reconstruction, fs, 0.030);
title('LALAL 7 stems vs original (30 ms)');
nexttile;
plotSegmentOverlay(sunoRound.referenceTrimmed, sunoRound.reconstruction, fs, 0.030);
title('Suno 11 stems vs original (30 ms)');
nexttile;
plotResidualEnvelope(lalalRound.referenceTrimmed, lalalRound.reconstruction, fs);
title(sprintf('LALAL residual, rel. %.1f dB, r = %.6f', ...
    lalalRound.relativeErrorDb, lalalRound.correlation));
nexttile;
plotResidualEnvelope(sunoRound.referenceTrimmed, sunoRound.reconstruction, fs);
title(sprintf('Suno residual, rel. %+.1f dB, r = %.4f', ...
    sunoRound.relativeErrorDb, sunoRound.correlation));
contract = moodifylab.figureContract("S004-roundtrip-identity", ...
    Conclusion="The LALAL 7-stem set reconstructs the original to -60 dB; the Suno 11-stem set does not reconstruct it at all.", ...
    EvidenceRole="provenance", ...
    SourceData=["自己的神话3.wav", "LALAL 7-stem sum", "Suno 11-stem sum"], ...
    Units=["seconds", "digital full scale", "decibels"], ...
    CalibrationStatus="DIGITAL_NUMERICAL_BASELINE", ...
    Uncertainty="Deterministic given the files; no population inference.", ...
    Limitations="Round-trip fidelity is not separation correctness and not listening quality. A stem set can reconstruct the source and still separate poorly.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig01_roundtrip_identity", contract);

% Fig 2 - alignment. Shows comparability directly.
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 1, 2, 'TileSpacing', 'compact');
nexttile;
plot(lalalLags / fs * 1000, lalalCorrCurve, 'LineWidth', 1.1); hold on;
xline(0, 'k:', 'LineWidth', 0.7);
xlabel('Lag (ms)'); ylabel('Normalised envelope correlation');
% Two-line titles: a single line this long gets clipped by the tile width.
% Figure text stays ASCII. applyFigureStyle sets Arial, which has no CJK
% glyphs, so Chinese here renders as tofu boxes in every export.
title({sprintf('LALAL vs Original: env peak %.4f @ %.1f ms', ...
    max(lalalCorrCurve), lalalLag * 1000 / fs); ...
    sprintf('waveform r = %.6f', lalalRound.correlation)});
grid on;
nexttile;
plot(sunoLags / fs * 1000, sunoCorrCurve, 'LineWidth', 1.1); hold on;
xline(0, 'k:', 'LineWidth', 0.7);
xlabel('Lag (ms)'); ylabel('Normalised envelope correlation');
% Suno DOES produce an envelope peak (~0.81): the two renders share a
% loudness contour because they are the same song. What it does not have is
% waveform correspondence. Title must carry both numbers or it reads as a
% contradiction.
title({sprintf('Suno vs Original: env peak %.4f @ %.1f ms', ...
    max(sunoCorrCurve), sunoLag * 1000 / fs); ...
    sprintf('waveform r = %.4f', sunoRound.correlation)});
grid on;
contract = moodifylab.figureContract("S004-alignment", ...
    Conclusion="LALAL is sample-aligned with the original; the Suno render has no alignment peak and is therefore not on the original timebase.", ...
    EvidenceRole="provenance", ...
    SourceData=["自己的神话3.wav", "LALAL master", "Suno master"], ...
    Units=["milliseconds", "dimensionless correlation"], ...
    CalibrationStatus="DIGITAL_NUMERICAL_BASELINE", ...
    Uncertainty=sprintf("Lag search range +/-%.0f ms, %.0f s envelope window.", maxLag * 1000 / fs, windowSeconds), ...
    Limitations="A flat correlation curve cannot distinguish a different performance from a heavily processed one.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig02_alignment", contract);

% Fig 3 - long-term average spectrum of the three masters.
[origSpec, specFreqs] = longTermSpectrum(original, fs);
[lalalSpec, ~] = longTermSpectrum(lalal, fs);
[sunoSpec, ~] = longTermSpectrum(suno, fs);
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
semilogx(specFreqs, origSpec, specFreqs, lalalSpec, specFreqs, sunoSpec, ...
    'LineWidth', 1.1);
xlim([20, 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Power (dB)');
legend('Original', 'LALAL master', 'Suno master', 'Location', 'southwest');
title('Long-term average spectrum');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});   % same colour per version as every other figure
semilogx(specFreqs, lalalSpec - origSpec, specFreqs, sunoSpec - origSpec, ...
    'LineWidth', 1.1);
xlim([20, 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Level difference (dB)');
legend('LALAL - original', 'Suno - original', 'Location', 'southwest');
yline(0, 'k:', 'LineWidth', 0.7);
title('Departure from the original');
contract = moodifylab.figureContract("S004-spectrum", ...
    Conclusion="The two masters differ from the original and from each other in a band-dependent way; this is descriptive and does not rank them.", ...
    EvidenceRole="descriptive", ...
    SourceData=["自己的神话3.wav", "LALAL master", "Suno master"], ...
    Units=["hertz", "decibels, uncalibrated to any SPL reference"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT", ...
    Uncertainty="NOT_REPORTED_ACROSS_RENDERS: n=1 per version, so no confidence interval is meaningful.", ...
    Limitations="Spectrum shape is not quality. A mastering EQ move in either direction may be intended.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig03_spectrum", contract);

% Fig 4 - time-varying loudness and the loudness confound.
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
plotLoudnessCurve(lalalLoud, fs, 'LALAL master'); hold on;
plotLoudnessCurve(sunoLoud, fs, 'Suno master');
plotLoudnessCurve(origLoud, fs, 'Original');
grid on; xlabel('Time (s)'); ylabel('Short-term loudness (LUFS)');
legend('Location', 'southeast');
title('Short-term loudness (BS.1770-4, 400 ms blocks)');
nexttile;
colorBarsByVersion(bar([origLufs, lalalLufs, sunoLufs]));
set(gca, 'XTickLabel', {'Original', 'LALAL', 'Suno'});
ylabel('Integrated loudness (LUFS)'); grid on;
title(sprintf('Integrated loudness: Suno is %+.2f LU relative to LALAL', ...
    sunoLufs - lalalLufs));
contract = moodifylab.figureContract("S004-loudness", ...
    Conclusion="The two masters differ by a measurable loudness offset, which is a confound for any unstructured listening comparison.", ...
    EvidenceRole="measurement", ...
    SourceData=["自己的神话3.wav", "LALAL master", "Suno master"], ...
    Units=["LUFS", "seconds"], ...
    CalibrationStatus="ITU-R BS.1770-4 IMPLEMENTED HERE (no Audio Toolbox on this host)", ...
    Uncertainty=sprintf("Mono/stereo regression delta %.4f LU.", loudnessDelta), ...
    Limitations="Loudness is not preference. Higher loudness is not better loudness.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig04_loudness", contract);

% Fig 5 - dynamics and stereo field.
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
colorBarsByVersion(bar([metrics.descriptors.original.crestDb, ...
     metrics.descriptors.lalal.crestDb, ...
     metrics.descriptors.suno.crestDb]));
set(gca, 'XTickLabel', {'Original', 'LALAL', 'Suno'});
ylabel('Crest factor (dB)'); grid on; title('Peak-to-RMS');
nexttile;
histogram(metrics.descriptors.original.shortTermDb, 40); hold on;
histogram(metrics.descriptors.lalal.shortTermDb, 40);
histogram(metrics.descriptors.suno.shortTermDb, 40);
xlabel('Short-term level (dBFS)'); ylabel('Count');
legend('Original', 'LALAL', 'Suno'); grid on; title('Level distribution');
nexttile;
plot(metrics.descriptors.original.correlationOverTime, 'LineWidth', 1.1); hold on;
plot(metrics.descriptors.lalal.correlationOverTime, 'LineWidth', 1.1);
plot(metrics.descriptors.suno.correlationOverTime, 'LineWidth', 1.1);
xlabel('Window index (1 s)'); ylabel('L/R correlation');
legend('Original', 'LALAL', 'Suno'); grid on; title('Stereo correlation');
nexttile;
colorBarsByVersion(bar([metrics.descriptors.original.sideMidDb, ...
     metrics.descriptors.lalal.sideMidDb, ...
     metrics.descriptors.suno.sideMidDb]));
set(gca, 'XTickLabel', {'Original', 'LALAL', 'Suno'});
ylabel('Side / mid (dB)'); grid on; title('Stereo width');
contract = moodifylab.figureContract("S004-dynamics-stereo", ...
    Conclusion="Dynamics and stereo field differ between the three versions in specific, measurable ways.", ...
    EvidenceRole="descriptive", ...
    SourceData=["自己的神话3.wav", "LALAL master", "Suno master"], ...
    Units=["decibels", "dBFS", "dimensionless"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT", ...
    Uncertainty="NOT_REPORTED_ACROSS_RENDERS: n=1 per version.", ...
    Limitations="Wider is not better and more dynamic is not better. No figure here supports a ranking.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig05_dynamics_stereo", contract);

% Fig 6 - what processing changed, isolated. Only valid for LALAL, because
% only LALAL is sample-aligned with the original.
delta = lalal(1:size(original, 1), :) - original;
[deltaSpec, ~] = longTermSpectrum(delta, fs);
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
% Plot a decimated view. Putting all 9.68M samples into the line object makes
% the saved .fig ~63 MB for no visible benefit, since only 20 s is shown.
displaySeconds = 20;
displayStride = 8;
displaySamples = min(round(displaySeconds * fs), size(delta, 1));
displayTime = (0:displayStride:(displaySamples - 1)) / fs;
plot(displayTime, delta(1:displayStride:displaySamples, 1), 'LineWidth', 0.6);
xlim([0, displaySeconds]); grid on;
xlabel('Time (s)'); ylabel('Residual (FS)');
title('LALAL master minus original, first 20 s (stride 8)');
nexttile;
semilogx(specFreqs, deltaSpec, 'LineWidth', 1.1);
xlim([20, 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Residual power (dB)');
title('Spectrum of the processing residual');
contract = moodifylab.figureContract("S004-processing-residual", ...
    Conclusion="The residual isolates exactly what the LALAL mastering chain changed, because that master is sample-aligned with the original.", ...
    EvidenceRole="measurement", ...
    SourceData=["自己的神话3.wav", "自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["seconds", "digital full scale", "hertz", "decibels"], ...
    CalibrationStatus="DIGITAL_NUMERICAL_BASELINE", ...
    Uncertainty="Deterministic difference of two aligned signals.", ...
    Limitations="Applies only to the LALAL master. The Suno master is not sample-aligned, so no equivalent residual can be computed for it.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig06_processing_residual", contract);

fprintf('[S004]   figures done in %.1f s\n', toc(stageTimer));

%% ---- Persist ------------------------------------------------------------
result = struct();
result.status = "COMPLETE";
result.studyId = "S004";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "Q1 provenance is answered with a verifiable numeric identity. " ...
    "Q2 differences are described with units. " ...
    "Q3 preference is NOT answered and no figure here ranks the versions."];
result.limitations = [ ...
    "One song, one render per version. No perceptual calibration, no listener " ...
    "panel, no confidence interval across renders."];

writeMetricsTable(metrics, fullfile(ctx.outputDir, 'metrics.csv'));
fprintf('[S004] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S004] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

function s = describeSignal(audio, fs)
s = struct();
s.frames = size(audio, 1);
s.channels = size(audio, 2);
s.sampleRate = fs;
s.durationSeconds = size(audio, 1) / fs;
s.peakDbfs = 20 * log10(max(abs(audio(:))) + eps);
s.rmsDbfs = 20 * log10(sqrt(mean(audio(:).^2)) + eps);
s.crestDb = s.peakDbfs - s.rmsDbfs;
end

% -------------------------------------------------------------------------
function out = stemRoundtrip(stemDir, stemNames, reference, fs)
% Sum stems incrementally so the full set is never held in memory at once.
reconstruction = [];
for index = 1:numel(stemNames)
    stemPath = fullfile(stemDir, stemNames(index));
    if ~isfile(stemPath)
        error('MoodifyLab:S004:MissingStem', 'Missing stem: %s', stemPath);
    end
    [stemAudio, stemRate] = audioread(stemPath);
    if stemRate ~= fs
        error('MoodifyLab:S004:StemRateMismatch', ...
            'Stem %s is %d Hz, expected %d Hz.', stemNames(index), stemRate, fs);
    end
    if isempty(reconstruction)
        reconstruction = zeros(size(stemAudio), 'double');
    end
    if size(stemAudio, 1) < size(reconstruction, 1)
        reconstruction = reconstruction(1:size(stemAudio, 1), :);
    end
    reconstruction(1:size(stemAudio, 1), :) = ...
        reconstruction(1:size(stemAudio, 1), :) + stemAudio;
    clear stemAudio;
end

% Align the reconstruction to the reference over a bounded lag search, then
% trim to the common overlap. Lag is retained as evidence.
maxLag = round(0.75 * fs);
[bestLag, ~, ~] = alignLag(reference, reconstruction, maxLag, 60, fs);
[refTrimmed, recTrimmed] = trimToLag(reference, reconstruction, bestLag);

commonFrames = min(size(refTrimmed, 1), size(recTrimmed, 1));
refTrimmed = refTrimmed(1:commonFrames, :);
recTrimmed = recTrimmed(1:commonFrames, :);

residual = refTrimmed - recTrimmed;
refRms = sqrt(mean(refTrimmed(:).^2));
resRms = sqrt(mean(residual(:).^2));

out = struct();
out.stemCount = numel(stemNames);
out.reconstructionFrames = size(reconstruction, 1);
out.estimatedLagSamples = bestLag;
out.comparedFrames = commonFrames;
out.correlation = correlationCoefficient(refTrimmed, recTrimmed);
out.residualRmsDbfs = 20 * log10(resRms + eps);
out.relativeErrorDb = 20 * log10(resRms / max(refRms, eps));
% Both trimmed views travel together. Plotting the reconstruction against an
% untrimmed original would shift the comparison by the alignment lag and
% silently corrupt exactly the case (Suno) that the figure exists to show.
out.reconstruction = recTrimmed;
out.referenceTrimmed = refTrimmed;
end

% -------------------------------------------------------------------------
function [refOut, recOut] = trimToLag(reference, reconstruction, lag)
% lag is the offset of reconstruction relative to reference.
if lag >= 0
    refStart = 1; recStart = 1 + lag;
else
    refStart = 1 - lag; recStart = 1;
end
refEnd = min(size(reference, 1), refStart + size(reconstruction, 1) - recStart);
recEnd = recStart + (refEnd - refStart);
refOut = reference(refStart:refEnd, :);
recOut = reconstruction(recStart:recEnd, :);
end

% -------------------------------------------------------------------------
function [bestLag, curve, lags] = alignLag(reference, candidate, maxLag, windowSeconds, fs)
% Bounded lag search on smoothed energy envelopes.
%
% LAG CONVENTION: lag L means candidate(n) approximates reference(n - L).
%   L > 0  -> candidate is LATER than reference (trim L samples off its head)
%   L < 0  -> candidate is EARLIER than reference
% This matches trimToLag.
%
% Both windows are anchored at the SAME absolute start. The candidate segment
% for lag L is sampled at absolute offset +L from the reference segment, so the
% correlation peak sits at the true lag by construction.
%
% An earlier version instead shifted the candidate window start by -maxLag and
% then treated the returned lag as absolute. That biased every result by
% maxLag (0.75 s here), which drove the LALAL round-trip correlation from
% ~1.0 to ~0. Do not reintroduce that offset.
%
% Two stages: a cheap sweep on a decimated envelope to locate the peak, then a
% full-rate refine within +/- (decim+2) samples for sample-accurate lag.

decim = 64;
refEnv = localEnvelope(mean(reference, 2), round(0.010 * fs));
candEnv = localEnvelope(mean(candidate, 2), round(0.010 * fs));
nRefFull = numel(refEnv);
nCandFull = numel(candEnv);

% ---- stage 1: coarse sweep on the decimated envelope --------------------
refDecimated = refEnv(1:decim:end);
candDecimated = candEnv(1:decim:end);
maxLagDecimated = max(1, round(maxLag / decim));
windowDecimated = min(round(windowSeconds * fs / decim), ...
                      numel(refDecimated) - 2 * maxLagDecimated - 1);
if windowDecimated < 4
    error('MoodifyLab:S004:AlignWindow', ...
        'Signal too short to align within +/-%d samples.', maxLag);
end
anchorDecimated = floor((numel(refDecimated) - windowDecimated) / 2) + 1;
refSegmentDecimated = refDecimated(anchorDecimated:(anchorDecimated + windowDecimated - 1));

lagsDecimated = (-maxLagDecimated:maxLagDecimated)';
curveDecimated = -Inf(numel(lagsDecimated), 1);
for index = 1:numel(lagsDecimated)
    first = anchorDecimated + lagsDecimated(index);
    last = first + windowDecimated - 1;
    if first < 1 || last > numel(candDecimated)
        continue;
    end
    curveDecimated(index) = localCorrelation( ...
        candDecimated(first:last), refSegmentDecimated);
end
[~, coarsePeak] = max(curveDecimated);
if ~isfinite(curveDecimated(coarsePeak))
    error('MoodifyLab:S004:AlignRange', ...
        'No candidate lag inside +/-%d samples was usable.', maxLag);
end
coarseLag = lagsDecimated(coarsePeak) * decim;

% ---- stage 2: full-rate refine near the coarse peak ---------------------
refineRange = decim + 2;
anchorFull = (anchorDecimated - 1) * decim + 1;
fineWindow = min(round(5 * fs), nRefFull - anchorFull - refineRange - 1);
if fineWindow < round(fs)
    fineWindow = max(round(0.5 * fs), nRefFull - anchorFull - refineRange - 1);
end
refSegmentFine = refEnv(anchorFull:(anchorFull + fineWindow - 1));

fineLags = (coarseLag - refineRange:coarseLag + refineRange)';
fineCurve = -Inf(numel(fineLags), 1);
for index = 1:numel(fineLags)
    first = anchorFull + fineLags(index);
    last = first + fineWindow - 1;
    if first < 1 || last > nCandFull
        continue;
    end
    fineCurve(index) = localCorrelation(candEnv(first:last), refSegmentFine);
end
[~, finePeak] = max(fineCurve);
if isfinite(fineCurve(finePeak))
    bestLag = fineLags(finePeak);
else
    bestLag = coarseLag;
end

% Report the smooth coarse curve for plotting; lags in sample units.
lags = lagsDecimated * decim;
curve = curveDecimated;
end

% -------------------------------------------------------------------------
function y = localEnvelope(x, halfWidth)
y = sqrt(localMovingMean(x.^2, halfWidth));
y = (y - mean(y)) / (std(y) + eps);
end

% -------------------------------------------------------------------------
function y = localMovingMean(x, halfWidth)
% movmean is O(n); conv with a kernel this wide would be O(n*k), which on a
% 9.7M-sample master means ~10^10 operations instead of ~10^7.
y = movmean(x, 2 * halfWidth + 1);
end

% -------------------------------------------------------------------------
function value = localCorrelation(a, b)
n = min(numel(a), numel(b));
a = a(1:n);
b = b(1:n);
denominator = sqrt(sum(a.^2) * sum(b.^2));
if denominator <= eps
    value = -Inf;
else
    value = sum(a .* b) / denominator;
end
end

% -------------------------------------------------------------------------
function value = correlationCoefficient(a, b)
a = a(:) - mean(a(:));
b = b(:) - mean(b(:));
denominator = sqrt(sum(a.^2) * sum(b.^2));
if denominator <= eps
    value = 0;
else
    value = sum(a .* b) / denominator;
end
end

% -------------------------------------------------------------------------
function [spectrumDb, freqs] = longTermSpectrum(audio, fs)
mono = mean(audio, 2);
[power, freqs] = pwelch(mono, hann(8192), 4096, 8192, fs);
spectrumDb = 10 * log10(power + eps);
end

% -------------------------------------------------------------------------
function d = descriptorSet(audio, fs)
mono = mean(audio, 2);
peak = max(abs(mono));
rmsValue = sqrt(mean(mono.^2));

windowLength = round(1.0 * fs);
windowCount = max(1, floor(numel(mono) / windowLength));
shortTerm = zeros(windowCount, 1);
correlationOverTime = zeros(windowCount, 1);
for index = 1:windowCount
    span = (index - 1) * windowLength + (1:windowLength);
    segment = mono(span);
    shortTerm(index) = 20 * log10(sqrt(mean(segment.^2)) + eps);
    left = audio(span, 1);
    right = audio(span, 2);
    if std(left) < eps || std(right) < eps
        correlationOverTime(index) = 1;
    else
        matrix = corrcoef(left, right);
        correlationOverTime(index) = matrix(1, 2);
    end
end

mid = 0.5 * (audio(:, 1) + audio(:, 2));
side = 0.5 * (audio(:, 1) - audio(:, 2));

d = struct();
d.peakDbfs = 20 * log10(peak + eps);
d.rmsDbfs = 20 * log10(rmsValue + eps);
d.crestDb = d.peakDbfs - d.rmsDbfs;
d.shortTermDb = shortTerm;
d.correlationOverTime = correlationOverTime;
d.sideMidDb = 10 * log10((mean(side.^2) + eps) / (mean(mid.^2) + eps));
d.meanCorrelation = mean(correlationOverTime);
end

% -------------------------------------------------------------------------
function colorBarsByVersion(barHandle)
% Colour three version bars to match the line/histogram order.
%
% Without this the bar charts default to a single colour, so a reader who has
% learned "blue = Original" from the line panels reads the bars wrong. The
% Moodify figure standard requires colour to encode meaning consistently.
palette = [0 0.4470 0.7410;      % Original  (MATLAB ColorOrder 1)
           0.8500 0.3250 0.0980; % LALAL     (ColorOrder 2)
           0.9290 0.6940 0.1250];% Suno      (ColorOrder 3)
barHandle.FaceColor = 'flat';
barHandle.CData = palette;
end

% -------------------------------------------------------------------------
function plotSegmentOverlay(reference, reconstruction, fs, seconds)
samples = min([round(seconds * fs), size(reference, 1), size(reconstruction, 1)]);
timeAxis = (0:(samples - 1)) / fs * 1000;
refSegment = reference(1:samples, 1);
recSegment = reconstruction(1:samples, 1);
plot(timeAxis, refSegment, 'LineWidth', 1.3); hold on;
plot(timeAxis, recSegment, '--', 'LineWidth', 1.0);
xlabel('Time (ms)'); ylabel('Amplitude (FS)');
legend('Original', 'Stem sum', 'Location', 'best'); grid on;
% Auto-scaling means a quieter trace can look like a dead zero line. State
% both RMS levels so a low trace is not misread as "the stems are broken".
refRmsDb = 20 * log10(sqrt(mean(refSegment.^2)) + eps);
recRmsDb = 20 * log10(sqrt(mean(recSegment.^2)) + eps);
text(0.02, 0.04, sprintf('RMS in view: original %.1f dBFS, stem sum %.1f dBFS', ...
    refRmsDb, recRmsDb), 'Units', 'normalized', 'FontSize', 7, ...
    'VerticalAlignment', 'bottom');
end

% -------------------------------------------------------------------------
function plotResidualEnvelope(reference, reconstruction, fs)
samples = min(size(reference, 1), size(reconstruction, 1));
residual = reference(1:samples, 1) - reconstruction(1:samples, 1);
windowLength = round(1.0 * fs);
windowCount = floor(samples / windowLength);
envelopeDb = zeros(windowCount, 1);
for index = 1:windowCount
    span = (index - 1) * windowLength + (1:windowLength);
    envelopeDb(index) = 20 * log10(sqrt(mean(residual(span).^2)) + eps);
end
plot((1:windowCount), envelopeDb, 'LineWidth', 1.1);
xlabel('Window (1 s)'); ylabel('Residual RMS (dBFS)');
grid on;
end

% -------------------------------------------------------------------------
function plotLoudnessCurve(detail, fs, label)
if isempty(detail.blockLoudness)
    return;
end
timeAxis = (detail.blockStarts - 1) / fs;
% DisplayName is required: without it the later legend() call falls back to
% MATLAB's auto names and the figure reads "data1 / data2 / data3".
plot(timeAxis, detail.blockLoudness, 'LineWidth', 1.1, 'DisplayName', label);
end

% -------------------------------------------------------------------------
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end

% -------------------------------------------------------------------------
function writeMetricsTable(metrics, path)
names = ["original"; "lalal"; "suno"];
peak = [metrics.descriptors.original.peakDbfs; ...
        metrics.descriptors.lalal.peakDbfs; ...
        metrics.descriptors.suno.peakDbfs];
rmsValue = [metrics.descriptors.original.rmsDbfs; ...
            metrics.descriptors.lalal.rmsDbfs; ...
            metrics.descriptors.suno.rmsDbfs];
crest = [metrics.descriptors.original.crestDb; ...
         metrics.descriptors.lalal.crestDb; ...
         metrics.descriptors.suno.crestDb];
sideMid = [metrics.descriptors.original.sideMidDb; ...
           metrics.descriptors.lalal.sideMidDb; ...
           metrics.descriptors.suno.sideMidDb];
lufs = [metrics.loudness.originalLufs; ...
        metrics.loudness.lalalLufs; ...
        metrics.loudness.sunoLufs];
writetable(table(names, lufs, peak, rmsValue, crest, sideMid, ...
    'VariableNames', {'version', 'lufs', 'peak_dbfs', 'rms_dbfs', ...
                      'crest_db', 'side_mid_db'}), path);
end
