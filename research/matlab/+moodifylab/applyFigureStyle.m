function applyFigureStyle(figureHandle)
%APPLYFIGURESTYLE Apply Moodify's publication-oriented MATLAB visual standard.

arguments
    figureHandle (1,1) matlab.ui.Figure
end

figureHandle.Color = 'w';
figureHandle.Units = 'centimeters';
if figureHandle.Position(3) < 16
    figureHandle.Position(3:4) = [18.3, 11.5];
end
set(findall(figureHandle, '-property', 'FontName'), 'FontName', 'Arial');
set(findall(figureHandle, '-property', 'FontSize'), 'FontSize', 8);
set(findall(figureHandle, 'Type', 'axes'), ...
    'Box', 'off', 'LineWidth', 0.75, 'TickDir', 'out', ...
    'TickLength', [0.015, 0.015], 'Layer', 'top');

% A visible figure renders the axes toolbar into exportgraphics output and
% MATLAB warns: "导出的图像显示了坐标区工具栏". Hide it before exporting.
axesHandles = findall(figureHandle, 'Type', 'axes');
for index = 1:numel(axesHandles)
    try
        toolbar = axesHandles(index).Toolbar;
        if ~isempty(toolbar)
            toolbar.Visible = 'off';
        end
    catch
        % axes without a Toolbar property in this release
    end
end
set(findall(figureHandle, 'Type', 'legend'), ...
    'Box', 'off', 'FontSize', 7.5);

lines = findall(figureHandle, 'Type', 'line');
for index = 1:numel(lines)
    if lines(index).LineWidth < 1.1
        lines(index).LineWidth = 1.1;
    end
end
end
