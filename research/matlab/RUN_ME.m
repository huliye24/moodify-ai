%% RUN_ME.m - 自己的神话 三版对比 (S004: 原曲 / LALAL / Suno)
%
%   在 MATLAB GUI 里打开本文件，按 F5 运行。
%
%   为什么是 RUN_ME 而不是 -batch：
%     MATLAB 冷启动 40-60 s，且 -batch 模式下 stdout 是块缓冲的。
%     如果在跑完前杀掉进程，日志会是空的，等于白跑。所以这里用 diary
%     把全部输出落盘到 run_log.txt，并逐阶段计时，便于中途观察进度。
%
%   产出（全部落在 projectOutDir）：
%     run_log.txt                       本次完整输出
%     metrics.csv                       三版逐项测量
%     result.json                       结构化结果 + 失败项
%     fig01..fig06 的 .png/.pdf/.svg/.fig  六组图，各 600 dpi PNG
%     fig0N_*_figure.json               每图的科学契约（结论/单位/不确定性/局限）
%
%   注意：本机没有 Audio Toolbox，所以 LUFS 由 moodifylab.loudnessBs1770
%   按 ITU-R BS.1770-4 自行实现。它会把各声道功率【求和】而非取平均 ——
%   取平均会让立体声比单声道低 3.01 dB。脚本开头有一项回归测试会断言这点。

clear; clc; close all;

studyId = "S004";
projectOutDir = "E:\荣景文川 文化集团 2026\逍遥仙\挑选\三版对比_MATLAB_20261011";

% ---------------------------------------------------------------- 环境准备
runStart = tic;
if ~isfolder(projectOutDir)
    mkdir(projectOutDir);
end
logPath = fullfile(projectOutDir, 'run_log.txt');
if isfile(logPath)
    delete(logPath);
end
diary(logPath);
diary on;

fprintf('=================================================\n');
fprintf('RUN_ME  study %s\n', studyId);
fprintf('MATLAB  %s\n', version);
fprintf('host    %s\n', computer);
fprintf('start   %s\n', datestr(now, 'yyyy-mm-dd HH:MM:SS'));
fprintf('output  %s\n', projectOutDir);
fprintf('=================================================\n\n');

% ------------------------------------------------------------- 路径自检
matlabRoot = fileparts(mfilename('fullpath'));
addpath(matlabRoot);
addpath(fullfile(matlabRoot, 'studies'));
fprintf('matlab root  %s\n', matlabRoot);
fprintf('moodifylab   %s\n\n', which('moodifylab.saveFigure'));

if isempty(which('moodifylab.saveFigure'))
    error('RUN_ME:PathMissing', ...
        'moodifylab package not on path. Open MATLAB in %s', matlabRoot);
end

% ------------------------------------------------------------------- ctx
ctx = struct();
ctx.outputDir = char(projectOutDir);
ctx.seed = 20261011;
ctx.figureVisible = true;   % 设为 false 可无窗口跑（用于复跑）
ctx.studyId = studyId;

% ------------------------------------------------------------- 分阶段执行
% 每个阶段单独计时并落盘，这样中途失败也能定位到阶段。
stageResults = struct();
stageNames = ["S004"];
overallStatus = "COMPLETE";

for index = 1:numel(stageNames)
    name = stageNames(index);
    fprintf('\n---- stage %s @ %s ----\n', name, datestr(now, 'HH:MM:SS'));
    stageTimer = tic;
    try
        stageResults.(char(name)) = moodifylab.runStudy(name, ctx);
        fprintf('---- stage %s OK in %.1f s ----\n', name, toc(stageTimer));
    catch exception
        overallStatus = "FAILED_AT_" + name;
        fprintf(2, '---- stage %s FAILED in %.1f s ----\n', name, toc(stageTimer));
        fprintf(2, 'identifier: %s\n', exception.identifier);
        fprintf(2, 'message   : %s\n', exception.message);
        for frameIndex = 1:numel(exception.stack)
            fprintf(2, '   at %s line %d\n', ...
                exception.stack(frameIndex).name, exception.stack(frameIndex).line);
        end
        stageResults.(char(name)) = struct( ...
            'status', "FAIL", ...
            'errorIdentifier', string(exception.identifier), ...
            'errorMessage', string(exception.message));
        break;
    end
end

% ------------------------------------------------------------------ 收尾
totalSeconds = toc(runStart);
fprintf('\n=================================================\n');
fprintf('status   %s\n', overallStatus);
fprintf('elapsed  %.1f s (%.2f min)\n', totalSeconds, totalSeconds / 60);
fprintf('end      %s\n', datestr(now, 'yyyy-mm-dd HH:MM:SS'));

summary = struct();
summary.schemaVersion = "moodify-matlab-run/0.1";
summary.studyId = studyId;
summary.status = overallStatus;
summary.elapsedSeconds = totalSeconds;
summary.matlabVersion = version;
summary.computer = computer;
summary.outputDir = char(projectOutDir);
summary.logPath = logPath;
summary.stages = stageResults;
moodifylab.writeJson(fullfile(projectOutDir, 'run_summary.json'), summary);

fprintf('log      %s\n', logPath);
fprintf('summary  %s\n', fullfile(projectOutDir, 'run_summary.json'));
fprintf('=================================================\n');

diary off;
