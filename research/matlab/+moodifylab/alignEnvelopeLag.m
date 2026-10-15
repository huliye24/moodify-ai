function [bestLag, curve, lags] = alignEnvelopeLag(reference, candidate, maxLag, windowSeconds, fs)
%ALIGNENVELOPELAG Bounded envelope-lag search between two signals.
%
%   [bestLag, curve, lags] = moodifylab.alignEnvelopeLag(reference, candidate, maxLag, windowSeconds, fs)
%
%   LAG CONVENTION: lag L means candidate(n) approximates reference(n - L).
%     L > 0  -> candidate is LATER than reference (trim L samples off its head)
%     L < 0  -> candidate is EARLIER than reference
%
%   Both windows are anchored at the SAME absolute start, and the candidate
%   segment for lag L is sampled at absolute offset +L from the reference
%   segment, so the correlation peak sits at the true lag by construction.
%   Do not offset the candidate window start by -maxLag and then treat the
%   returned lag as absolute: that biases every result by maxLag.
%
%   Two stages: a cheap sweep on a decimated envelope to locate the peak, then
%   a full-rate refine within +/- (decim+2) samples for sample accuracy.
%
%   curve/lags are the coarse sweep in sample units, for plotting.

decim = 64;
refEnv = localEnvelope(mean(reference, 2), round(0.010 * fs));
candEnv = localEnvelope(mean(candidate, 2), round(0.010 * fs));
nRefFull = numel(refEnv);
nCandFull = numel(candEnv);

% ---- stage 1: coarse sweep on the decimated envelope --------------------
refDecimated = refEnv(1:decim:end);
candDecimated = candEnv(1:decim:end);
maxLagDecimated = max(1, round(maxLag / decim));
windowDecimated = min(round(windowSeconds * fs / decim), ...
                      numel(refDecimated) - 2 * maxLagDecimated - 1);
if windowDecimated < 4
    error('MoodifyLab:AlignEnvelopeLag:TooShort', ...
        'Signal too short to align within +/-%d samples.', maxLag);
end
anchorDecimated = floor((numel(refDecimated) - windowDecimated) / 2) + 1;
refSegmentDecimated = refDecimated(anchorDecimated:(anchorDecimated + windowDecimated - 1));

lagsDecimated = (-maxLagDecimated:maxLagDecimated)';
curveDecimated = -Inf(numel(lagsDecimated), 1);
for index = 1:numel(lagsDecimated)
    first = anchorDecimated + lagsDecimated(index);
    last = first + windowDecimated - 1;
    if first < 1 || last > numel(candDecimated)
        continue;
    end
    curveDecimated(index) = localCorrelation(candDecimated(first:last), refSegmentDecimated);
end
[~, coarsePeak] = max(curveDecimated);
if ~isfinite(curveDecimated(coarsePeak))
    error('MoodifyLab:AlignEnvelopeLag:NoPeak', ...
        'No candidate lag inside +/-%d samples was usable.', maxLag);
end
coarseLag = lagsDecimated(coarsePeak) * decim;

% ---- stage 2: full-rate refine near the coarse peak ---------------------
refineRange = decim + 2;
anchorFull = (anchorDecimated - 1) * decim + 1;
fineWindow = min(round(5 * fs), nRefFull - anchorFull - refineRange - 1);
if fineWindow < round(fs)
    fineWindow = max(round(0.5 * fs), nRefFull - anchorFull - refineRange - 1);
end
refSegmentFine = refEnv(anchorFull:(anchorFull + fineWindow - 1));

fineLags = (coarseLag - refineRange:coarseLag + refineRange)';
fineCurve = -Inf(numel(fineLags), 1);
for index = 1:numel(fineLags)
    first = anchorFull + fineLags(index);
    last = first + fineWindow - 1;
    if first < 1 || last > nCandFull
        continue;
    end
    fineCurve(index) = localCorrelation(candEnv(first:last), refSegmentFine);
end
[~, finePeak] = max(fineCurve);
if isfinite(fineCurve(finePeak))
    bestLag = fineLags(finePeak);
else
    bestLag = coarseLag;
end

lags = lagsDecimated * decim;
curve = curveDecimated;
end

% -------------------------------------------------------------------------
function y = localEnvelope(x, halfWidth)
y = sqrt(localMovingMean(x.^2, halfWidth));
y = (y - mean(y)) / (std(y) + eps);
end

% -------------------------------------------------------------------------
function y = localMovingMean(x, halfWidth)
% movmean is O(n); conv with a kernel this wide would be O(n*k).
y = movmean(x, 2 * halfWidth + 1);
end

% -------------------------------------------------------------------------
function value = localCorrelation(a, b)
n = min(numel(a), numel(b));
a = a(1:n);
b = b(1:n);
denominator = sqrt(sum(a.^2) * sum(b.^2));
if denominator <= eps
    value = -Inf;
else
    value = sum(a .* b) / denominator;
end
end
