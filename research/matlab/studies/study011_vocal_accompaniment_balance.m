function result = study011_vocal_accompaniment_balance(ctx)
%STUDY011_VOCAL_ACCOMPANIMENT_BALANCE Locate phrases whose vocal/accompaniment balance is anomalous.
%
%   DETECT AND LOCATE ONLY. This study applies no EQ, no compression, no gain
%   automation, and writes no processed audio. It ranks phrases and exports
%   listening material so S012 can act on ONE of them, chosen by a human who
%   has heard it.
%
%   WHY PHRASE BOUNDARIES COME FROM A NOTE TRANSCRIPTION
%   The obvious segmentation -- gate the vocal stem's energy -- does not work
%   on this material. Measured: the vocal stem's short-time level is bimodal
%   (a separation-artifact hump around -90 dBFS and the vocal body around
%   -25 dBFS) with a valley at -75..-65 dBFS. Gating in that valley leaves the
%   vocal active 73.9% of the song with only FOUR silent gaps (0.65-18.08,
%   18.80-25.09, 27.71-87.10, 109.62-175.55 s). Two of those run a minute.
%   It finds the instrumental break correctly (87-110 s, which matches the
%   MIDI analysis) but cannot resolve sung phrases, because this vocal is
%   continuous across them.
%
%   So phrase boundaries are taken from inter-note gaps in the Basic Pitch
%   vocal transcription: gap > 0.30 s yields 36 phrases, median 2.30 s. That
%   transcription is declared REFERENCE_ONLY and non-authoritative, so the
%   BOUNDARIES inherit that status. The energy gate is still applied, to drop
%   any phrase that straddles the instrumental break. Two independent signals
%   agree on that break (energy 87.10 s, notes 87.14 s), which is the check
%   that the boundaries are usable.
%
%   AUTHORITY LIMIT: the LALAL multistem set has ONE vocal stem. It contains
%   lead and backing vocals together; there is no way to isolate the lead from
%   this separation. What is measured here is VOCALS vs ACCOMPANIMENT, not
%   lead vocal vs accompaniment.
%
%   Balance is V minus A in dB, computed over each phrase. An outlier is a
%   phrase whose balance departs from the song's own distribution -- which is
%   a candidate for listening, NOT a defect. A deliberately buried or pushed
%   vocal is a legitimate production choice.

fprintf('[S011] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
stemDir = fullfile(root, "LALAL_AI分轨_20261011", "自己的神话3_multistem");
originalPath = fullfile(root, "自己的神话3.wav");
noteCsv = fullfile(root, "MIDI_BasicPitch_7分轨_LA_20261011", "midi_raw", ...
                   "01_stem_vocals_basic_pitch.csv");

vocalStem = "01_stem_vocals.wav";
accompanimentStems = ["02_stem_drum.wav", "03_stem_bass.wav", ...
    "04_stem_piano.wav", "05_stem_acoustic_guitar.wav", ...
    "06_stem_electric_guitar.wav", "07_back_no_multistem.wav"];

noteGapSeconds    = 0.30;   % inter-note gap that ends a phrase
minPhraseSeconds  = 0.80;   % shorter than this cannot be judged or acted on
minNotesPerPhrase = 3;
roundtripGateDb   = -30.0;  % V + A must reconstruct the original this well
fadeSeconds       = 0.020;
maxExports        = 6;      % hard cap, reported, never silent

auditionDir = fullfile(ctx.outputDir, 'audition');
if ~isfolder(auditionDir)
    mkdir(auditionDir);
end
failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: stems, decomposition gate ---------------------------------
fprintf('[S011] stage 1: stems and decomposition gate\n');
stageTimer = tic;
[vocal, fs] = audioread(fullfile(stemDir, vocalStem));
vocal = vocal(:, 1:2);
accompaniment = zeros(size(vocal));
for index = 1:numel(accompanimentStems)
    [part, partRate] = audioread(fullfile(stemDir, accompanimentStems(index)));
    if partRate ~= fs
        error('MoodifyLab:S011:RateMismatch', 'Stem %s has a different rate.', ...
            accompanimentStems(index));
    end
    part = part(:, 1:2);
    frames = min(size(part, 1), size(accompaniment, 1));
    if frames < size(accompaniment, 1)
        accompaniment = accompaniment(1:frames, :);
        vocal = vocal(1:frames, :);
    end
    accompaniment(1:frames, :) = accompaniment(1:frames, :) + part(1:frames, :);
end

% The decomposition is only meaningful if V + A is the original. Without this
% gate a balance number cannot be attributed to the master at all.
[original, originalRate] = audioread(originalPath);
if originalRate ~= fs
    error('MoodifyLab:S011:RateMismatch', 'Original has a different rate.');
end
frames = min([size(original,1), size(vocal,1), size(accompaniment,1)]);
original = original(1:frames, 1:2);
vocal = vocal(1:frames, :);
accompaniment = accompaniment(1:frames, :);
reconstruction = vocal + accompaniment;
residual = original - reconstruction;
relativeErrorDb = 20*log10(sqrt(mean(residual(:).^2)) / (sqrt(mean(original(:).^2)) + eps) + eps);
reconstructionCorrelation = localCorrelation(original, reconstruction);
fprintf('[S011]   V + A vs original: corr %.9f, relative error %.3f dB\n', ...
    reconstructionCorrelation, relativeErrorDb);
metrics.decomposition = struct('correlation', reconstructionCorrelation, ...
    'relativeErrorDb', relativeErrorDb, 'gateDb', roundtripGateDb, ...
    'passed', relativeErrorDb <= roundtripGateDb, ...
    'frames', frames, 'sampleRate', fs);
if relativeErrorDb > roundtripGateDb
    failures(end + 1) = "DECOMPOSITION_GATE_FAILED"; %#ok<AGROW>
end
fprintf('[S011]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: phrase boundaries from the note transcription -------------
fprintf('[S011] stage 2: phrase boundaries\n');
stageTimer = tic;
% Read the two columns needed by hand. The file's pitch_bend field is itself a
% variable-length comma-separated list, so rows carry more fields than the
% header has names; readtable would either fail on the ragged rows or mint
% unnamed variables. Only the first two columns are wanted.
[noteStart, noteEnd] = readNoteTimes(noteCsv);
[noteStart, order] = sort(noteStart);
noteEnd = noteEnd(order);

phrases = zeros(0, 4);   % start, end, noteCount, noteSpan
if numel(noteStart) >= minNotesPerPhrase
    breaks = find((noteStart(2:end) - noteEnd(1:end-1)) > noteGapSeconds);
    bounds = [0; breaks; numel(noteStart)];
    for index = 1:(numel(bounds) - 1)
        first = bounds(index) + 1;
        last = bounds(index + 1);
        count = last - first + 1;
        if count < minNotesPerPhrase
            continue;
        end
        startSecond = noteStart(first);
        endSecond = noteEnd(last);
        if (endSecond - startSecond) < minPhraseSeconds
            continue;
        end
        phrases(end + 1, :) = [startSecond, endSecond, count, ...
            endSecond - startSecond]; %#ok<AGROW>
    end
end
fprintf('[S011]   %d phrases from a %.2f s note gap (min %.2f s, min %d notes)\n', ...
    size(phrases, 1), noteGapSeconds, minPhraseSeconds, minNotesPerPhrase);
if isempty(phrases)
    error('MoodifyLab:S011:NoPhrases', 'No phrases survived segmentation.');
end
metrics.segmentation = struct('noteGapSeconds', noteGapSeconds, ...
    'minPhraseSeconds', minPhraseSeconds, 'minNotesPerPhrase', minNotesPerPhrase, ...
    'phraseCount', size(phrases, 1), ...
    'medianPhraseSeconds', median(phrases(:, 4)), ...
    'noteSourceIsReferenceOnly', true);
fprintf('[S011]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: vocal activity gate ---------------------------------------
% Measured bimodality puts the valley at -75..-65 dBFS. The gate sits in the
% middle of it so the result is insensitive to the exact value; the occupancy
% plateau (-70 -> -55 changes occupancy by 0.9 points) is what makes it safe.
fprintf('[S011] stage 3: vocal activity gate\n');
stageTimer = tic;
vocalMono = mean(vocal, 2);
hop = round(0.010 * fs);
window = round(0.040 * fs);
frameCount = floor((numel(vocalMono) - window) / hop);
frameRms = zeros(frameCount, 1);
for index = 1:frameCount
    span = (index-1)*hop + (1:window);
    frameRms(index) = 20*log10(sqrt(mean(vocalMono(span).^2)) + eps);
end
frameTime = ((1:frameCount)' - 1) * 0.010;
activityThresholdDbfs = -70;
activeFrames = frameRms > activityThresholdDbfs;
metrics.activityGate = struct('thresholdDbfs', activityThresholdDbfs, ...
    'activePercent', 100 * mean(activeFrames), ...
    'histogramValleyDbfs', [-75, -65]);

% Drop phrases that straddle inactive material (the instrumental break).
keep = false(size(phrases, 1), 1);
for index = 1:size(phrases, 1)
    inside = frameTime >= phrases(index, 1) & frameTime <= phrases(index, 2);
    if ~any(inside)
        continue;
    end
    keep(index) = mean(activeFrames(inside)) >= 0.80;
end
droppedByGate = sum(~keep);
phrases = phrases(keep, :);
metrics.activityGate.phrasesDropped = droppedByGate;
fprintf('[S011]   gate at %.0f dBFS keeps %.1f%% of frames; dropped %d phrase(s)\n', ...
    activityThresholdDbfs, 100 * mean(activeFrames), droppedByGate);
if size(phrases, 1) < 5
    failures(end + 1) = "TOO_FEW_PHRASES_AFTER_GATE"; %#ok<AGROW>
end
fprintf('[S011]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: per-phrase balance ----------------------------------------
fprintf('[S011] stage 4: per-phrase balance\n');
stageTimer = tic;
phraseCount = size(phrases, 1);
vocalDb = zeros(phraseCount, 1);
accompanimentDb = zeros(phraseCount, 1);
balanceDb = zeros(phraseCount, 1);
for index = 1:phraseCount
    first = max(1, round(phrases(index, 1) * fs) + 1);
    last = min(frames, round(phrases(index, 2) * fs));
    span = first:last;
    vocalDb(index) = 20*log10(sqrt(mean(vocalMono(span).^2)) + eps);
    accompanimentMono = mean(accompaniment(span, :), 2);
    accompanimentDb(index) = 20*log10(sqrt(mean(accompanimentMono.^2)) + eps);
    balanceDb(index) = vocalDb(index) - accompanimentDb(index);
end

% Distribution FIRST, threshold second. An earlier study in this project set a
% threshold before looking at the spread and flagged 7 of 10 bands, so the
% spread is measured and printed before any flag is chosen.
balanceMedian = median(balanceDb);
balanceMad = median(abs(balanceDb - balanceMedian));
scale = 1.4826 * balanceMad;
if scale <= eps
    scale = max(std(balanceDb), 0.5);
    failures(end + 1) = "BALANCE_SCALE_DEGENERATE"; %#ok<AGROW>
end
robustZ = (balanceDb - balanceMedian) / scale;
metrics.balance = struct('medianDb', balanceMedian, 'madDb', balanceMad, ...
    'scaleDb', scale, 'minDb', min(balanceDb), 'maxDb', max(balanceDb), ...
    'spreadDb', max(balanceDb) - min(balanceDb), ...
    'stdDb', std(balanceDb), 'robustZMin', min(robustZ), 'robustZMax', max(robustZ));
fprintf('[S011]   V-A balance: median %.2f dB, MAD %.2f, spread %.2f dB (%.2f-%.2f)\n', ...
    balanceMedian, balanceMad, metrics.balance.spreadDb, min(balanceDb), max(balanceDb));
fprintf('[S011]   robust z range %.2f .. %.2f\n', min(robustZ), max(robustZ));

% Sensitivity: how many phrases are flagged at each cutoff. Reported so the
% reader can see how much the headline depends on the chosen number.
cutoffs = [1.5, 2.0, 2.5, 3.0, 4.0];
flaggedAtCutoff = zeros(size(cutoffs));
for index = 1:numel(cutoffs)
    flaggedAtCutoff(index) = sum(abs(robustZ) > cutoffs(index));
end
metrics.balanceSensitivity = struct('cutoffs', cutoffs, 'flagged', flaggedAtCutoff);
fprintf('[S011]   flagged at |z| > %s : %s\n', ...
    mat2str(cutoffs), mat2str(flaggedAtCutoff));
fprintf('[S011]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: rank and export -------------------------------------------
% Confidence for S012 couples how far the phrase departs with how much
% material there is to act on: a two-second outlier is easier to fix
% defensibly than a one-second one.
fprintf('[S011] stage 5: rank and export\n');
stageTimer = tic;
actionable = phrases(:, 4) >= 1.5 & phrases(:, 3) >= 5;
confidence = abs(robustZ) .* min(phrases(:, 4) / 3, 1.5);
confidence(~actionable) = -Inf;
[~, ranked] = sort(confidence, 'descend');

candidateTable = table((1:phraseCount)', phrases(:,1), phrases(:,2), ...
    phrases(:,3), phrases(:,4), vocalDb, accompanimentDb, balanceDb, robustZ, ...
    confidence, actionable, ...
    'VariableNames', {'phrase', 'start_s', 'end_s', 'note_count', 'duration_s', ...
    'vocal_db', 'accompaniment_db', 'balance_db', 'robust_z', 'confidence', ...
    'actionable'});
writetable(candidateTable, fullfile(ctx.outputDir, 's011_phrase_balance.csv'));

exported = 0;
exportRows = table();
for index = 1:phraseCount
    if exported >= maxExports
        break;
    end
    candidate = ranked(index);
    if ~actionable(candidate)
        break;
    end
    first = max(1, round(phrases(candidate,1) * fs) + 1);
    last = min(frames, round(phrases(candidate,2) * fs));
    span = first:last;
    vSeg = applyFades(vocal(span, :), fs, fadeSeconds);
    aSeg = applyFades(accompaniment(span, :), fs, fadeSeconds);
    mixSeg = applyFades(reconstruction(span, :), fs, fadeSeconds);
    stem = sprintf('%02d_phrase_%02d_%07.1f-%07.1f', exported + 1, candidate, ...
        phrases(candidate,1), phrases(candidate,2));
    audiowrite(fullfile(auditionDir, char(stem + "_vocals.wav")), vSeg, fs, 'BitsPerSample', 24);
    audiowrite(fullfile(auditionDir, char(stem + "_accompaniment.wav")), aSeg, fs, 'BitsPerSample', 24);
    audiowrite(fullfile(auditionDir, char(stem + "_mix.wav")), mixSeg, fs, 'BitsPerSample', 24);
    exported = exported + 1;
    exportRows = [exportRows; table(exported, candidate, phrases(candidate,1), ...
        phrases(candidate,2), balanceDb(candidate), robustZ(candidate), ...
        string(stem + "_vocals.wav"), string(stem + "_accompaniment.wav"), ...
        string(stem + "_mix.wav"), ...
        'VariableNames', {'export', 'phrase', 'start_s', 'end_s', ...
        'balance_db', 'robust_z', 'vocals_wav', 'accompaniment_wav', 'mix_wav'})]; %#ok<AGROW>
end
if ~isempty(exportRows)
    writetable(exportRows, fullfile(ctx.outputDir, 's011_exports.csv'));
end
capApplied = sum(actionable) > maxExports;
if capApplied
    failures(end + 1) = "EXPORT_CAP_APPLIED"; %#ok<AGROW>
end
metrics.candidates = struct('phraseCount', phraseCount, ...
    'actionableCount', sum(actionable), 'exported', exported, ...
    'maxExports', maxExports, 'capApplied', capApplied, ...
    'bestPhrase', ranked(1), 'bestConfidence', confidence(ranked(1)), ...
    'bestBalanceDb', balanceDb(ranked(1)), ...
    'bestPhraseStartS', phrases(ranked(1), 1), ...
    'bestPhraseEndS', phrases(ranked(1), 2), ...
    'bestPhraseNotes', phrases(ranked(1), 3), ...
    'bestPhraseSeconds', phrases(ranked(1), 4));
fprintf('[S011]   %d actionable of %d phrases; exported %d set(s) (cap %d, applied %d)\n', ...
    sum(actionable), phraseCount, exported, maxExports, capApplied);
fprintf('[S011]   best phrase #%d at %.2f-%.2f s, balance %+.2f dB, |z| %.2f\n', ...
    ranked(1), phrases(ranked(1),1), phrases(ranked(1),2), ...
    balanceDb(ranked(1)), abs(robustZ(ranked(1))));
fprintf('[S011]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Figures -------------------------------------------------------------
% Figure failures are caught, not fatal. By this point the measurements and
% every CSV are already valid; losing them because a plot call failed wastes a
% run and hides the numbers behind a stack. The error is recorded and printed
% so it cannot pass unnoticed.
fprintf('[S011] figures\n');
stageTimer = tic;
try
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
plot(frameTime, frameRms, 'LineWidth', 0.8); hold on;
yline(activityThresholdDbfs, 'k--', 'LineWidth', 0.8);
grid on; xlabel('Time (s)'); ylabel('Vocal level (dBFS, 40 ms)');
legend('Vocal stem', sprintf('%d dBFS gate', activityThresholdDbfs), ...
    'Location', 'southeast');
title('Vocal stem level; gate sits in the measured bimodal valley');
nexttile;
histogram(frameRms, 80);
xlabel('Vocal level (dBFS)'); ylabel('Count'); grid on;
title('Bimodal: artifact hump near -90, vocal body near -25');
nexttile;
stem(1:phraseCount, balanceDb, 'Marker', 'none'); hold on;
yline(balanceMedian, 'k-', 'LineWidth', 0.9);
yline(balanceMedian + 2*scale, 'k--', 'LineWidth', 0.7);
yline(balanceMedian - 2*scale, 'k--', 'LineWidth', 0.7);
grid on; xlabel('Phrase'); ylabel('Vocals minus accompaniment (dB)');
title(sprintf('Per-phrase balance; median %.2f dB, spread %.2f dB', ...
    balanceMedian, metrics.balance.spreadDb));
nexttile;
plot(cutoffs, flaggedAtCutoff, 'o-', 'LineWidth', 1.2);
grid on; xlabel('|robust z| cutoff'); ylabel('Phrases flagged');
title('Threshold sensitivity');
contract = moodifylab.figureContract("S011-vocal-accompaniment-balance", ...
    Conclusion="Locates phrases whose vocals-to-accompaniment balance departs from this song's own distribution, and exports them for listening.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["LALAL 7-stem set", "自己的神话3.wav", ...
                "01_stem_vocals_basic_pitch.csv (REFERENCE_ONLY)"], ...
    Units=["seconds", "dBFS", "decibels", "robust z"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT; the reference is this song's own balance distribution, not a target", ...
    Uncertainty=sprintf("%d phrases; scale %.2f dB from MAD. Phrase boundaries inherit the REFERENCE_ONLY status of the note transcription they come from.", ...
        phraseCount, scale), ...
    Limitations="The LALAL set has one vocal stem, so this measures VOCALS (lead and backing together) versus accompaniment, not lead versus accompaniment. An outlier is a candidate for listening, not a defect -- a deliberately buried or pushed vocal is a legitimate production choice. No processing is applied and no processed audio is written.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig22_vocal_accompaniment_balance", contract);
fprintf('[S011]   figures done in %.1f s\n', toc(stageTimer));
catch figureError
    failures(end + 1) = "FIGURES_FAILED"; %#ok<AGROW>
    fprintf(2, '[S011]   FIGURES FAILED: %s\n', figureError.identifier);
    fprintf(2, '[S011]   %s\n', figureError.message);
    for frameIndex = 1:numel(figureError.stack)
        fprintf(2, '[S011]      at %s:%d\n', ...
            figureError.stack(frameIndex).name, figureError.stack(frameIndex).line);
    end
    fprintf(2, '[S011]   measurements and CSVs are unaffected; continuing.\n');
    close all force;
end

%% ---- Persist -------------------------------------------------------------
scalars = {
    'phrases_total', phraseCount;
    'phrases_actionable', sum(actionable);
    'phrases_dropped_by_gate', droppedByGate;
    'decomposition_relative_error_db', relativeErrorDb;
    'balance_median_db', balanceMedian;
    'balance_mad_db', balanceMad;
    'balance_spread_db', metrics.balance.spreadDb;
    'robust_z_min', min(robustZ);
    'robust_z_max', max(robustZ);
    'exports_written', exported;
    'export_cap_applied', double(capApplied);
    'best_phrase_index', ranked(1);
    'best_phrase_start_s', phrases(ranked(1),1);
    'best_phrase_end_s', phrases(ranked(1),2);
    'best_phrase_balance_db', balanceDb(ranked(1));
    };
writetable(cell2table(scalars, 'VariableNames', {'metric', 'value'}), ...
    fullfile(ctx.outputDir, 's011_summary.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S011";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "Locates and exports candidate phrases for listening. It does not judge " ...
    "what is audible and applies no processing."];
result.limitations = [ ...
    "Phrase boundaries come from a REFERENCE_ONLY note transcription, so they " ...
    "inherit that status -- a missed or spurious note moves a boundary. The " ...
    "vocal stem contains lead and backing together, so this is vocals versus " ...
    "accompaniment. Balance outliers are candidates, not defects. n=1."];
fprintf('[S011] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S011] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function [starts, ends] = readNoteTimes(path)
% Robust reader for the note-events CSV: take the first two comma-separated
% fields of each data row and ignore the rest.
fileId = fopen(path, 'r', 'n', 'UTF-8');
if fileId < 0
    error('MoodifyLab:S011:NoteCsvMissing', 'Cannot open %s', path);
end
cleanup = onCleanup(@() fclose(fileId));
fgetl(fileId);                       % header
starts = zeros(0, 1);
ends = zeros(0, 1);
while true
    line = fgetl(fileId);
    if ~ischar(line)
        break;
    end
    line = strtrim(line);
    if isempty(line)
        continue;
    end
    fields = strsplit(line, ',');
    if numel(fields) < 2
        continue;
    end
    startValue = str2double(fields{1});
    endValue = str2double(fields{2});
    if isnan(startValue) || isnan(endValue)
        continue;
    end
    starts(end + 1, 1) = startValue; %#ok<AGROW>
    ends(end + 1, 1) = endValue; %#ok<AGROW>
end
clear cleanup;
if isempty(starts)
    error('MoodifyLab:S011:NoNotes', 'No usable note rows in %s', path);
end
end

% -------------------------------------------------------------------------
function value = localCorrelation(a, b)
x = a(:) - mean(a(:));
y = b(:) - mean(b(:));
denominator = sqrt(sum(x.^2) * sum(y.^2));
if denominator <= eps
    value = 0;
else
    value = sum(x .* y) / denominator;
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
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end
