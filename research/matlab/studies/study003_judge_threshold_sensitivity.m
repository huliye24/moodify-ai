function result = study003_judge_threshold_sensitivity(ctx)
%STUDY003_JUDGE_THRESHOLD_SENSITIVITY Show threshold-driven decision changes.

sampleCount = 4000;
latentQuality = randn(sampleCount, 1);
measurementNoise = 0.45 * randn(sampleCount, 1);
observedScore = latentQuality + measurementNoise;
referenceLabel = latentQuality >= 0;
thresholds = (-1.5:0.02:1.5)';

accuracy = zeros(size(thresholds));
positiveRate = zeros(size(thresholds));
falsePositiveRate = zeros(size(thresholds));
falseNegativeRate = zeros(size(thresholds));
for index = 1:numel(thresholds)
    predicted = observedScore >= thresholds(index);
    accuracy(index) = mean(predicted == referenceLabel);
    positiveRate(index) = mean(predicted);
    falsePositiveRate(index) = sum(predicted & ~referenceLabel) / max(sum(~referenceLabel), 1);
    falseNegativeRate(index) = sum(~predicted & referenceLabel) / max(sum(referenceLabel), 1);
end

[bestAccuracy, bestIndex] = max(accuracy);
bestThreshold = thresholds(bestIndex);
data = table(thresholds, accuracy, positiveRate, falsePositiveRate, falseNegativeRate);
writetable(data, fullfile(ctx.outputDir, 'threshold_sweep.csv'));

fig = figure('Visible', visibleState(ctx.figureVisible), 'Color', 'w');
tiledlayout(2, 1);
nexttile;
plot(thresholds, accuracy, 'LineWidth', 1.5);
hold on; xline(bestThreshold, '--');
xlabel('Decision threshold'); ylabel('Accuracy'); grid on;
title('S003: synthetic threshold sensitivity');
nexttile;
plot(thresholds, positiveRate, 'LineWidth', 1.2);
hold on;
plot(thresholds, falsePositiveRate, 'LineWidth', 1.2);
plot(thresholds, falseNegativeRate, 'LineWidth', 1.2);
xlabel('Decision threshold'); ylabel('Rate');
legend('Positive', 'False positive', 'False negative'); grid on;
contract = moodifylab.figureContract("S003-judge-threshold-sensitivity", ...
    Conclusion="Binary decision rates are sensitive to the selected threshold.", ...
    EvidenceRole="sensitivity analysis", SourceData="threshold_sweep.csv", ...
    Units=["dimensionless synthetic score", "rate"], ...
    CalibrationStatus="UNCALIBRATED_SYNTHETIC", ...
    Uncertainty="One seeded synthetic sample; no confidence interval.", ...
    Limitations="Does not calibrate Judge-1 or authorize a production threshold.");
moodifylab.saveFigure(fig, ctx.outputDir, "judge_threshold_sensitivity", contract);

result = struct();
result.status = "PASS";
result.sampleCount = sampleCount;
result.bestSyntheticThreshold = bestThreshold;
result.bestSyntheticAccuracy = bestAccuracy;
result.decisionRateRange = max(positiveRate) - min(positiveRate);
result.claim = "Decision rates materially change across the scanned threshold range.";
result.limitation = "Synthetic demonstration only; it does not calibrate Judge-1 or authorize a production threshold.";
result.calibrationStatus = "UNCALIBRATED_SYNTHETIC";
end

function state = visibleState(isVisible)
if isVisible, state = 'on'; else, state = 'off'; end
end
