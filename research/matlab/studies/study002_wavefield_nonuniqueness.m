function result = study002_wavefield_nonuniqueness(ctx)
%STUDY002_WAVEFIELD_NONUNIQUENESS Construct two fields identical at two sensors.

soundSpeed = 343;
frequency = 1000;
waveNumber = 2*pi*frequency/soundSpeed;
sources = [-1.0, 1.5; 0.8, 1.2; 0.1, -1.0];
sensors = [-0.09, 0; 0.09, 0];
probe = [0.75, 0.35];
H = transferMatrix(sensors, sources, waveNumber);
hProbe = transferMatrix(probe, sources, waveNumber);

weightsA = [1.0; 0.7 * exp(1i*0.4); 0.5 * exp(-1i*0.8)];
nullDirection = null(H);
assert(~isempty(nullDirection), 'Expected an underdetermined two-sensor system.');
weightsB = weightsA + 1.3 * nullDirection(:,1);
sensorA = H * weightsA;
sensorB = H * weightsB;
probeA = hProbe * weightsA;
probeB = hProbe * weightsB;
sensorRelativeError = norm(sensorB-sensorA) / max(norm(sensorA), eps);
probeRelativeDifference = abs(probeB-probeA) / max(abs(probeA), eps);
passed = sensorRelativeError < 1e-10 && probeRelativeDifference > 1e-3;

measurementData = table((1:2)', real(sensorA), imag(sensorA), ...
    real(sensorB), imag(sensorB), abs(sensorB-sensorA), ...
    'VariableNames', {'sensor','fieldAReal','fieldAImag','fieldBReal', ...
    'fieldBImag','absoluteDifference'});
writetable(measurementData, fullfile(ctx.outputDir, 'sensor_measurements.csv'));
probeData = table(real(probeA), imag(probeA), real(probeB), imag(probeB), ...
    abs(probeB-probeA), probeRelativeDifference, ...
    'VariableNames', {'fieldAReal','fieldAImag','fieldBReal','fieldBImag', ...
    'absoluteDifference','relativeDifference'});
writetable(probeData, fullfile(ctx.outputDir, 'probe_measurement.csv'));

[gridX, gridY] = meshgrid(linspace(-1.5,1.5,121), linspace(-1.5,2.0,141));
points = [gridX(:), gridY(:)];
fieldA = transferMatrix(points, sources, waveNumber) * weightsA;
fieldB = transferMatrix(points, sources, waveNumber) * weightsB;
fieldDifference = reshape(abs(fieldB-fieldA), size(gridX));
fig = figure('Visible', visibleState(ctx.figureVisible), 'Color', 'w');
tiledlayout(1, 2);
nexttile;
bar([abs(sensorA), abs(sensorB)]);
xlabel('Sensor'); ylabel('|Pressure proxy|');
legend('Field A', 'Field B'); grid on;
title('Same observations at two sensors');
nexttile;
imagesc(gridX(1,:), gridY(:,1), fieldDifference);
set(gca, 'YDir', 'normal'); axis equal tight; colorbar;
hold on; plot(sensors(:,1), sensors(:,2), 'wo', 'MarkerFaceColor', 'k');
plot(probe(1), probe(2), 'wp', 'MarkerFaceColor', 'y', 'MarkerSize', 10);
xlabel('x (m)'); ylabel('y (m)');
title('|Field B - Field A| away from sensors');
contract = moodifylab.figureContract("S002-wavefield-nonuniqueness", ...
    Conclusion="Two-channel equality does not uniquely identify the surrounding simulated field.", ...
    EvidenceRole="constructive counterexample", ...
    SourceData=["sensor_measurements.csv", "probe_measurement.csv"], ...
    Units=["metres", "1000 Hz complex pressure proxy"], ...
    CalibrationStatus="SIMULATION_ONLY", ...
    Uncertainty="Numerical null-space residual reported in result.json.", ...
    Limitations="Idealized 2D free-field proxy, not calibrated room evidence.");
moodifylab.saveFigure(fig, ctx.outputDir, "wavefield_nonuniqueness", contract);

result = struct();
result.status = string(ternary(passed, 'PASS', 'FAIL'));
result.sensorRelativeError = sensorRelativeError;
result.probeRelativeDifference = probeRelativeDifference;
result.frequencyHz = frequency;
result.claim = "Two distinct simulated source states match two-channel observations while differing elsewhere.";
result.limitation = "Idealized 2D free-field proxy at one frequency; not a calibrated real-room measurement.";
end

function H = transferMatrix(receivers, sources, waveNumber)
dx = receivers(:,1) - sources(:,1)';
dy = receivers(:,2) - sources(:,2)';
distance = max(sqrt(dx.^2 + dy.^2), 1e-6);
H = exp(-1i * waveNumber * distance) ./ (4*pi*distance);
end

function state = visibleState(isVisible)
if isVisible, state = 'on'; else, state = 'off'; end
end

function value = ternary(condition, whenTrue, whenFalse)
if condition, value = whenTrue; else, value = whenFalse; end
end
