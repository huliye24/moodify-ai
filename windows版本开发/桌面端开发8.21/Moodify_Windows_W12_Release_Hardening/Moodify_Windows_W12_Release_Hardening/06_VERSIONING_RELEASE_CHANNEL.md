# Versioning & Release Channel

## Single Version Authority

建议只有一个主版本来源，再生成到各 package/build metadata。

至少：

```text
product_version
build_number
git_commit
build_channel
```

## Channels

```text
ALPHA
BETA
STABLE
```

W12 目标：

```text
BETA_CANDIDATE
```

## User-visible

```text
Moodify x.y.z
```

## Internal

日志/manifest：

```text
x.y.z
build N
commit abcdef
channel beta
```

## Installer Filename

推荐：

```text
Moodify-Windows-x.y.z-Beta-Setup.exe
```

具体服从 packaging tool。
