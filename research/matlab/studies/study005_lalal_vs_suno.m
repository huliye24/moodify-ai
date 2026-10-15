function result = study005_lalal_vs_suno(ctx)
%STUDY005_LALAL_VS_SUNO Direct LALAL-vs-Suno comparison plus a three-way overview.
%
%   S004 anchors everything on the original. This study asks a different
%   question: how do the two finished masters differ FROM EACH OTHER, once the
%   loudness confound is removed? It also produces one at-a-glance overview of
%   all three versions.
%
%   Q1 provenance is answered in S004 and is not repeated here.
%   Q3 preference is not answered here either. No figure ranks the versions.
%
%   Honest framing that the figures must carry: these two are DIFFERENT
%   RENDERS, not one audio transformed into another. Their waveforms are
%   uncorrelated, so the difference signal between them is NOT a small
%   residual -- it sits at roughly the level of the material itself. That is
%   a statement about how different the renders are, not about which is wrong.

fprintf('[S005] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
originalPath = fullfile(root, "自己的神话3.wav");
lalalMaster  = fullfile(root, "LALAL重制版_vs_Suno分轨重制版_20261011", ...
                        "自己的神话_LALAL分轨重制_48k24.wav");
sunoMaster   = fullfile(root, "重制_贝叶斯双版本", "修复版_保守", ...
                        "自己的神话_重制A_局部修复保守版_48k24bit.wav");

bandEdges = [20 60; 60 125; 125 250; 250 500; 500 1000; ...
             1000 2000; 2000 4000; 4000 8000; 8000 16000; 16000 20000];
bandLabels = ["20-60"; "60-125"; "125-250"; "250-500"; "500-1k"; ...
              "1k-2k"; "2k-4k"; "4k-8k"; "8k-16k"; "16k-20k"];

failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: load -------------------------------------------------------
fprintf('[S005] stage 1: load\n');
stageTimer = tic;
[original, fs] = audioread(originalPath);
[lalal, fsLalal] = audioread(lalalMaster);
[suno, fsSuno] = audioread(sunoMaster);
if fsLalal ~= fs || fsSuno ~= fs
    error('MoodifyLab:S005:RateMismatch', 'Sample rates differ (%.0f/%.0f/%.0f).', fs, fsLalal, fsSuno);
end
fprintf('[S005]   original %d, lalal %d, suno %d frames @ %d Hz\n', ...
    size(original,1), size(lalal,1), size(suno,1), fs);
metrics.inputs = struct( ...
    'originalFrames', size(original,1), 'lalalFrames', size(lalal,1), ...
    'sunoFrames', size(suno,1), 'sampleRate', fs);
fprintf('[S005]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: loudness measurement + equal-loudness match ---------------
fprintf('[S005] stage 2: loudness match\n');
stageTimer = tic;
[origLufs, origLoud] = moodifylab.loudnessBs1770(original, fs);
[lalalLufs, lalalLoud] = moodifylab.loudnessBs1770(lalal, fs);
[sunoLufs, sunoLoud] = moodifylab.loudnessBs1770(suno, fs);

% Attenuate only: never amplify, so neither version can win by being louder.
targetLufs = min([lalalLufs, sunoLufs]);
lalalGainDb = targetLufs - lalalLufs;
sunoGainDb  = targetLufs - sunoLufs;
lalalMatched = lalal * 10^(lalalGainDb / 20);
sunoMatched  = suno  * 10^(sunoGainDb / 20);
[~, lalalMatchedLufs] = moodifylab.loudnessBs1770(lalalMatched, fs);
[~, sunoMatchedLufs] = moodifylab.loudnessBs1770(sunoMatched, fs);

fprintf('[S005]   original %.3f  lalal %.3f  suno %.3f LUFS\n', origLufs, lalalLufs, sunoLufs);
fprintf('[S005]   match target %.3f LUFS; lalal %+.3f dB, suno %+.3f dB\n', ...
    targetLufs, lalalGainDb, sunoGainDb);
metrics.loudnessMatch = struct( ...
    'originalLufs', origLufs, 'lalalLufs', lalalLufs, 'sunoLufs', sunoLufs, ...
    'targetLufs', targetLufs, 'lalalGainDb', lalalGainDb, 'sunoGainDb', sunoGainDb, ...
    'lalalMatchedLufs', lalalMatchedLufs, 'sunoMatchedLufs', sunoMatchedLufs, ...
    'loudnessOffsetLu', sunoLufs - lalalLufs);
fprintf('[S005]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: align LALAL to Suno directly ------------------------------
fprintf('[S005] stage 3: align lalal vs suno\n');
stageTimer = tic;
maxLag = round(0.75 * fs);
[lalalSunoLag, lalalSunoCurve, lalalSunoLags] = ...
    moodifylab.alignEnvelopeLag(lalalMatched, sunoMatched, maxLag, 60, fs);
[lalalTrim, sunoTrim] = trimToLag(lalalMatched, sunoMatched, lalalSunoLag);
commonFrames = min(size(lalalTrim,1), size(sunoTrim,1));
lalalTrim = lalalTrim(1:commonFrames, :);
sunoTrim  = sunoTrim(1:commonFrames, :);
waveformCorrelation = correlationCoefficient(lalalTrim, sunoTrim);
fprintf('[S005]   lag %d samples (%.1f ms), env peak %.4f, waveform r %.6f\n', ...
    lalalSunoLag, lalalSunoLag*1000/fs, max(lalalSunoCurve), waveformCorrelation);
metrics.alignment = struct( ...
    'lagSamples', lalalSunoLag, 'lagMs', lalalSunoLag*1000/fs, ...
    'envelopePeakCorrelation', max(lalalSunoCurve), ...
    'waveformCorrelation', waveformCorrelation, ...
    'comparedFrames', commonFrames, 'maxSearchedLagMs', maxLag*1000/fs);
fprintf('[S005]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: new figure 07 - three-way overview ------------------------
% The other S004 figures each cover one dimension. This one is the single
% "read it in one glance" panel.
fprintf('[S005] stage 4: fig07 overview\n');
stageTimer = tic;

% Pick the loudest sustained 8 s of the original as a representative excerpt.
excerptSeconds = 8;
excerptStart = pickLoudestStart(original, fs, excerptSeconds);
excerptCount = round(excerptSeconds * fs);
excerptRange = excerptStart:(excerptStart + excerptCount - 1);

% Compare shapes at matched loudness, otherwise the Suno trace dwarfs the rest.
origShapeMono = mean(original(excerptRange, :), 2) * 10^((targetLufs - origLufs)/20);
lalalShapeMono = mean(lalalMatched(excerptRange, :), 2);
sunoShapeMono = mean(sunoMatched(excerptRange, :), 2);

% Plot a short-time envelope, NOT the raw waveform. Eight seconds at 48 kHz is
% ~380k samples: drawn into a ~7 cm panel the raw traces collapse into a solid
% block and convey nothing. A 20 ms envelope is readable at this scale and
% still shows how the three versions shape the passage.
envelopeWindow = round(0.020 * fs);
envelopeHop = round(0.010 * fs);
origEnvelope = shortTimeEnvelopeDb(origShapeMono, envelopeWindow, envelopeHop);
lalalEnvelope = shortTimeEnvelopeDb(lalalShapeMono, envelopeWindow, envelopeHop);
sunoEnvelope = shortTimeEnvelopeDb(sunoShapeMono, envelopeWindow, envelopeHop);
envelopeTime = ((0:(numel(origEnvelope) - 1)) * envelopeHop) / fs;

fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
% Plot order is fixed as Original, LALAL, Suno in EVERY panel so a colour
% always means the same version within this figure.
% Original is drawn THICKER than the others on purpose: LALAL reproduces the
% original to -60 dB, so their curves coincide almost exactly and a normal
% line would be completely hidden under the LALAL trace, making the figure
% look like a series is missing. The wider blue halo shows both are present.
plot(envelopeTime, origEnvelope, 'LineWidth', 2.6); hold on;
plot(envelopeTime, lalalEnvelope, 'LineWidth', 1.0);
plot(envelopeTime, sunoEnvelope, 'LineWidth', 1.0);
xlabel(sprintf('Time within excerpt (s), from %.1f s', excerptStart/fs));
ylabel('Envelope (dBFS, 20 ms)');
legend('Original', 'LALAL', 'Suno', 'Location', 'best'); grid on;
title(sprintf('Excerpt envelope (%.0f s from loudest passage)', excerptSeconds));

nexttile;
plotLoudness(origLoud, fs, 'Original', 2.6); hold on;
plotLoudness(lalalLoud, fs, 'LALAL', 1.0);
plotLoudness(sunoLoud, fs, 'Suno', 1.0);
xlabel('Time (s)'); ylabel('Short-term loudness (LUFS)');
legend('Location', 'southeast'); grid on;
title('Short-term loudness, full song');

nexttile;
[origSpec, specFreqs] = longTermSpectrum(original, fs);
[lalalSpec, ~] = longTermSpectrum(lalal, fs);
[sunoSpec, ~] = longTermSpectrum(suno, fs);
originalRmsEnvelope = rmsEnvelope(original, fs);
lalalRmsEnvelope = rmsEnvelope(lalal, fs);
sunoRmsEnvelope = rmsEnvelope(suno, fs);
semilogx(specFreqs, origSpec, specFreqs, lalalSpec, specFreqs, sunoSpec, 'LineWidth', 1.0);
xlim([20 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Power (dB)');
legend('Original', 'LALAL', 'Suno', 'Location', 'southwest');
title('Long-term average spectrum');

nexttile;
plot(originalRmsEnvelope, 'LineWidth', 1.0); hold on;
plot(lalalRmsEnvelope, 'LineWidth', 1.0);
plot(sunoRmsEnvelope, 'LineWidth', 1.0);
xlabel('Window (1 s)'); ylabel('RMS (dBFS)');
legend('Original', 'LALAL', 'Suno', 'Location', 'southeast'); grid on;
title('Per-second RMS envelope');

contract = moodifylab.figureContract("S005-three-way-overview", ...
    Conclusion="One-glance view of the three versions: shape, loudness contour, spectrum and level envelope.", ...
    EvidenceRole="orientation", ...
    SourceData=["自己的神话3.wav", "自己的神话_LALAL分轨重制_48k24.wav", ...
                "自己的神话_重制A_局部修复保守版_48k24bit.wav"], ...
    Units=["seconds", "digital full scale", "LUFS", "hertz", "decibels"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT", ...
    Uncertainty="NOT_REPORTED_ACROSS_RENDERS: n=1 per version.", ...
    Limitations="The waveform panel is loudness-matched so shapes are comparable; that hides the real loudness offset, which the other two panels show. Nothing here ranks the versions.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig07_three_way_overview", contract);
fprintf('[S005]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: fig08 - equal-loudness spectral difference ----------------
fprintf('[S005] stage 5: fig08 spectral difference\n');
stageTimer = tic;
[lalalSpecMatched, ~] = longTermSpectrum(lalalMatched, fs);
[sunoSpecMatched, ~] = longTermSpectrum(sunoMatched, fs);
spectralDelta = sunoSpecMatched - lalalSpecMatched;

[lalalBand, ~] = bandPowerPerSecond(lalalMatched, fs, bandEdges);
[sunoBand, ~] = bandPowerPerSecond(sunoMatched, fs, bandEdges);
meanLalalBand = mean(lalalBand, 1);
meanSunoBand = mean(sunoBand, 1);
bandDelta = meanSunoBand - meanLalalBand;

fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 1, 2, 'TileSpacing', 'compact');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});
semilogx(specFreqs, lalalSpecMatched, specFreqs, sunoSpecMatched, 'LineWidth', 1.1);
xlim([20 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Power (dB)');
legend('LALAL', 'Suno', 'Location', 'southwest');
title(sprintf('Spectra at matched loudness (%.2f LUFS)', targetLufs));
nexttile;
barh(bandDelta);
set(gca, 'YTick', 1:numel(bandLabels), 'YTickLabel', cellstr(bandLabels));
ylabel('Band (Hz)'); xlabel('Suno - LALAL (dB)');
grid on; xline(0, 'k:', 'LineWidth', 0.7);
title('Mean band-power difference');
contract = moodifylab.figureContract("S005-spectral-difference", ...
    Conclusion="With loudness equalised, the two masters differ by a few dB in specific bands rather than globally.", ...
    EvidenceRole="measurement", ...
    SourceData=["LALAL master", "Suno master"], ...
    Units=["hertz", "decibels"], ...
    CalibrationStatus="LOUDNESS-MATCHED TO THE QUIETER MASTER; scales otherwise uncalibrated", ...
    Uncertainty="Single render per version. Band values are means over the whole song.", ...
    Limitations="EQ differences may be intentional in either master and are not defects. This is a description, not a ranking.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig08_spectral_difference", contract);
fprintf('[S005]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: fig09 - per-second difference heatmap ---------------------
fprintf('[S005] stage 6: fig09 difference heatmap\n');
stageTimer = tic;
nSeconds = min(size(lalalBand, 1), size(sunoBand, 1));
bandDifference = sunoBand(1:nSeconds, :) - lalalBand(1:nSeconds, :);

% Mean ABSOLUTE band difference, in dB. An earlier version summed the linear
% band power ratios and took 10*log10 of the total, which is not interpretable:
% ten bands all differing by 0 dB sum to 10, so the curve's floor sat at
% "10 dB" while reading as if 10 dB of difference were present. mean(|dB|) has
% an honest zero and the same units as the heatmap above it.
perSecondDifferenceDb = mean(abs(bandDifference), 2);

fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
imagesc(1:nSeconds, 1:numel(bandLabels), bandDifference.');
set(gca, 'YTick', 1:numel(bandLabels), 'YTickLabel', cellstr(bandLabels));
xlabel('Time (s)'); ylabel('Band (Hz)');
cb = colorbar; cb.Label.String = 'Suno - LALAL (dB)';
colormap(gca, blueWhiteRed(256));
caxis([-12 12]);
title('Band-by-band difference over time (equal loudness)');
nexttile;
plot(1:nSeconds, perSecondDifferenceDb, 'LineWidth', 1.0);
xlabel('Time (s)'); ylabel('Mean |band difference| (dB)');
grid on; xlim([1 nSeconds]);
title('Per-second mean absolute band difference');
contract = moodifylab.figureContract("S005-difference-heatmap", ...
    Conclusion="Where in time and frequency the two masters diverge most, once loudness is equalised.", ...
    EvidenceRole="descriptive", ...
    SourceData=["LALAL master", "Suno master"], ...
    Units=["seconds", "hertz", "decibels"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT; colour is a relative difference only", ...
    Uncertainty="1 s / one-band resolution; n=1 per version.", ...
    Limitations="Divergence is not error. Two competent masters of different provenance will diverge. The colour scale is clamped to +/-12 dB.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig09_difference_heatmap", contract);
fprintf('[S005]   stage 6 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 7: fig10 - dynamics and stereo, A vs B -----------------------
fprintf('[S005] stage 7: fig10 dynamics/stereo\n');
stageTimer = tic;
lalalDesc = perSecondStereo(lalalMatched, fs);
sunoDesc = perSecondStereo(sunoMatched, fs);
nDyn = min(numel(lalalDesc.rmsDb), numel(sunoDesc.rmsDb));

fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});
plot(lalalDesc.rmsDb(1:nDyn), 'LineWidth', 1.0); hold on;
plot(sunoDesc.rmsDb(1:nDyn), 'LineWidth', 1.0);
xlabel('Window (1 s)'); ylabel('RMS (dBFS)');
legend('LALAL', 'Suno', 'Location', 'southeast'); grid on; title('Short-term level');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});
plot(lalalDesc.crestDb(1:nDyn), 'LineWidth', 1.0); hold on;
plot(sunoDesc.crestDb(1:nDyn), 'LineWidth', 1.0);
xlabel('Window (1 s)'); ylabel('Crest (dB)');
legend('LALAL', 'Suno', 'Location', 'southeast'); grid on; title('Crest factor');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});
plot(lalalDesc.correlation(1:nDyn), 'LineWidth', 1.0); hold on;
plot(sunoDesc.correlation(1:nDyn), 'LineWidth', 1.0);
xlabel('Window (1 s)'); ylabel('L/R correlation');
legend('LALAL', 'Suno', 'Location', 'southeast'); grid on; title('Stereo correlation');
nexttile;
moodifylab.useVersionColors({'LALAL', 'Suno'});
plot(lalalDesc.sideMidDb(1:nDyn), 'LineWidth', 1.0); hold on;
plot(sunoDesc.sideMidDb(1:nDyn), 'LineWidth', 1.0);
xlabel('Window (1 s)'); ylabel('Side / mid (dB)');
legend('LALAL', 'Suno', 'Location', 'southeast'); grid on; title('Stereo width');
contract = moodifylab.figureContract("S005-dynamics-stereo-ab", ...
    Conclusion="Per-second dynamics and stereo behaviour of the two masters side by side.", ...
    EvidenceRole="descriptive", ...
    SourceData=["LALAL master", "Suno master"], ...
    Units=["seconds", "dBFS", "decibels", "dimensionless"], ...
    CalibrationStatus="LOUDNESS-MATCHED", ...
    Uncertainty="1 s windows; n=1 per version.", ...
    Limitations="Wider is not better; more dynamic is not better. No ranking is implied.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig10_dynamics_stereo_ab", contract);
metrics.dynamics = struct( ...
    'lalalMeanRmsDb', mean(lalalDesc.rmsDb), 'sunoMeanRmsDb', mean(sunoDesc.rmsDb), ...
    'lalalMeanCrestDb', mean(lalalDesc.crestDb), 'sunoMeanCrestDb', mean(sunoDesc.crestDb), ...
    'lalalMeanCorrelation', mean(lalalDesc.correlation), 'sunoMeanCorrelation', mean(sunoDesc.correlation), ...
    'lalalMeanSideMidDb', mean(lalalDesc.sideMidDb), 'sunoMeanSideMidDb', mean(sunoDesc.sideMidDb));
fprintf('[S005]   stage 7 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 8: fig11 - residual audibility + difference file -------------
% Because these are different renders, this "residual" is not a small error
% term. Its loudness is the honest headline: it says how audible the gap is.
fprintf('[S005] stage 8: fig11 residual audibility\n');
stageTimer = tic;
difference = sunoTrim - lalalTrim;
diffLufs = moodifylab.loudnessBs1770(difference, fs);
diffRms = sqrt(mean(difference(:).^2));
diffRmsDb = 20*log10(diffRms + eps);
lalalRms = sqrt(mean(lalalTrim(:).^2));
lalalRmsDb = 20*log10(lalalRms + eps);

% Signal-level sanity check on the "different renders" claim. For two
% uncorrelated signals of equal RMS the difference is sqrt(2) x either one,
% i.e. +3.01 dB ABOVE. Measuring ~+3 dB therefore CONFIRMS the renders share
% almost nothing sample-wise; it is not a defect. A residual well BELOW the
% masters would be the surprising result here.
diffVsMasterDb = diffRmsDb - lalalRmsDb;
predictedUncorrelatedDb = 10 * log10(2);   % +3.0103 dB
impliedCorrelation = 1 - (10^(diffVsMasterDb/10)) / 2;
[diffSpec, ~] = longTermSpectrum(difference, fs);

differencePath = fullfile(ctx.outputDir, 'lalal_vs_suno_difference_48k24.wav');
audiowrite(differencePath, difference / max(abs(difference(:)) + eps) * 0.5, fs, ...
    'BitsPerSample', 24);

fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 1, 'TileSpacing', 'compact');
nexttile;
displaySamples = min(round(20*fs), size(difference,1));
plot((0:8:(displaySamples-1))/fs, difference(1:8:displaySamples, 1), 'LineWidth', 0.6);
xlabel('Time (s)'); ylabel('Difference (FS)'); grid on;
title({sprintf('Suno - LALAL residual, first 20 s (stride 8). Residual %.2f LUFS', diffLufs); ...
    sprintf('%.2f dB vs the masters (uncorrelated renders predict +%.2f dB)', ...
    diffVsMasterDb, predictedUncorrelatedDb)});
nexttile;
moodifylab.useVersionColors({'LALAL', 'Residual'});
semilogx(specFreqs, lalalSpecMatched, specFreqs, diffSpec, 'LineWidth', 1.1);
xlim([20 20000]); grid on;
xlabel('Frequency (Hz)'); ylabel('Power (dB)');
legend('LALAL master', 'Suno - LALAL residual', 'Location', 'southwest');
title('Residual spectrum vs the master spectrum');
contract = moodifylab.figureContract("S005-residual-audibility", ...
    Conclusion="The difference between the two masters is LOUDER than either master, sitting about 3 dB above them -- the signature of two uncorrelated signals, i.e. genuinely different renders rather than one audio transformed into another.", ...
    EvidenceRole="measurement", ...
    SourceData=["LALAL master", "Suno master"], ...
    Units=["seconds", "digital full scale", "LUFS", "hertz", "decibels"], ...
    CalibrationStatus="ITU-R BS.1770-4 implemented in this bundle; loudness-matched inputs", ...
    Uncertainty="Alignment is envelope-based and imperfect between different renders; a better alignment would LOWER this residual, so treat it as an upper bound on similarity.", ...
    Limitations="A large residual does NOT mean either master is defective. It quantifies how far apart two different renders are. The exported WAV is normalised to -6 dBFS for listening and is not level-accurate.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig11_residual_audibility", contract);

metrics.residual = struct( ...
    'differenceLufs', diffLufs, 'differenceRmsDbfs', diffRmsDb, ...
    'masterRmsDbfs', lalalRmsDb, 'differenceVsMasterDb', diffVsMasterDb, ...
    'predictedUncorrelatedDb', predictedUncorrelatedDb, ...
    'impliedCorrelation', impliedCorrelation, ...
    'differenceWav', differencePath);
fprintf(['[S005]   residual %.2f LUFS, %+.2f dB vs masters ' ...
    '(uncorrelated predicts +%.2f -> implied rho %.3f)\n'], ...
    diffLufs, diffVsMasterDb, predictedUncorrelatedDb, impliedCorrelation);
fprintf('[S005]   stage 8 done in %.1f s\n', toc(stageTimer));

%% ---- Persist -------------------------------------------------------------
bandTable = table(bandLabels, meanLalalBand(:), meanSunoBand(:), bandDelta(:), ...
    'VariableNames', {'band_hz', 'lalal_mean_db', 'suno_mean_db', 'suno_minus_lalal_db'});
writetable(bandTable, fullfile(ctx.outputDir, 's005_band_difference.csv'));

seriesTable = table((1:nSeconds)', perSecondDifferenceDb, ...
    'VariableNames', {'second', 'mean_abs_band_difference_db'});
for b = 1:numel(bandLabels)
    seriesTable.(matlab.lang.makeValidName("diff_" + bandLabels(b))) = bandDifference(:, b);
end
writetable(seriesTable, fullfile(ctx.outputDir, 's005_difference_series.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S005";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "S004 answers provenance. S005 answers how the two finished masters differ " ...
    "once loudness is removed. Neither ranks perceived quality."];
result.limitations = [ ...
    "Different renders, not one audio transformed. Alignment between them is " ...
    "envelope-based and imperfect, so the residual is an upper bound on similarity. " ...
    "n=1 per version; no listener panel."];
fprintf('[S005] complete.\n');
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function startIndex = pickLoudestStart(audio, fs, seconds)
% Anchor the overview excerpt on the loudest sustained passage (usually the
% chorus) rather than the intro, which is often a fade-in.
mono = mean(audio, 2);
window = round(1.0 * fs);
count = floor(numel(mono) / window);
if count < seconds
    startIndex = 1;
    return;
end
levels = zeros(count, 1);
for index = 1:count
    span = (index - 1) * window + (1:window);
    levels(index) = mean(mono(span).^2);
end
smooth = movmean(levels, seconds);
[~, peak] = max(smooth);
startIndex = max(1, min((peak - 1) * window + 1, numel(mono) - round(seconds * fs) - 1));
end

% -------------------------------------------------------------------------
function envelopeDb = shortTimeEnvelopeDb(mono, window, hop)
% Short-time RMS envelope in dBFS, for plotting signals far too dense to draw
% as raw samples.
segments = floor((numel(mono) - window) / hop) + 1;
if segments < 1
    envelopeDb = 20 * log10(abs(mono) + eps);
    return;
end
envelopeDb = zeros(segments, 1);
for index = 1:segments
    span = (index - 1) * hop + (1:window);
    envelopeDb(index) = 20 * log10(sqrt(mean(mono(span).^2)) + eps);
end
end

% -------------------------------------------------------------------------
function [refOut, candOut] = trimToLag(reference, candidate, lag)
% lag is the offset of candidate relative to reference.
if lag >= 0
    refStart = 1; candStart = 1 + lag;
else
    refStart = 1 - lag; candStart = 1;
end
refEnd = min(size(reference, 1), refStart + size(candidate, 1) - candStart);
candEnd = candStart + (refEnd - refStart);
refOut = reference(refStart:refEnd, :);
candOut = candidate(candStart:candEnd, :);
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
function [dbMatrix, seconds] = bandPowerPerSecond(audio, fs, edges, windowSeconds)
arguments
    audio double
    fs (1,1) double
    edges double
    windowSeconds (1,1) double = 1.0
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
    power = abs(fft(segment)).^2;
    halfPower = power(half);
    for band = 1:nBands
        dbMatrix(index, band) = 10*log10(sum(halfPower(masks(:, band))) + eps);
    end
end
seconds = (1:segments)';
end

% -------------------------------------------------------------------------
function d = perSecondStereo(audio, fs)
window = round(1.0 * fs);
total = size(audio, 1);
segments = floor(total / window);
d = struct();
d.rmsDb = zeros(segments, 1);
d.crestDb = zeros(segments, 1);
d.correlation = zeros(segments, 1);
d.sideMidDb = zeros(segments, 1);
for index = 1:segments
    span = (index-1)*window + (1:window);
    left = audio(span, 1);
    right = audio(span, 2);
    mono = 0.5 * (left + right);
    side = 0.5 * (left - right);
    rmsValue = sqrt(mean(mono.^2));
    d.rmsDb(index) = 20*log10(rmsValue + eps);
    d.crestDb(index) = 20*log10((max(abs(mono)) + eps) / (rmsValue + eps));
    if std(left) < eps || std(right) < eps
        d.correlation(index) = 1;
    else
        matrix = corrcoef(left, right);
        d.correlation(index) = matrix(1, 2);
    end
    d.sideMidDb(index) = 10*log10((mean(side.^2) + eps) / (mean(mono.^2) + eps));
end
end

% -------------------------------------------------------------------------
function y = rmsEnvelope(audio, fs)
window = round(1.0 * fs);
mono = mean(audio, 2);
segments = floor(numel(mono) / window);
y = zeros(segments, 1);
for index = 1:segments
    span = (index-1)*window + (1:window);
    y(index) = 20*log10(sqrt(mean(mono(span).^2)) + eps);
end
end

% -------------------------------------------------------------------------
function plotLoudness(detail, fs, label, lineWidth)
% nargin rather than an `arguments` default: keeps this helper consistent with
% the rest of the bundle and avoids relying on arguments-block behaviour.
if isempty(detail.blockLoudness)
    return;
end
if nargin < 4
    lineWidth = 1.1;
end
plot((detail.blockStarts - 1) / fs, detail.blockLoudness, ...
    'LineWidth', lineWidth, 'DisplayName', label);
end

% -------------------------------------------------------------------------
function colors = blueWhiteRed(count)
% Diverging map: the difference is signed, so zero must read as neutral.
half = floor(count / 2);
lower = [linspace(0.13, 1, half)', linspace(0.30, 1, half)', linspace(0.65, 1, half)'];
upper = [linspace(1, 0.75, count - half)', linspace(1, 0.25, count - half)', ...
         linspace(1, 0.20, count - half)'];
colors = [lower; upper];
end

% -------------------------------------------------------------------------
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end
