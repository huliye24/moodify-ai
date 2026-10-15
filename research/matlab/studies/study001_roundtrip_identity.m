function result = study001_roundtrip_identity(ctx)
%STUDY001_ROUNDTRIP_IDENTITY Measure 24-bit WAV transport error.

sampleRate = 48000;
durationSeconds = 2;
t = (0:(sampleRate * durationSeconds - 1))' / sampleRate;
left = 0.45 * sin(2*pi*220*t) + 0.20 * sin(2*pi*997*t + 0.3);
right = 0.40 * sin(2*pi*330*t + 0.1) + 0.18 * sin(2*pi*1499*t);
source = [left, right];
audioPath = fullfile(ctx.outputDir, 'transport_24bit.wav');
audiowrite(audioPath, source, sampleRate, 'BitsPerSample', 24);
[decoded, decodedRate] = audioread(audioPath);

errorSignal = decoded - source;
maxAbsError = max(abs(errorSignal), [], 'all');
rmsError = sqrt(mean(errorSignal.^2, 'all'));
signalRms = sqrt(mean(source.^2, 'all'));
snrDb = 20 * log10(signalRms / max(rmsError, eps));
tolerance = 2^-22;
passed = decodedRate == sampleRate && isequal(size(decoded), size(source)) ...
    && maxAbsError <= tolerance;

metrics = table(sampleRate, durationSeconds, maxAbsError, rmsError, snrDb, ...
    tolerance, passed);
writetable(metrics, fullfile(ctx.outputDir, 'metrics.csv'));

nfft = 8192;
frequencies = (0:(nfft/2))' * sampleRate / nfft;
sourceSpectrum = abs(fft(source(:,1), nfft));
errorSpectrum = abs(fft(errorSignal(:,1), nfft));
fig = figure('Visible', visibleState(ctx.figureVisible), 'Color', 'w');
tiledlayout(2, 1);
nexttile;
plot(t(1:1000) * 1000, source(1:1000,1), 'LineWidth', 1.0);
hold on;
plot(t(1:1000) * 1000, errorSignal(1:1000,1) * 1e6, 'LineWidth', 0.8);
xlabel('Time (ms)'); ylabel('Amplitude / error x10^6');
legend('Source', 'Transport error x10^6'); grid on;
title('S001: 24-bit WAV transport');
nexttile;
semilogx(frequencies(2:end), 20*log10(sourceSpectrum(2:nfft/2+1) + eps));
hold on;
semilogx(frequencies(2:end), 20*log10(errorSpectrum(2:nfft/2+1) + eps));
xlabel('Frequency (Hz)'); ylabel('Magnitude (dB, uncalibrated)');
legend('Source', 'Error'); grid on;
contract = moodifylab.figureContract("S001-roundtrip-error", ...
    Conclusion="A 24-bit WAV write/read cycle stays within the declared numerical tolerance.", ...
    EvidenceRole="validation", SourceData="metrics.csv", ...
    Units=["seconds", "hertz", "digital full scale", "decibels"], ...
    CalibrationStatus="DIGITAL_NUMERICAL_BASELINE", ...
    Uncertainty="Deterministic quantization error; no population inference.", ...
    Limitations="Not a perceptual or stem-separation roundtrip test.");
moodifylab.saveFigure(fig, ctx.outputDir, "roundtrip_error", contract);

result = struct();
result.status = string(ternary(passed, 'PASS', 'FAIL'));
result.maxAbsError = maxAbsError;
result.rmsError = rmsError;
result.snrDb = snrDb;
result.tolerance = tolerance;
result.claim = "24-bit WAV write/read error stayed within the declared numerical tolerance.";
result.limitation = "This is a transport baseline, not perceptual validation or stem roundtrip proof.";
end

function state = visibleState(isVisible)
state = char(string(logical(isVisible)).replace("true", "on").replace("false", "off"));
end

function value = ternary(condition, whenTrue, whenFalse)
if condition, value = whenTrue; else, value = whenFalse; end
end
