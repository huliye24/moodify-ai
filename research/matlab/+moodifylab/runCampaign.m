function summary = runCampaign(cfg)
%RUNCAMPAIGN Run registered studies repeatedly with checkpoints and stop control.

arguments
    cfg (1,1) struct
end

required = ["campaignName", "outputRoot", "studyIds", "maxIterations", ...
    "maxDurationHours", "pauseSeconds", "seedBase", "stopFile", "figureVisible"];
for name = required
    assert(isfield(cfg, name), 'MoodifyLab:MissingConfig', ...
        'Missing campaign configuration field: %s', name);
end
assert(cfg.maxIterations > 0, 'maxIterations must be positive.');
assert(cfg.maxDurationHours > 0, 'maxDurationHours must be positive.');
assert(cfg.pauseSeconds >= 0, 'pauseSeconds must be nonnegative.');

rootDir = fileparts(fileparts(mfilename('fullpath')));
addpath(rootDir);
addpath(fullfile(rootDir, 'studies'));

campaignDir = fullfile(cfg.outputRoot, char(cfg.campaignName));
if ~isfolder(campaignDir)
    mkdir(campaignDir);
end

started = datetime('now', 'TimeZone', 'UTC');
iteration = 0;
records = struct('iteration', {}, 'studyId', {}, 'status', {}, ...
    'resultFile', {}, 'completedAtUtc', {});
stopReason = "MAX_ITERATIONS";

while iteration < cfg.maxIterations
    if hours(datetime('now', 'TimeZone', 'UTC') - started) >= cfg.maxDurationHours
        stopReason = "MAX_DURATION";
        break;
    end
    if isfile(cfg.stopFile)
        stopReason = "STOP_FILE";
        break;
    end

    iteration = iteration + 1;
    iterationDir = fullfile(campaignDir, sprintf('iteration_%06d', iteration));
    for studyId = string(cfg.studyIds)
        if isfile(cfg.stopFile)
            stopReason = "STOP_FILE";
            break;
        end
        ctx = struct();
        ctx.iteration = iteration;
        ctx.seed = cfg.seedBase + iteration - 1;
        ctx.figureVisible = logical(cfg.figureVisible);
        ctx.outputDir = fullfile(iterationDir, char(studyId));
        result = moodifylab.runStudy(studyId, ctx);

        record = struct();
        record.iteration = iteration;
        record.studyId = studyId;
        record.status = string(result.status);
        record.resultFile = fullfile(ctx.outputDir, 'result.json');
        record.completedAtUtc = string(datetime('now', 'TimeZone', 'UTC'), ...
            'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
        records(end + 1) = record; %#ok<AGROW>

        checkpoint = buildSummary(cfg, started, iteration, records, "RUNNING");
        moodifylab.writeJson(fullfile(campaignDir, 'campaign_status.json'), checkpoint);
    end
    if stopReason == "STOP_FILE"
        break;
    end
    if iteration < cfg.maxIterations && cfg.pauseSeconds > 0
        pause(cfg.pauseSeconds);
    end
end

summary = buildSummary(cfg, started, iteration, records, stopReason);
moodifylab.writeJson(fullfile(campaignDir, 'campaign_status.json'), summary);
save(fullfile(campaignDir, 'campaign_summary.mat'), 'summary', 'cfg');
fprintf('Moodify MATLAB campaign %s stopped: %s (%d iterations, %d studies).\n', ...
    cfg.campaignName, stopReason, iteration, numel(records));
end

function summary = buildSummary(cfg, started, iteration, records, state)
summary = struct();
summary.schemaVersion = cfg.schemaVersion;
summary.campaignName = cfg.campaignName;
summary.startedAtUtc = string(started, 'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
summary.updatedAtUtc = string(datetime('now', 'TimeZone', 'UTC'), ...
    'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
summary.iterationsCompleted = iteration;
summary.studyRunsCompleted = numel(records);
summary.state = state;
summary.records = records;
summary.boundary = "EXPERIMENTAL_NOT_PRODUCTION_TRUTH";
end
