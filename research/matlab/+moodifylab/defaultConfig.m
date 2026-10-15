function cfg = defaultConfig()
%DEFAULTCONFIG Reproducible defaults for a local research pass.

rootDir = fileparts(fileparts(mfilename('fullpath')));
cfg = struct();
cfg.schemaVersion = "moodify-matlab-campaign/0.1";
cfg.campaignName = "local_smoke";
cfg.outputRoot = fullfile(rootDir, 'outputs');
cfg.studyIds = ["S001", "S002", "S003"];
cfg.maxIterations = 1;
cfg.maxDurationHours = 1;
cfg.pauseSeconds = 0;
cfg.seedBase = 20261007;
cfg.stopFile = fullfile(rootDir, 'STOP');
cfg.figureVisible = false;
end
