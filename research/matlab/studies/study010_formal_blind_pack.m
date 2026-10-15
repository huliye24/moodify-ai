function result = study010_formal_blind_pack(ctx)
%STUDY010_FORMAL_BLIND_PACK Build a de-duplicated, randomized, scoreable blind list.
%
%   Why this replaces S009. Three defects were verified in the S009 pack:
%
%     1. THREE cross-class overlaps. Every "largest_processing_delta" window
%        overlapped a "high_correlation" window (7-12 vs 7-14, 114-125 vs
%        123-130, 158-165 vs 159-166). The listener heard the same music twice
%        under two different class labels. S009's non-overlap rule was applied
%        PER CLASS, so it could not see collisions across classes.
%     2. Variable excerpt length: 6, 12, 8, 7, 8, 8, 8, 8, 8, 8 s.
%     3. The X/Y assignment alternated perfectly (YXYXYXYXYX). A predictable
%        order is exactly what randomisation exists to remove.
%
%   This study fixes all three, adds catch trials so a listener's
%   false-positive rate is measurable, and emits a score sheet that can be
%   filled in directly.
%
%   It MEASURES AND EXPORTS ONLY. No EQ, no compression, no widening, and no
%   processed master is written. Excerpts are copies of existing material.
%
%   BLINDING DISCIPLINE: the X/Y mapping is written to a separate file named
%   to make its status obvious. Do not open it until every pair has been
%   scored. The blinding here is PROCEDURAL (the mapping lives in another
%   file), not cryptographic: ctx.seed is recorded and the mapping is on disk.
%   It removes ORDER BIAS, which is what the S009 defect was.

fprintf('[S010] start %s\n', datestr(now, 'HH:MM:SS'));

songRoot = "E:\荣景文川 文化集团 2026\逍遥仙";
root = fullfile(songRoot, "挑选");
originalPath = fullfile(root, "自己的神话3.wav");
masterPath = fullfile(root, "LALAL重制版_vs_Suno分轨重制版_20261011", ...
                      "自己的神话_LALAL分轨重制_48k24.wav");

% ---- design constants ----------------------------------------------------
excerptSeconds   = 8;     % every excerpt is exactly this long
pairsPerClass    = 3;
catchTrialCount  = 3;     % X and Y are the SAME audio; measures false positives
guardSeconds     = 3;     % minimum untouched gap between allocated windows
windowSeconds    = 4;     % band-delta analysis window
fadeSeconds      = 0.030;
bandEdges = [20 60; 60 125; 125 250; 250 500; 500 1000; ...
             1000 2000; 2000 4000; 4000 8000; 8000 16000; 16000 20000];

auditionDir = fullfile(ctx.outputDir, 'audition');
if ~isfolder(auditionDir)
    mkdir(auditionDir);
end
failures = strings(0, 1);
metrics = struct();

%% ---- Stage 1: load and gate ---------------------------------------------
fprintf('[S010] stage 1: load and gate\n');
stageTimer = tic;
[original, fs] = audioread(originalPath);
[master, fsMaster] = audioread(masterPath);
if fsMaster ~= fs
    error('MoodifyLab:S010:RateMismatch', 'Sample rates differ.');
end
frames = min(size(original, 1), size(master, 1));
original = original(1:frames, 1:2);
master = master(1:frames, 1:2);
seconds = floor(frames / fs);
monoOriginal = mean(original, 2);
monoMaster = mean(master, 2);

correlation = nan(seconds, 1);
rmsMaster = nan(seconds, 1);
rmsOriginal = nan(seconds, 1);
peakDb = nan(seconds, 1);
for index = 1:seconds
    span = (index-1)*fs + (1:fs);
    sampleSpan = span(span <= frames);
    left = master(sampleSpan, 1);
    right = master(sampleSpan, 2);
    if numel(left) > 2 && std(left) > eps && std(right) > eps
        matrix = corrcoef(left, right);
        correlation(index) = matrix(1, 2);
    end
    rmsMaster(index) = 20*log10(sqrt(mean(monoMaster(sampleSpan).^2)) + eps);
    rmsOriginal(index) = 20*log10(sqrt(mean(monoOriginal(sampleSpan).^2)) + eps);
    peakDb(index) = 20*log10(max(abs(monoMaster(sampleSpan))) + eps);
end

% Activity gate. Windows made of quiet material are REMOVED, not labelled.
activityThreshold = max(-45, median(rmsOriginal) - 20);
active = (rmsOriginal > activityThreshold) & (rmsMaster > activityThreshold);
metrics.gating = struct('activityThresholdDbfs', activityThreshold, ...
    'activeSeconds', sum(active), 'totalSeconds', seconds);
fprintf('[S010]   activity threshold %.1f dBFS; %d of %d s active\n', ...
    activityThreshold, sum(active), seconds);
fprintf('[S010]   stage 1 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 2: same-render band delta ------------------------------------
fprintf('[S010] stage 2: same-render band delta\n');
stageTimer = tic;
bandOriginal = bandPowerPerWindow(original, fs, bandEdges, windowSeconds);
bandMaster = bandPowerPerWindow(master, fs, bandEdges, windowSeconds);
windowCount = min(size(bandOriginal, 1), size(bandMaster, 1));
bandDelta = bandMaster(1:windowCount, :) - bandOriginal(1:windowCount, :);
deltaStrength = max(abs(bandDelta), [], 2);
metrics.delta = struct('windowSeconds', windowSeconds, ...
    'medianDb', median(deltaStrength), ...
    'p95Db', prctile(deltaStrength, 95), ...
    'maxDb', max(deltaStrength));

% One value per second, so every class is scored on the same timebase.
deltaPerSecond = nan(seconds, 1);
for index = 1:windowCount
    span = (index-1)*windowSeconds + (1:windowSeconds);
    span = span(span <= seconds);
    deltaPerSecond(span) = deltaStrength(index);
end
fprintf('[S010]   max |band delta|: median %.3f, p95 %.3f, max %.3f dB\n', ...
    metrics.delta.medianDb, metrics.delta.p95Db, metrics.delta.maxDb);
fprintf('[S010]   stage 2 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 3: global allocation -----------------------------------------
% Greedy over ONE occupancy map shared by every class, so no window can be
% claimed twice. S009 applied non-overlap per class and produced three
% cross-class collisions.
fprintf('[S010] stage 3: global allocation\n');
stageTimer = tic;
lastStart = seconds - excerptSeconds + 1;
fullyActive = false(lastStart, 1);
for start = 1:lastStart
    fullyActive(start) = all(active(start:(start + excerptSeconds - 1)));
end
candidateStarts = find(fullyActive);
fprintf('[S010]   %d of %d possible %d s windows are fully active\n', ...
    numel(candidateStarts), lastStart, excerptSeconds);
if numel(candidateStarts) < pairsPerClass
    error('MoodifyLab:S010:TooFewWindows', ...
        'Only %d fully active windows available.', numel(candidateStarts));
end

classNames = ["high_correlation", "low_correlation", ...
              "largest_processing_delta", "control"];
classScores = {
    meanCorrelationPerWindow(correlation, candidateStarts, excerptSeconds), -1; ...
    meanCorrelationPerWindow(correlation, candidateStarts, excerptSeconds), +1; ...
    meanValuePerWindow(deltaPerSecond, candidateStarts, excerptSeconds), -1; ...
    abs(meanValuePerWindow(deltaPerSecond, candidateStarts, excerptSeconds) - median(deltaStrength)), +1};

occupied = false(1, seconds);
allocations = struct('class', {}, 'start', {}, 'end', {}, 'score', {});
for classIndex = 1:numel(classNames)
    scores = classScores{classIndex, 1};
    direction = classScores{classIndex, 2};      % -1 = high is best, +1 = low is best
    [~, order] = sort(direction * scores, 'ascend');
    taken = 0;
    for candidate = 1:numel(order)
        if taken >= pairsPerClass
            break;
        end
        start = candidateStarts(order(candidate));
        stop = start + excerptSeconds - 1;
        guardStart = max(1, start - guardSeconds);
        guardStop = min(seconds, stop + guardSeconds);
        if any(occupied(guardStart:guardStop))
            continue;
        end
        occupied(start:stop) = true;
        taken = taken + 1;
        allocations(end + 1) = struct('class', classNames(classIndex), ...
            'start', start, 'end', stop, 'score', scores(order(candidate))); %#ok<AGROW>
    end
    fprintf('[S010]   %-24s allocated %d of %d\n', classNames(classIndex), taken, pairsPerClass);
    if taken < pairsPerClass
        failures(end + 1) = "UNDERFILLED_" + upper(classNames(classIndex)); %#ok<AGROW>
    end
end

% Catch trials: both sides are the SAME audio. Without them a listener's
% false-positive rate is unknown, and "I heard a difference" cannot be
% interpreted. Drawn from windows nearest the median delta so they look
% like ordinary material.
% Walk the candidates explicitly. An earlier version built a matrix of guard
% spans and indexed occupied() with it, which is LINEAR indexing into the
% occupancy map and silently consults the wrong samples.
catchCandidates = zeros(0, 1);
for candidate = 1:numel(candidateStarts)
    start = candidateStarts(candidate);
    guardStart = max(1, start - guardSeconds);
    guardStop = min(seconds, start + excerptSeconds - 1 + guardSeconds);
    if ~any(occupied(guardStart:guardStop))
        catchCandidates(end + 1, 1) = start; %#ok<AGROW>
    end
end
catchAllocations = struct('class', {}, 'start', {}, 'end', {}, 'score', {});
if ~isempty(catchCandidates)
    catchScore = abs(meanValuePerWindow(deltaPerSecond, catchCandidates, excerptSeconds) ...
        - median(deltaStrength));
    [~, order] = sort(catchScore, 'ascend');
    taken = 0;
    for candidate = 1:numel(order)
        if taken >= catchTrialCount
            break;
        end
        start = catchCandidates(order(candidate));
        stop = start + excerptSeconds - 1;
        guardStart = max(1, start - guardSeconds);
        guardStop = min(seconds, stop + guardSeconds);
        if any(occupied(guardStart:guardStop))
            continue;
        end
        occupied(start:stop) = true;
        taken = taken + 1;
        catchAllocations(end + 1) = struct('class', "catch_trial", ...
            'start', start, 'end', stop, 'score', catchScore(order(candidate))); %#ok<AGROW>
    end
    fprintf('[S010]   %-24s allocated %d of %d\n', "catch_trial", taken, catchTrialCount);
end
metrics.allocation = struct('classes', classNames, 'pairsPerClass', pairsPerClass, ...
    'catchTrials', numel(catchAllocations), 'guardSeconds', guardSeconds, ...
    'excerptSeconds', excerptSeconds, 'fullyActiveWindows', numel(candidateStarts));
fprintf('[S010]   stage 3 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 4: randomise order and X/Y -----------------------------------
% S009's assignment alternated YXYXYXYXYX, i.e. fully predictable. Here the
% order and the sides are drawn from the seeded stream that runStudy installed,
% so the result is reproducible but not inferable while listening.
fprintf('[S010] stage 4: randomise\n');
stageTimer = tic;
allAllocations = [allocations, catchAllocations];
pairCount = numel(allAllocations);
permutation = randperm(pairCount);
allAllocations = allAllocations(permutation);
masterOnY = rand(1, pairCount) < 0.5;

% Report the realised imbalance so a surprisingly lopsided draw is visible
% rather than hidden behind the word "random".
yCount = sum(masterOnY);
longestRun = longestAlternationRun(masterOnY);
metrics.randomisation = struct('pairCount', pairCount, ...
    'masterOnYCount', yCount, 'masterOnXCount', pairCount - yCount, ...
    'longestRun', longestRun, 'seedUsed', ctx.seed);
fprintf('[S010]   %d pairs; master on Y %d, on X %d; longest run %d\n', ...
    pairCount, yCount, pairCount - yCount, longestRun);
if longestRun >= 5
    failures(end + 1) = "RANDOMISATION_LONG_RUN"; %#ok<AGROW>
end
fprintf('[S010]   stage 4 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 5: export -----------------------------------------------------
fprintf('[S010] stage 5: export\n');
stageTimer = tic;
manifest = table();
mapping = table();
for index = 1:pairCount
    entry = allAllocations(index);
    first = (entry.start - 1) * fs + 1;
    last = min(entry.end * fs, frames);
    span = first:last;
    masterExcerpt = applyFades(master(span, :), fs, fadeSeconds);
    if entry.class == "catch_trial"
        % Both sides identical: this is the false-positive control.
        xAudio = masterExcerpt; yAudio = masterExcerpt;
    elseif masterOnY(index)
        xAudio = applyFades(original(span, :), fs, fadeSeconds); yAudio = masterExcerpt;
    else
        xAudio = masterExcerpt; yAudio = applyFades(original(span, :), fs, fadeSeconds);
    end
    stem = sprintf('%02d_%s_%05.1f-%05.1f', index, entry.class, entry.start, entry.end);
    xName = stem + "_X.wav";
    yName = stem + "_Y.wav";
    audiowrite(fullfile(auditionDir, char(xName)), xAudio, fs, 'BitsPerSample', 24);
    audiowrite(fullfile(auditionDir, char(yName)), yAudio, fs, 'BitsPerSample', 24);
    manifest = [manifest; table(index, entry.class, entry.start, entry.end, ...
        entry.score, string(xName), string(yName), ...
        'VariableNames', {'pair', 'class', 'start_s', 'end_s', 'evidence', 'X', 'Y'})]; %#ok<AGROW>
    if entry.class == "catch_trial"
        side = "SAME_ON_BOTH_SIDES";
    elseif masterOnY(index)
        side = "Y";
    else
        side = "X";
    end
    mapping = [mapping; table(index, entry.class, side, ...
        'VariableNames', {'pair', 'class', 'master_is'})]; %#ok<AGROW>
end

% Cross-class overlap check, run on the OUTPUT rather than assumed.
overlapPairs = countOverlaps(allAllocations);
metrics.allocation.overlapPairs = overlapPairs;
if overlapPairs > 0
    failures(end + 1) = "WINDOWS_OVERLAP"; %#ok<AGROW>
end
fprintf('[S010]   exported %d pairs, %d cross-class overlap(s)\n', pairCount, overlapPairs);
fprintf('[S010]   stage 5 done in %.1f s\n', toc(stageTimer));

%% ---- Stage 6: score sheet ------------------------------------------------
fprintf('[S010] stage 6: score sheet\n');
stageTimer = tic;
scoreSheet = fullfile(ctx.outputDir, 'blind_scoresheet.csv');
writeScoreSheet(scoreSheet, manifest);
htmlPath = fullfile(ctx.outputDir, 'blind_scoresheet.html');
writeScoreSheetHtml(htmlPath, manifest, excerptSeconds);
mappingPath = fullfile(ctx.outputDir, 'DO_NOT_OPEN_UNTIL_SCORED_mapping.csv');
writetable(mapping, mappingPath);
writetable(manifest, fullfile(ctx.outputDir, 's010_audition_manifest.csv'));
writetable(table((1:windowCount)', (0:windowCount-1)'*windowSeconds, deltaStrength, ...
    'VariableNames', {'window', 'start_s', 'max_abs_band_delta_db'}), ...
    fullfile(ctx.outputDir, 's010_processing_delta.csv'));
fprintf('[S010]   score sheet : %s\n', scoreSheet);
fprintf('[S010]   html sheet  : %s\n', htmlPath);
fprintf('[S010]   SEALED      : %s\n', mappingPath);
fprintf('[S010]   stage 6 done in %.1f s\n', toc(stageTimer));

%% ---- Figures -------------------------------------------------------------
fprintf('[S010] figures\n');
stageTimer = tic;
fig = figure('Visible', figureVisibility(ctx));
tiledlayout(fig, 2, 2, 'TileSpacing', 'compact');
nexttile;
plot(1:seconds, correlation, 'LineWidth', 1.0);
ylim([-0.3, 1.05]); grid on;
xlabel('Time (s)'); ylabel('L/R correlation');
title('Stereo correlation (descriptive)');
nexttile;
plot(1:seconds, rmsOriginal, 'LineWidth', 1.0); hold on;
plot(1:seconds, rmsMaster, 'LineWidth', 1.0);
yline(activityThreshold, 'k--', 'LineWidth', 0.8);
grid on; xlabel('Time (s)'); ylabel('Level (dBFS)');
legend('Original', 'LALAL', sprintf('%.1f dBFS gate', activityThreshold), ...
    'Location', 'southeast');
title(sprintf('Activity gate; %d of %d s active', sum(active), seconds));
nexttile;
plot((1:windowCount)*windowSeconds - windowSeconds, deltaStrength, 'LineWidth', 1.0);
hold on;
for index = 1:pairCount
    entry = allAllocations(index);
    color = [0 0 0];
    if entry.class == "catch_trial", color = [0.49 0.18 0.56]; end
    plot([entry.start entry.end], [0 0], '-', 'Color', color, 'LineWidth', 3);
end
grid on; xlabel('Time (s)'); ylabel('Max |band delta| (dB)');
legend('Delta strength', 'Allocated windows (purple = catch trial)', ...
    'Location', 'northwest');
title('Same-render evidence and the windows actually used');
nexttile;
histogram(correlation(active), 30);
xlabel('L/R correlation (active seconds)'); ylabel('Count');
grid on; title('Correlation distribution, active seconds only');
contract = moodifylab.figureContract("S010-blind-design", ...
    Conclusion="A de-duplicated, fixed-length, randomized blind list with an activity gate, plus catch trials that measure a listener's false-positive rate.", ...
    EvidenceRole="audition-design", ...
    SourceData=["自己的神话3.wav", "自己的神话_LALAL分轨重制_48k24.wav"], ...
    Units=["seconds", "dimensionless correlation", "dBFS", "decibels"], ...
    CalibrationStatus="EXPERIMENTAL; excerpt length fixed so length cannot cue the answer", ...
    Uncertainty=sprintf("%d pairs, %d of them catch trials; longest same-side run %d. n=1 per version.", ...
        pairCount, numel(catchAllocations), longestRun), ...
    Limitations="This is listening material, not a finding. Blinding is PROCEDURAL: the mapping is a separate file on the same disk, and the seed is recorded, so it removes order bias but is not cryptographic. Do not open the mapping until every pair is scored.");
moodifylab.saveFigure(fig, ctx.outputDir, "fig21_blind_design", contract);
fprintf('[S010]   figures done in %.1f s\n', toc(stageTimer));

%% ---- Persist -------------------------------------------------------------
scalars = {
    'excerpt_seconds', excerptSeconds;
    'pairs_total', pairCount;
    'pairs_catch_trial', numel(catchAllocations);
    'activity_threshold_dbfs', activityThreshold;
    'active_seconds', sum(active);
    'fully_active_windows', numel(candidateStarts);
    'cross_class_overlaps', overlapPairs;
    'longest_same_side_run', longestRun;
    'master_on_y', yCount;
    'delta_median_db', metrics.delta.medianDb;
    'delta_p95_db', metrics.delta.p95Db;
    'delta_max_db', metrics.delta.maxDb;
    };
writetable(cell2table(scalars, 'VariableNames', {'metric', 'value'}), ...
    fullfile(ctx.outputDir, 's010_summary.csv'));

result = struct();
result.status = "COMPLETE";
result.studyId = "S010";
result.failures = failures;
result.metrics = metrics;
result.authority = "EXPERIMENTAL";
result.answerBoundary = [ ...
    "Builds the listening list and the score sheet. It does not judge what " ...
    "is audible, and it applies no processing."];
result.limitations = [ ...
    "Blinding is procedural, not cryptographic: the sealed mapping is a file " ...
    "on the same disk. Do not open it before scoring every pair. n=1 per " ...
    "version; catch trials exist precisely because a listener's false-positive " ...
    "rate is otherwise unknown."];
fprintf('[S010] complete. failures: %s\n', strjoin(cellstr(failures), ', '));
if isempty(failures)
    fprintf('[S010] failures: none\n');
end
end

% =========================================================================
% Local helpers
% =========================================================================

% -------------------------------------------------------------------------
function values = meanCorrelationPerWindow(correlation, starts, lengthSeconds)
values = zeros(numel(starts), 1);
for index = 1:numel(starts)
    span = starts(index):(starts(index) + lengthSeconds - 1);
    span = span(span <= numel(correlation) & span >= 1);
    values(index) = mean(correlation(span), 'omitnan');
end
end

% -------------------------------------------------------------------------
function values = meanValuePerWindow(series, starts, lengthSeconds)
values = zeros(numel(starts), 1);
for index = 1:numel(starts)
    span = starts(index):(starts(index) + lengthSeconds - 1);
    span = span(span <= numel(series) & span >= 1);
    values(index) = mean(series(span), 'omitnan');
end
end

% -------------------------------------------------------------------------
function overlaps = countOverlaps(allocations)
% Verified on the produced list rather than assumed from the allocation loop.
overlaps = 0;
for first = 1:numel(allocations)
    for second = first + 1:numel(allocations)
        a = allocations(first);
        b = allocations(second);
        if a.start <= b.end && b.start <= a.end
            overlaps = overlaps + 1;
        end
    end
end
end

% -------------------------------------------------------------------------
function run = longestAlternationRun(flags)
% Longest run of identical values. A long run means a listener could guess.
run = 0;
current = 0;
for index = 1:numel(flags)
    if index > 1 && flags(index) == flags(index - 1)
        current = current + 1;
    else
        current = 1;
    end
    run = max(run, current);
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
function writeScoreSheet(path, manifest)
fileId = fopen(path, 'w', 'n', 'UTF-8');
if fileId < 0
    error('MoodifyLab:S010:SheetWrite', 'Cannot open %s', path);
end
cleanup = onCleanup(@() fclose(fileId));
fprintf(fileId, 'pair,file_X,file_Y,difference_heard_yes_no,preference_X_Y_none,confidence_1_to_5,notes\n');
for index = 1:height(manifest)
    fprintf(fileId, '%d,%s,%s,,,, \n', manifest.pair(index), ...
        manifest.X(index), manifest.Y(index));
end
clear cleanup;
end

% -------------------------------------------------------------------------
function writeScoreSheetHtml(path, manifest, excerptSeconds)
% Self-contained page: radio buttons per pair, and a button that produces the
% same CSV rows as blind_scoresheet.csv so the result can be pasted straight
% back into the analysis.
fileId = fopen(path, 'w', 'n', 'UTF-8');
if fileId < 0
    error('MoodifyLab:S010:SheetWrite', 'Cannot open %s', path);
end
cleanup = onCleanup(@() fclose(fileId));
fprintf(fileId, '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n');
fprintf(fileId, '<title>Blind listening score sheet</title>\n<style>\n');
fprintf(fileId, 'body{font-family:Arial,sans-serif;font-size:14px;margin:24px;max-width:900px}\n');
fprintf(fileId, 'table{border-collapse:collapse;width:100%%}\n');
fprintf(fileId, 'th,td{border:1px solid #ccc;padding:6px 8px;text-align:left}\n');
fprintf(fileId, 'th{background:#4a5568;color:#fff}\n');
fprintf(fileId, 'tr:nth-child(even){background:#f7f7f7}\n');
fprintf(fileId, 'audio{height:28px;vertical-align:middle}\n');
fprintf(fileId, '.out{width:100%%;height:180px;font-family:monospace;margin-top:12px}\n');
fprintf(fileId, '.note{background:#fffbea;border-left:4px solid #e0a800;padding:8px 12px;margin:12px 0}\n');
fprintf(fileId, 'button{padding:8px 14px;font-size:14px;margin-top:8px}\n');
fprintf(fileId, '</style>\n</head>\n<body>\n');
fprintf(fileId, '<h1>Blind listening score sheet</h1>\n');
fprintf(fileId, '<div class="note"><b>Each excerpt is %d s.</b> X and Y are the same passage; ' , excerptSeconds);
fprintf(fileId, 'one of them may be the LALAL master. Listen first, then answer. ');
fprintf(fileId, 'Some pairs are identical on both sides &mdash; that is deliberate and is how a false-positive rate is measured. ');
fprintf(fileId, 'Do <b>not</b> open <code>DO_NOT_OPEN_UNTIL_SCORED_mapping.csv</code> until every pair is scored.</div>\n');
fprintf(fileId, '<table id="t">\n<thead><tr><th>#</th><th>X</th><th>Y</th>');
fprintf(fileId, '<th>Heard a difference?</th><th>Prefer</th><th>Confidence</th></tr></thead>\n<tbody>\n');
for index = 1:height(manifest)
    pair = manifest.pair(index);
    fprintf(fileId, '<tr><td>%d</td>\n', pair);
    fprintf(fileId, '<td><audio controls preload="none" src="audition/%s"></audio></td>\n', manifest.X(index));
    fprintf(fileId, '<td><audio controls preload="none" src="audition/%s"></audio></td>\n', manifest.Y(index));
    fprintf(fileId, '<td><label><input type="radio" name="d%d" value="yes"> yes</label> ', pair);
    fprintf(fileId, '<label><input type="radio" name="d%d" value="no"> no</label></td>\n', pair);
    fprintf(fileId, '<td><label><input type="radio" name="p%d" value="X"> X</label> ', pair);
    fprintf(fileId, '<label><input type="radio" name="p%d" value="Y"> Y</label> ', pair);
    fprintf(fileId, '<label><input type="radio" name="p%d" value="none"> none</label></td>\n', pair);
    fprintf(fileId, '<td><select name="c%d"><option value=""></option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select></td></tr>\n', pair);
end
fprintf(fileId, '</tbody></table>\n');
fprintf(fileId, '<button onclick="emit()">Produce CSV rows</button>\n');
fprintf(fileId, '<textarea class="out" id="out" placeholder="Press the button, then copy this into blind_scoresheet.csv"></textarea>\n');
fprintf(fileId, '<script>\nfunction v(n){var e=document.querySelector(''input[name="''+n+''"]:checked'');return e?e.value:'''';}\n');
fprintf(fileId, 'function emit(){var L=[''pair,difference_heard_yes_no,preference_X_Y_none,confidence_1_to_5''];\n');
fprintf(fileId, 'for(var i=1;i<=%d;i++){var c=document.querySelector(''select[name="c''+i+''"]'');');
fprintf(fileId, 'L.push(i+'',''+v(''d''+i)+'',''+v(''p''+i)+'',''+(c?c.value:''''));}\n', height(manifest));
fprintf(fileId, 'document.getElementById(''out'').value=L.join(''\\n'');}\n</script>\n</body>\n</html>\n');
clear cleanup;
end

% -------------------------------------------------------------------------
function state = figureVisibility(ctx)
if isfield(ctx, 'figureVisible') && ctx.figureVisible
    state = 'on';
else
    state = 'off';
end
end
