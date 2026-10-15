function [lufs, detail] = loudnessBs1770(audio, sampleRate, varargin)
%LOUDNESSBS1770 ITU-R BS.1770-4 integrated loudness without Audio Toolbox.
%
%   [lufs, detail] = moodifylab.loudnessBs1770(audio, sampleRate)
%
%   This installation has no Audio Toolbox, so `integratedLoudness` is not
%   available. This function implements the K-weighting filter, the 400 ms
%   gating blocks, and the two-stage absolute/relative gate directly.
%
%   CHANNEL POWERS ARE SUMMED, NEVER AVERAGED. Summing is what BS.1770-4
%   specifies (G_i = 1.0 per channel). Averaging across channels under-reports
%   stereo loudness by 10*log10(2) = 3.01 dB relative to mono. Callers should
%   assert mono/stereo agreement on identical content; see the regression test
%   in study004.
%
%   audio         n-by-channels double, nominal full scale = 1.0
%   sampleRate    Hz
%   returns       lufs   integrated loudness, LUFS (LKFS)
%                 detail per-block loudness, gate thresholds, block count

% Deliberately NO `arguments` block here. MATLAB rejects a bare `varargin`
% declaration inside one: "varargin can only be used within a repeating
% argument block". Validating by hand keeps the name/value options and
% sidesteps that restriction.
if ~isnumeric(audio) || ~isreal(audio)
    error('MoodifyLab:loudnessBs1770:BadAudio', ...
        'audio must be real numeric.');
end
audio = double(audio);
if ~isnumeric(sampleRate) || ~isscalar(sampleRate) ...
        || ~isfinite(sampleRate) || sampleRate <= 0
    error('MoodifyLab:loudnessBs1770:BadRate', ...
        'sampleRate must be a positive finite scalar.');
end

blockSeconds = 0.400;   % BS.1770-4 gating block
hopSeconds   = 0.100;   % 75 percent overlap
absoluteGate = -70.0;   % LUFS, absolute gate
relativeGate = -10.0;   % LU, relative gate below the ungated mean

if mod(numel(varargin), 2) ~= 0
    error('MoodifyLab:loudnessBs1770:BadOptions', ...
        'Options must be name/value pairs.');
end
for k = 1:2:numel(varargin)
    switch lower(string(varargin{k}))
        case "blockseconds", blockSeconds = varargin{k+1};
        case "hopseconds",   hopSeconds   = varargin{k+1};
        case "absolutegate", absoluteGate = varargin{k+1};
        case "relativegate", relativeGate = varargin{k+1};
        otherwise
            error('MoodifyLab:loudnessBs1770:UnknownOption', ...
                'Unknown option: %s', string(varargin{k}));
    end
end

if size(audio, 1) < size(audio, 2)
    audio = audio.';   % require samples along dim 1
end

% ---- K-weighting: stage 1 high shelf, then stage 2 RLB high pass ---------
[b1, a1] = shelfStage(sampleRate);
[b2, a2] = highPassStage(sampleRate);

weighted = filter(b1, a1, audio);
weighted = filter(b2, a2, weighted);

% ---- Gating blocks -------------------------------------------------------
blockLength = round(blockSeconds * sampleRate);
hopLength   = round(hopSeconds * sampleRate);
sampleCount = size(weighted, 1);

if sampleCount < blockLength
    lufs = NaN;
    detail = struct('blockLoudness', [], 'relativeThreshold', NaN, ...
        'blockCount', 0, 'gatedBlockCount', 0, ...
        'insufficientData', true);
    return;
end

starts = 1:hopLength:(sampleCount - blockLength + 1);
blockCount = numel(starts);
channelCount = size(weighted, 2);

% Mean square per channel per block (z_ij)
z = zeros(blockCount, channelCount);
for index = 1:blockCount
    segment = weighted(starts(index):(starts(index) + blockLength - 1), :);
    z(index, :) = mean(segment.^2, 1);
end

% Channel powers are SUMMED (G_i = 1.0). Do not replace with mean().
channelPower = sum(z, 2);
blockLoudness = -0.691 + 10 * log10(max(channelPower, eps));

% ---- Absolute gate -------------------------------------------------------
keepAbsolute = blockLoudness > absoluteGate;
if ~any(keepAbsolute)
    lufs = -Inf;
    detail = struct('blockLoudness', blockLoudness, ...
        'relativeThreshold', NaN, 'blockCount', blockCount, ...
        'gatedBlockCount', 0, 'insufficientData', false);
    return;
end

% ---- Relative gate -------------------------------------------------------
meanAboveAbsolute = -0.691 + 10 * log10( ...
    mean(channelPower(keepAbsolute)));
relativeThreshold = meanAboveAbsolute + relativeGate;

keepFinal = keepAbsolute & (blockLoudness > relativeThreshold);
if ~any(keepFinal)
    keepFinal = keepAbsolute;
end

lufs = -0.691 + 10 * log10(mean(channelPower(keepFinal)));

detail = struct();
detail.blockLoudness = blockLoudness;
detail.blockStarts = starts;
detail.blockCount = blockCount;
detail.gatedBlockCount = sum(keepFinal);
detail.relativeThreshold = relativeThreshold;
detail.absoluteThreshold = absoluteGate;
detail.insufficientData = false;
end

% -------------------------------------------------------------------------
function [b, a] = shelfStage(sampleRate)
% Stage 1: high-shelf pre-filter, BS.1770-4 Table 1.
f0 = 1681.974450955533;
G  = 3.999843853973347;
Q  = 0.7071752369554196;

K  = tan(pi * f0 / sampleRate);
Vh = 10^(G / 20);
Vb = Vh^0.4996667741545416;

a0 = 1 + K / Q + K^2;
b = [(Vh + Vb * K / Q + K^2), 2 * (K^2 - Vh), (Vh - Vb * K / Q + K^2)] / a0;
a = [1, 2 * (K^2 - 1) / a0, (1 - K / Q + K^2) / a0];
end

% -------------------------------------------------------------------------
function [b, a] = highPassStage(sampleRate)
% Stage 2: RLB high-pass, BS.1770-4 Table 1.
f0 = 38.13547087602444;
Q  = 0.5003270373238773;

K = tan(pi * f0 / sampleRate);
b = [1, -2, 1];
a = [1, ...
     2 * (K^2 - 1) / (1 + K / Q + K^2), ...
     (1 - K / Q + K^2) / (1 + K / Q + K^2)];
end
