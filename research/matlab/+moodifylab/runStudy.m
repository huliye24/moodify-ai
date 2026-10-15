function result = runStudy(studyId, ctx)
%RUNSTUDY Dispatch one registered study and persist a result envelope.

arguments
    studyId (1,1) string
    ctx (1,1) struct
end

if ~isfolder(ctx.outputDir)
    mkdir(ctx.outputDir);
end
% Use an explicit stream instead of rng(seed, generator). Some managed
% R2023b installations expose a reduced rng wrapper, while RandStream is
% stable and also makes the selected generator unambiguous in evidence.
stream = RandStream('mt19937ar', 'Seed', ctx.seed);
RandStream.setGlobalStream(stream);

switch upper(studyId)
    case "S001"
        studyFunction = @study001_roundtrip_identity;
    case "S002"
        studyFunction = @study002_wavefield_nonuniqueness;
    case "S003"
        studyFunction = @study003_judge_threshold_sensitivity;
    case "S004"
        studyFunction = @study004_ownmyth_three_way_comparison;
    case "S005"
        studyFunction = @study005_lalal_vs_suno;
    case "S006"
        studyFunction = @study006_lalal_preprocessing_diagnostic;
    otherwise
        error('MoodifyLab:UnknownStudy', 'Unknown study ID: %s', studyId);
end

started = datetime('now', 'TimeZone', 'UTC');
try
    result = studyFunction(ctx);
catch exception
    result = struct();
    result.status = "FAIL";
    result.errorIdentifier = string(exception.identifier);
    result.errorMessage = string(exception.message);
end
result.studyId = upper(studyId);
result.seed = ctx.seed;
result.startedAtUtc = string(started, 'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
result.completedAtUtc = string(datetime('now', 'TimeZone', 'UTC'), ...
    'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
result.runtime = version;
result.authority = "EXPERIMENTAL";
moodifylab.writeJson(fullfile(ctx.outputDir, 'result.json'), result);
save(fullfile(ctx.outputDir, 'workspace.mat'), 'result', 'ctx');
end
