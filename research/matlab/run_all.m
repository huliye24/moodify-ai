function summary = run_all()
%RUN_ALL Run one deterministic pass of every registered Moodify MATLAB study.

rootDir = fileparts(mfilename('fullpath'));
addpath(rootDir);
addpath(fullfile(rootDir, 'studies'));

cfg = moodifylab.defaultConfig();
summary = moodifylab.runCampaign(cfg);
end
