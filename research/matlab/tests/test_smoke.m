function test_smoke()
%TEST_SMOKE Execute every study once in a temporary output directory.

rootDir = fileparts(fileparts(mfilename('fullpath')));
addpath(rootDir);
addpath(fullfile(rootDir, 'studies'));
temporaryOutput = tempname;
cleanup = onCleanup(@() removeTree(temporaryOutput));

cfg = moodifylab.defaultConfig();
cfg.outputRoot = temporaryOutput;
cfg.campaignName = "smoke";
cfg.maxIterations = 1;
cfg.figureVisible = false;
summary = moodifylab.runCampaign(cfg);

assert(summary.iterationsCompleted == 1);
assert(summary.studyRunsCompleted == 3);
assert(all(string({summary.records.status}) == "PASS"));
assert(isfile(fullfile(temporaryOutput, 'smoke', 'campaign_status.json')));
fprintf('Moodify MATLAB smoke test: PASS\n');
clear cleanup;
removeTree(temporaryOutput);
end

function removeTree(path)
if isfolder(path)
    rmdir(path, 's');
end
end
