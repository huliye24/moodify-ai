function writeJson(path, value)
%WRITEJSON Atomically write pretty JSON using UTF-8.

parent = fileparts(path);
if ~isfolder(parent)
    mkdir(parent);
end
temporary = [tempname(parent), '.json'];
fileId = fopen(temporary, 'w', 'n', 'UTF-8');
assert(fileId >= 0, 'MoodifyLab:WriteFailed', 'Cannot open %s', temporary);
cleanup = onCleanup(@() fclose(fileId));
fwrite(fileId, jsonencode(value, PrettyPrint=true), 'char');
clear cleanup;
[ok, message] = movefile(temporary, path, 'f');
assert(ok, 'MoodifyLab:MoveFailed', 'Cannot publish %s: %s', path, message);
end
