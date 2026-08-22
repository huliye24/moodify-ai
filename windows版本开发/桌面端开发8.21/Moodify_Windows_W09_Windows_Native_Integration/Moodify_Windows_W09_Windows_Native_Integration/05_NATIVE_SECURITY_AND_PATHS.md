# Native Security & Path Safety

## Native IPC

只允许明确 channel + 明确 schema。

禁止：
```text
execute(command)
runShell(string)
eval(payload)
```

## File Input

所有 Open With / second-instance 文件参数：

```text
OS args/event
→ normalize
→ validate
→ W02 import
```

不直接交给 shell。

## Required Path Cases

```text
C:\Music\hello world.flac
C:\音乐\夜.mp3
C:\A&B\song.wav
C:\(Live)\song.flac
Unicode
very-long-path
multiple files
non-audio file
directory path
```

若支持 UNC/network path，要单独验证；否则安全拒绝。

## Forbidden

```text
cmd.exe /c <user path>
powershell <user path>
shell=True
manual split on spaces
```

## Logging

不记录 token / credential / private audio content。
本地绝对路径只在诊断确有必要时最小化记录。
