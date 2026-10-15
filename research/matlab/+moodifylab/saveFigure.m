function manifest = saveFigure(figureHandle, outputDir, baseName, contract)
%SAVEFIGURE Export publication, review, and editable versions with provenance.

arguments
    figureHandle (1,1) matlab.ui.Figure
    outputDir
    baseName (1,1) string
    contract (1,1) struct = moodifylab.figureContract(baseName)
end

if ~isfolder(outputDir)
    mkdir(outputDir);
end
moodifylab.applyFigureStyle(figureHandle);
drawnow;

pngPath = fullfile(outputDir, baseName + ".png");
pdfPath = fullfile(outputDir, baseName + ".pdf");
svgPath = fullfile(outputDir, baseName + ".svg");
figPath = fullfile(outputDir, baseName + ".fig");
exportgraphics(figureHandle, pngPath, 'Resolution', 600, ...
    'BackgroundColor', 'white');
exportgraphics(figureHandle, pdfPath, 'ContentType', 'vector', ...
    'BackgroundColor', 'white');
% R2023b exportgraphics does not support SVG on every installation. The
% MATLAB SVG print device remains vector and preserves MATLAB as the sole
% rendering backend.
print(figureHandle, svgPath, '-dsvg');
savefig(figureHandle, figPath);

manifest = struct();
manifest.schemaVersion = "moodify-matlab-figure/0.1";
manifest.createdAtUtc = string(datetime('now', 'TimeZone', 'UTC'), ...
    'yyyy-MM-dd''T''HH:mm:ss.SSSXXX');
manifest.matlabRuntime = version;
manifest.contract = contract;
manifest.exports = struct('png600dpi', pngPath, 'pdfVector', pdfPath, ...
    'svgVector', svgPath, 'matlabEditable', figPath);
manifest.credibilityBoundary = [ ...
    "MATLAB is the rendering and analysis runtime; credibility depends on " ...
    "source data, method, calibration, uncertainty, and reproducibility."];
moodifylab.writeJson(fullfile(outputDir, baseName + "_figure.json"), manifest);
close(figureHandle);
end
