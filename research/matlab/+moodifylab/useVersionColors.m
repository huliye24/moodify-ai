function useVersionColors(versionNames)
%USEVERSIONCOLORS Pin this axes' colour order to the fixed version palette.
%
%   moodifylab.useVersionColors({'Original','LALAL','Suno'})
%
%   Call it on a fresh axes BEFORE plotting. It sets ColorOrder so that each
%   version keeps ONE colour in every figure, including two-series panels.
%
%   Why this exists: MATLAB's default ColorOrder advances per plot call, so a
%   two-line panel hands LALAL the first colour (blue) while a three-line panel
%   gives it the second (orange). The reader then has to relearn the mapping
%   figure by figure. The Moodify figure standard requires colour to encode
%   meaning consistently, so the palette is declared once, here.
%
%   Original   blue    (MATLAB ColorOrder 1)
%   LALAL      orange  (ColorOrder 2)
%   Suno       yellow  (ColorOrder 3)
%   Residual   purple  (distinct: a derived curve, not a version)

arguments
    versionNames cell
end

palette = struct( ...
    'Original', [0.0000 0.4470 0.7410], ...
    'LALAL',    [0.8500 0.3250 0.0980], ...
    'Suno',     [0.9290 0.6940 0.1250], ...
    'Residual', [0.4940 0.1840 0.5560]);

order = zeros(numel(versionNames), 3);
for index = 1:numel(versionNames)
    name = char(versionNames{index});
    if ~isfield(palette, name)
        error('MoodifyLab:UseVersionColors:Unknown', ...
            'Unknown version "%s". Known: Original, LALAL, Suno, Residual.', name);
    end
    order(index, :) = palette.(name);
end
set(gca, 'ColorOrder', order, 'ColorOrderIndex', 1);
end
