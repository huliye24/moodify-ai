function result = study012_vocal_stem_local_diagnostic(ctx)
%STUDY012_VOCAL_STEM_LOCAL_DIAGNOSTIC Diagnose the LALAL VOCAL STEM in isolation.
%
%   WHY THIS IS SEPARATE FROM S011
%   S011 measured V minus A, which answers "did the vocal/accompaniment
%   RELATIONSHIP change". That is a mix-balance question, and it cannot answer
%   "what in the vocal itself needs repair". Worse, ranking on |z(V-A)| let the
%   accompaniment drive the result: the phrase S011 called best (16) had a
%   perfectly normal vocal (z = -0.66) and an elevated accompaniment
%   (z = +1.81). If the goal is to process the vocal, the accompaniment must
%   not enter the first-round ranking at all.
%
%   So this study looks at the VOCAL STEM ONLY and asks one question:
%   is this phrase anomalous AS A VOCAL?
%
%   WHAT IS AND IS NOT ATTRIBUTABLE
%   V + A reconstructs the original to -60.397 dB, and that is an identity, not
%   a measurement. It constrains what a low vocal level can mean:
%     V low AND A high  -> the separator moved energy from vocal to
%                          accompaniment. That IS attributable to separation.
%     V low AND A low   -> the master is genuinely quieter there, so the
%                          separator did not lose energy; whether the drop is
%                          performance or mix is a HUMAN judgement.
%     V low AND A normal -> same conclusion as above; the missing energy has
%                          nowhere to have gone.
%   This study reports which of the three applies. It does NOT conclude that a
%   low phrase should be raised -- a soft delivery, a tail, a separation miss
%   and a boundary cut all look similar in level alone.
%
%   NO PROCESSING. Nothing is EQ'd, gained, gated or written as processed audio.
%   Exports are copies of existing material with context, for listening.

fprintf('[S012] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
stemDir = fullfile(root, "LALAL_AI分轨_20261011", "自己的神话3_multistem");
originalPath = fullfile(root, "自己的神话3.wav");
noteCsv = fullfile(root, "MIDI_BasicPitch_7分轨_LA_20261011", "midi_raw", ...
                   "01_stem_vocals_basic_pitch.csv");
vocalStemPath = fullfile(stemDir, "01_stem_vocals.wav");

accompanimentStems = ["02_stem_drum.wav", "03_stem_bass.wav", ...
    "04_stem_piano.wav", "05_stem_acoustic_guitar.wav", ...
    "06_stem_electric_guitar.wav", "07_back_no_multistem.wav"];

noteGapSeconds   = 0.30;
minPhraseSeconds = 0.80;
minNotesPerPhrase = 3;
contextSeconds   = 8.0;     % audio either side of a focus phrase in the exports
fadeSeconds      = 0.020;
focusIndices     = [6, 16, 26, 27, 5];  % S011's vocal-side candidates and neighbours
maxFocusExports  = 6;

% Detector parameters, all engineering defaults, all reported.
dropoutBelowPhraseMedianDb = 12.0;
dropoutMinSeconds = 0.060;
seamJumpThresholdDb = 6.0;
sibilanceBandHz = [6000, 10000];
plosiveBandHz = [40, 160];

auditionDir = fullfile(ctx.outputDir, 'audition');
if ~isfolder(auditionDir)
    mkdir(auditionDir);
end
failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: load the vocal stem, and the pieces needed for attribution --
fprintf('[S012] stage 1: load\n');
stageTimer = tic;
[vocal, fs] = audioread(vocalStemPath);
vocal = vocal(:, 1:2);
[original, originalRate] = audioread(originalPath);
if originalRate ~= fs
    error('MoodifyLab:S012:RateMismatch', 'Original has a different rate.');
end

% The accompaniment is needed ONLY for the attribution test, never for ranking.
accompaniment = zeros(size(vocal));
for index = 1:numel(accompanimentStems)
    [part, partRate] = audioread(fullfile(stemDir, accompanimentStems(index)));
    if partRate ~= fs
        error('MoodifyLab:S012:RateMismatch', 'Stem %s has a different rate.', ...
            accompanimentStems(index));
    end
    part = part(:, 1:2);
    frames = min(size(part, 1), size(accompaniment, 1));
    if frames < size(accompaniment, 1)
        accompaniment = accompaniment(1:frames, :);
        vocal = vocal(1:frames, :);
        original = original(1:frames, :);
    end
    accompaniment(1:frames, :) = accompaniment(1:frames, :) + part(1:frames, :);
end
frames = min([size(vocal,1), size(original,1), size(accompaniment,1)]);
vocal = vocal(1:frames, :);
original = original(1:frames, 1:2);
accompaniment = accompaniment(1:frames, :);
vocalMono = mean(vocal, 2);
originalMono = mean(original, 2);
accompanimentMono = mean(accompaniment, 2);

residual = original - (vocal + accompaniment);
identityDb = 20*log10(sqrt(mean(residual(:).^2)) / (sqrt(mean(original(:).^2)) + eps) + eps);
fprintf('[S012]   vocal stem %d frames @ %d Hz; V+A identity %.3f dB\n', ...
    frames, fs, identityDb);
metrics.identity = struct('vPlusARelativeErrorDb', identityDb, 'frames', frames);
if identityDb > -30
    failures(end + 1) = "IDENTITY_GATE_FAILED"; %#ok<AGROW>
end
fprintf('[S012]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: phrases, same boundaries as S011 ---------------------------
fprintf('[S012] stage 2: phrase boundaries\n');
stageTimer = tic;
[noteStart, noteEnd] = readNoteTimes(noteCsv);
[noteStart, order] = sort(noteStart);
noteEnd = noteEnd(order);
phrases = zeros(0, 4);
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
phraseCount = size(phrases, 1);
fprintf('[S012]   %d phrases (note gap %.2f s)\n', phraseCount, noteGapSeconds);
metrics.segmentation = struct('phraseCount', phraseCount, ...
    'noteGapSeconds', noteGapSeconds, ...
    'boundariesInheritReferenceOnlyStatus', true);
fprintf('[S012]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: per-phrase vocal measurements ------------------------------
fprintf('[S012] stage 3: per-phrase vocal measurements\n');
stageTimer = tic;
hop = round(0.010 * fs);
window = round(0.040 * fs);
vocalRms = zeros(phraseCount, 1);
vocalPeak = zeros(phraseCount, 1);
vocalCrest = zeros(phraseCount, 1);
vocalStability = zeros(phraseCount, 1);      % std of short-time RMS within the phrase
dropoutSeconds = zeros(phraseCount, 1);
dropoutCount = zeros(phraseCount, 1);
sibilanceRatioDb = zeros(phraseCount, 1);
plosiveRatioDb = zeros(phraseCount, 1);
originalRms = zeros(phraseCount, 1);
accompanimentRms = zeros(phraseCount, 1);
boundaryJumpDb = zeros(phraseCount, 2);      % entry, exit jump vs the phrase body
boundaryMidNote = false(phraseCount, 1);

for index = 1:phraseCount
    first = max(1, round(phrases(index,1) * fs) + 1);
    last = min(frames, round(phrases(index,2) * fs));
    span = first:last;
    segment = vocalMono(span);
    if numel(segment) < window
        continue;
    end
    vocalRms(index) = 20*log10(sqrt(mean(segment.^2)) + eps);
    vocalPeak(index) = 20*log10(max(abs(segment)) + eps);
    vocalCrest(index) = vocalPeak(index) - vocalRms(index);
    originalRms(index) = 20*log10(sqrt(mean(originalMono(span).^2)) + eps);
    accompanimentRms(index) = 20*log10(sqrt(mean(accompanimentMono(span).^2)) + eps);

    % Within-phrase stability and dropouts, both from a 10 ms grid.
    frameCount = floor((numel(segment) - window) / hop);
    if frameCount >= 3
        frameRms = zeros(frameCount, 1);
        for frameIndex = 1:frameCount
            inner = (frameIndex-1)*hop + (1:window);
            frameRms(frameIndex) = 20*log10(sqrt(mean(segment(inner).^2)) + eps);
        end
        vocalStability(index) = std(frameRms);
        bodyLevel = median(frameRms);
        below = frameRms < (bodyLevel - dropoutBelowPhraseMedianDb);
        runs = 0;
        runLengths = [];
        counter = 0;
        for frameIndex = 1:numel(below)
            if below(frameIndex)
                counter = counter + 1;
            else
                if counter > 0
                    runLengths(end + 1) = counter * hop / fs; %#ok<AGROW>
                end
                counter = 0;
            end
        end
        if counter > 0
            runLengths(end + 1) = counter * hop / fs;
        end
        longRuns = runLengths(runLengths >= dropoutMinSeconds);
        dropoutCount(index) = numel(longRuns);
        dropoutSeconds(index) = sum(longRuns);
    end

    % Sibilance and plosive energy ratios, against the phrase's own mean.
    [power, freqs] = pwelch(segment, hann(min(8192, numel(segment))), [], ...
        min(8192, numel(segment)), fs);
    totalPower = sum(power) + eps;
    sibMask = freqs >= sibilanceBandHz(1) & freqs < sibilanceBandHz(2);
    ploMask = freqs >= plosiveBandHz(1) & freqs < plosiveBandHz(2);
    sibilanceRatioDb(index) = 10*log10(sum(power(sibMask)) / totalPower + eps);
    plosiveRatioDb(index) = 10*log10(sum(power(ploMask)) / totalPower + eps);

    % Boundary jumps: compare the first/last 50 ms against the phrase body.
    edge = min(round(0.050 * fs), floor(numel(segment) / 4));
    if edge >= 1
        head = 20*log10(sqrt(mean(segment(1:edge).^2)) + eps);
        tail = 20*log10(sqrt(mean(segment(end-edge+1:end).^2)) + eps);
        boundaryJumpDb(index, :) = [head - vocalRms(index), tail - vocalRms(index)];
    end

    % Does a transcribed note straddle either boundary? If so the boundary is
    % an artefact of the note-gap rule rather than a musical phrase edge.
    straddle = any(noteStart < phrases(index,1) & noteEnd > phrases(index,1)) || ...
               any(noteStart < phrases(index,2) & noteEnd > phrases(index,2));
    boundaryMidNote(index) = straddle;
end

% Robust z for the vocal level, computed on the vocal stem alone.
vocalMedian = median(vocalRms);
vocalMad = median(abs(vocalRms - vocalMedian));
vocalScale = 1.4826 * vocalMad;
if vocalScale <= eps
    vocalScale = max(std(vocalRms), 0.5);
    failures(end + 1) = "VOCAL_SCALE_DEGENERATE"; %#ok<AGROW>
end
vocalZ = (vocalRms - vocalMedian) / vocalScale;

% Same for the other two, so the attribution test compares like with like.
originalMedian = median(originalRms);
originalScale = max(1.4826 * median(abs(originalRms - originalMedian)), 0.5);
originalZ = (originalRms - originalMedian) / originalScale;
accompanimentMedian = median(accompanimentRms);
accompanimentScale = max(1.4826 * median(abs(accompanimentRms - accompanimentMedian)), 0.5);
accompanimentZ = (accompanimentRms - accompanimentMedian) / accompanimentScale;

fprintf('[S012]   vocal level: median %.2f dBFS, MAD %.2f, z %.2f .. %.2f\n', ...
    vocalMedian, vocalMad, min(vocalZ), max(vocalZ));
metrics.vocalLevel = struct('medianDbfs', vocalMedian, 'madDb', vocalMad, ...
    'scaleDb', vocalScale, 'zMin', min(vocalZ), 'zMax', max(vocalZ), ...
    'minDbfs', min(vocalRms), 'maxDbfs', max(vocalRms));
fprintf('[S012]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: attribution test -------------------------------------------
% One of three cases per phrase, from the identity V + A = original:
%   MIGRATION   V low, A high  -> energy moved vocal -> accompaniment
%   MASTER_LOW  V low, A low   -> the master is quieter there
%   VOCAL_ONLY  V low, A normal-> the master is quieter there and the missing
%                                 energy has nowhere to have gone
fprintf('[S012] stage 4: attribution\n');
stageTimer = tic;
attribution = strings(phraseCount, 1);
for index = 1:phraseCount
    vocalLow = vocalZ(index) < -1.5;
    accompanimentHigh = accompanimentZ(index) > 1.5;
    accompanimentLow = accompanimentZ(index) < -1.5;
    if vocalLow && accompanimentHigh
        attribution(index) = "MIGRATION_TO_ACCOMPANIMENT";
    elseif vocalLow && accompanimentLow
        attribution(index) = "MASTER_LOW_BOTH_SIDES";
    elseif vocalLow
        attribution(index) = "VOCAL_LOW_ACCOMPANIMENT_NORMAL";
    elseif vocalZ(index) > 1.5
        attribution(index) = "VOCAL_HIGH";
    else
        attribution(index) = "IN_RANGE";
    end
end
% Explicit fields rather than counts.(makeValidName(label)). Dynamic field
% names are invisible to a static check, which cannot then tell a real typo
% from an assignment it failed to see; naming them costs one line each.
metrics.attributionCounts = struct( ...
    'MIGRATION_TO_ACCOMPANIMENT', sum(attribution == "MIGRATION_TO_ACCOMPANIMENT"), ...
    'MASTER_LOW_BOTH_SIDES', sum(attribution == "MASTER_LOW_BOTH_SIDES"), ...
    'VOCAL_LOW_ACCOMPANIMENT_NORMAL', sum(attribution == "VOCAL_LOW_ACCOMPANIMENT_NORMAL"), ...
    'VOCAL_HIGH', sum(attribution == "VOCAL_HIGH"), ...
    'IN_RANGE', sum(attribution == "IN_RANGE"));
fprintf('[S012]   migration %d, master-low %d, vocal-low-only %d, vocal-high %d, in-range %d\n', ...
    metrics.attributionCounts.MIGRATION_TO_ACCOMPANIMENT, ...
    metrics.attributionCounts.MASTER_LOW_BOTH_SIDES, ...
    metrics.attributionCounts.VOCAL_LOW_ACCOMPANIMENT_NORMAL, ...
    metrics.attributionCounts.VOCAL_HIGH, ...
    metrics.attributionCounts.IN_RANGE);
fprintf('[S012]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: focus phrases and exports ----------------------------------
fprintf('[S012] stage 5: focus phrases\n');
stageTimer = tic;
focusTable = table();
exported = 0;
for index = 1:numel(focusIndices)
    phrase = focusIndices(index);
    if phrase < 1 || phrase > phraseCount || exported >= maxFocusExports
        continue;
    end
    first = max(1, round(phrases(phrase,1) * fs) + 1);
    last = min(frames, round(phrases(phrase,2) * fs));
    if last <= first
        continue;
    end
    % Context clip: the phrase plus generous either side, so a listener can
    % hear what the performance is doing around it.
    contextFirst = max(1, round((phrases(phrase,1) - contextSeconds) * fs) + 1);
    contextLast = min(frames, round((phrases(phrase,2) + contextSeconds) * fs));
    contextSpan = contextFirst:contextLast;

    exported = exported + 1;
    fileStem = sprintf('%02d_phrase_%02d_%07.1f-%07.1f', exported, phrase, ...
        phrases(phrase,1), phrases(phrase,2));
    vocalContext = applyFades(vocal(contextSpan, :), fs, fadeSeconds);
    mixContext = applyFades(original(contextSpan, :), fs, fadeSeconds);
    audiowrite(fullfile(auditionDir, char(fileStem + "_vocal_context.wav")), ...
        vocalContext, fs, 'BitsPerSample', 24);
    audiowrite(fullfile(auditionDir, char(fileStem + "_mix_context.wav")), ...
        mixContext, fs, 'BitsPerSample', 24);

    focusTable = [focusTable; table(exported, phrase, phrases(phrase,1), ...
        phrases(phrase,2), phrases(phrase,3), phrases(phrase,4), ...
        vocalRms(phrase), vocalPeak(phrase), vocalCrest(phrase), ...
        vocalStability(phrase), dropoutCount(phrase), dropoutSeconds(phrase), ...
        sibilanceRatioDb(phrase), plosiveRatioDb(phrase), ...
        boundaryJumpDb(phrase,1), boundaryJumpDb(phrase,2), ...
        boundaryMidNote(phrase), vocalZ(phrase), accompanimentZ(phrase), ...
        originalZ(phrase), attribution(phrase), ...
        string(fileStem + "_vocal_context.wav"), ...
        string(fileStem + "_mix_context.wav"), ...
        'VariableNames', {'export', 'phrase', 'start_s', 'end_s', 'note_count', ...
        'duration_s', 'vocal_rms_dbfs', 'vocal_peak_dbfs', 'vocal_crest_db', ...
        'vocal_stability_db', 'dropout_count', 'dropout_seconds', ...
        'sibilance_ratio_db', 'plosive_ratio_db', ...
        'entry_jump_db', 'exit_jump_db', 'boundary_mid_note', ...
        'vocal_z', 'accompaniment_z', 'original_z', 'attribution', ...
        'vocal_context_wav', 'mix_context_wav'})]; %#ok<AGROW>

    fprintf('[S012]   phrase %d %.1f-%.1f s: vocal z %+.2f, accomp z %+.2f, orig z %+.2f -> %s\n', ...
        phrase, phrases(phrase,1), phrases(phrase,2), vocalZ(phrase), ...
        accompanimentZ(phrase), originalZ(phrase), attribution(phrase));
end
if ~isempty(focusTable)
    writetable(focusTable, fullfile(ctx.outputDir, 's012_focus_phrases.csv'));
end
metrics.focus = struct('requested', focusIndices, 'exported', exported, ...
    'contextSeconds', contextSeconds, 'maxFocusExports', maxFocusExports);
fprintf('[S012]   exported %d focus set(s) with %.0f s context\n', ...
    exported, contextSeconds);
fprintf('[S012]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: full per-phrase table --------------------------------------
allPhrases = table((1:phraseCount)', phrases(:,1), phrases(:,2), phrases(:,3), ...
    phrases(:,4), vocalRms, vocalPeak, vocalCrest, vocalStability, ...
    dropoutCount, dropoutSeconds, sibilanceRatioDb, plosiveRatioDb, ...
    boundaryJumpDb(:,1), boundaryJumpDb(:,2), boundaryMidNote, ...
    vocalZ, accompanimentZ, originalZ, attribution, ...
    'VariableNames', {'phrase', 'start_s', 'end_s', 'note_count', 'duration_s', ...
    'vocal_rms_dbfs', 'vocal_peak_dbfs', 'vocal_crest_db', 'vocal_stability_db', ...
    'dropout_count', 'dropout_seconds', 'sibilance_ratio_db', 'plosive_ratio_db', ...
    'entry_jump_db', 'exit_jump_db', 'boundary_mid_note', ...
    'vocal_z', 'accompaniment_z', 'original_z', 'attribution'});
writetable(allPhrases, fullfile(ctx.outputDir, 's012_phrase_diagnostics.csv'));

%% ---- Figures -------------------------------------------------------------
% Figure failures are caught, not fatal: by here every measurement and CSV is
% valid, and losing them to a plot call wastes the run.
fprintf('[S012] figures\n');
stageTimer = tic;
try
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
plot(1:phraseCount, vocalRms, 'o-', 'LineWidth', 1.1); hold on;
yline(vocalMedian, 'k-', 'LineWidth', 0.9);
yline(vocalMedian - 1.5*vocalScale, 'k--', 'LineWidth', 0.7);
grid on; xlabel('Phrase'); ylabel('Vocal RMS (dBFS)');
title(sprintf('Vocal stem level by phrase; median %.1f dBFS', vocalMedian));
nexttile;
bar([sum(vocalZ < -1.5), sum(vocalZ > 1.5), ...
     sum(accompanimentZ < -1.5), sum(accompanimentZ > 1.5)]);
set(gca, 'XTickLabel', {'vocal low', 'vocal high', 'accomp low', 'accomp high'});
ylabel('Phrases beyond |z|>1.5'); grid on;
title('Which side moves (attribution input)');
nexttile;
scatter(vocalZ, accompanimentZ, 30, 'filled'); hold on;
xline(0, 'k:'); yline(0, 'k:');
xline(-1.5, 'k--'); xline(1.5, 'k--');
yline(-1.5, 'k--'); yline(1.5, 'k--');
axis([-6 6 -12 6]); grid on;
xlabel('Vocal z'); ylabel('Accompaniment z');
title('Attribution map; lower-right quadrant = energy migrated');
nexttile;
plot(1:phraseCount, dropoutSeconds, 'o-', 'LineWidth', 1.1);
grid on; xlabel('Phrase'); ylabel('Dropout seconds');
title('Within-phrase dropouts below the phrase median by 12 dB');
contract = moodifylab.figureContract("S012-vocal-stem-diagnostic", ...
    Conclusion="Diagnoses the vocal stem on its own, and separates a phrase that is genuinely quiet from one where the separator moved energy away.", ...
    EvidenceRole="diagnostic", ...
    SourceData=["01_stem_vocals.wav", "自己的神话3.wav", "LALAL 7-stem set", ...
                "01_stem_vocals_basic_pitch.csv (REFERENCE_ONLY)"], ...
    Units=["seconds", "dBFS", "decibels", "robust z", "phrase count"], ...
    CalibrationStatus="UNCALIBRATED_ENGINEERING_DEFAULT; thresholds are engineering defaults", ...
    Uncertainty=sprintf("%d phrases; vocal scale %.2f dB from MAD. Phrase boundaries inherit the REFERENCE_ONLY status of the note transcription.", ...
        phraseCount, vocalScale), ...
    Limitations="A low vocal level does NOT imply the phrase should be raised. A soft delivery, a held tail, a separation miss and a boundary cut all look the same in level alone; only listening distinguishes them. The accompaniment appears ONLY in the attribution test and never in the ranking. No processing is applied and no processed audio is written.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig23_vocal_stem_diagnostic", contract);
fprintf('[S012]   figures done in %.1f s\n', toc(stageTimer));
catch figureError
    failures(end + 1) = "FIGURES_FAILED"; %#ok<AGROW>
    fprintf(2, '[S012]   FIGURES FAILED: %s\n', figureError.identifier);
    fprintf(2, '[S012]   %s\n', figureError.message);
    for frameIndex = 1:numel(figureError.stack)
        fprintf(2, '[S012]      at %s:%d\n', ...
            figureError.stack(frameIndex).name, figureError.stack(frameIndex).line);
    end
    fprintf(2, '[S012]   measurements and CSVs are unaffected; continuing.\n');
    close all force;
end

%% ---- Persist -------------------------------------------------------------
scalars = {
    'phrases_total', phraseCount;
    'identity_relative_error_db', identityDb;
    'vocal_median_dbfs', vocalMedian;
    'vocal_scale_db', vocalScale;
    'vocal_z_min', min(vocalZ);
    'vocal_z_max', max(vocalZ);
    'phrases_vocal_low', sum(vocalZ < -1.5);
    'phrases_vocal_high', sum(vocalZ > 1.5);
    'phrases_migration', metrics.attributionCounts.MIGRATION_TO_ACCOMPANIMENT;
    'phrases_master_low', metrics.attributionCounts.MASTER_LOW_BOTH_SIDES;
    'phrases_vocal_low_only', metrics.attributionCounts.VOCAL_LOW_ACCOMPANIMENT_NORMAL;
    'focus_exported', exported;
    'focus_context_seconds', contextSeconds;
    'phrases_with_mid_note_boundary', sum(boundaryMidNote);
    };
writetable(cell2table(scalars, 'VariableNames', {'metric', 'value'}), ...
    fullfile(ctx.outputDir, 's012_summary.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S012";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "Diagnoses the vocal stem in isolation and exports focus phrases with context. " ...
    "It does not decide that any phrase should be processed, and applies no processing."];
result.limitations = [ ...
    "Level alone cannot separate a soft delivery, a held tail, a separation miss " ...
    "and a boundary cut -- listening is required. Phrase boundaries come from a " ...
    "REFERENCE_ONLY transcription. The vocal stem contains lead and backing " ...
    "together. n=1."];
fprintf('[S012] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S012] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function [starts, ends] = readNoteTimes(path)
% The file's pitch_bend field is a variable-length comma-separated list, so
% rows carry 14 to 281 fields against a 5-name header. Take the first two.
fileId = fopen(path, 'r', 'n', 'UTF-8');
if fileId < 0
    error('MoodifyLab:S012:NoteCsvMissing', 'Cannot open %s', path);
end
cleanup = onCleanup(@() fclose(fileId));
fgetl(fileId);
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
    error('MoodifyLab:S012:NoNotes', 'No usable note rows in %s', path);
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
