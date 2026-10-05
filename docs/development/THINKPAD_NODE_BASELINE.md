# ThinkPad Node Baseline — Moodify Heavy Development Lane

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001
**Machine role:** ThinkPad Heavy Development Node（compute factory）
**Branch:** `feat/thinkpad-heavy-lane-001`
**Date:** 2026-10-05
**Status:** AUDITED — 本文件记录实测事实，未测量的项如实标注。

---

## 1. Machine

| Item | Value |
|---|---|
| Manufacturer | LENOVO |
| Model | 21SJ |
| OS | Windows 11 Home China（家庭中文版），10.0.26200，64-bit |
| Machine role | Heavy lane: Core / DSP / PROCESS / benchmark / long tests |

## 2. CPU

```text
Intel(R) Core(TM) Ultra 5 135H  (Meteor Lake-H)
physical cores:  14
logical cores:   18
base clock:      1700 MHz (MaxClockSpeed reported by WMI)
```

## 3. Memory

```text
Total (visible): 15.49 GiB       (16 GB module)
Module:          ChangXin CXMR4E816S6AS-CN1C, LPDDR5-5600, 16 GiB
Locator:         Controller0-ChannelA-DIMM0   (soldered; single channel)
Free at audit:   ~0.93 GiB  (Get-Counter '\Memory\Available MBytes' = 951 MB)
```

**Honest note:** at audit time the desktop session was heavily loaded (~1 GB available
of ~15.5 GiB). Heavy jobs and model runtimes will contend for RAM. Benchmarks must
record memory and must state the machine's concurrent load; do not assume headroom.

## 4. Storage

```text
Physical disk:  YMTC YMSS2ED08B66MC  NVMe SSD  953.9 GB
C:\  (Windows-SSD NTFS)  500.0 GB total — 390.9 GB free
D:\  (Data        NTFS)  451.5 GB total — 364.4 GB free
```

D: has the most free space; local assets, model caches and venvs belong on D:
(under ignored/machine-local paths), never in Git.

## 5. GPU / Acceleration

```text
GPU:   Intel(R) Graphics (integrated, Meteor Lake) — driver 32.0.101.8801
VRAM:  reported AdapterRAM 2 GB (shared system memory; not dedicated)
NVIDIA: NOT PRESENT (nvidia-smi not found)
CUDA:  NOT_AVAILABLE
```

**GPU_ACCELERATION = NOT_AVAILABLE.** No CUDA, no verified accelerator runtime.
All model work (Demucs included) runs in **CPU mode** on this node. No CUDA path
exists to be tested here, and none will be claimed.

## 6. Toolchain

| Tool | Version | Source |
|---|---|---|
| Python | 3.10.10 | `D:\python\python.exe`（唯一解释器；`py -0p` 只列出 3.10-64） |
| pip | 22.3.1 | global site-packages（venv 内可升级，不动全局） |
| Node.js | **NOT INSTALLED** | not on PATH; `C:\Program Files\nodejs` absent |
| Git | 2.55.0.windows.5 | |
| FFmpeg | 9.0.2-full_build-www.gyan.dev | full build, with ffprobe |
| Java | **NOT INSTALLED** | Android 属 mainline，不受影响 |

## 7. Consequences for the Heavy Lane

1. **CPU-only node.** Demucs / model benchmarks are CPU benchmarks. GPU numbers
   cannot be produced here and must not be fabricated.
2. **RAM-constrained.** ~15.5 GiB total with ~1 GB free during a loaded session.
   Long soaks and model runs must be measured with memory telemetry, and
   concurrent desktop load recorded.
3. **All heavy runtime data stays local and ignored.** venvs, model caches,
   `local_audio_assets/`, benchmark raw output live on D: or in ignored dirs.
4. **Node.js absent** → Studio (electron) JS tests cannot run on this node.
   Studio/UI remains mainline-owned (§2/§3 of the task); this lane's test surface
   is the Python Core + repo-root tests.
5. Global pip is old (22.3.1); venvs will upgrade pip locally when needed, the
   global interpreter is left untouched.

## 8. Audit commands (reproducible)

```powershell
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,TotalPhysicalMemory
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,Manufacturer,PartNumber,DeviceLocator
Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,VideoProcessor,AdapterRAM
Get-PhysicalDisk | Select-Object FriendlyName,MediaType,BusType,Size
Get-Volume | Where-Object { $_.DriveLetter } | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
(Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
```

```text
python --version          → Python 3.10.10
py -0p                    → only 3.10-64 (D:\python\python.exe)
node --version            → command not found
git --version             → 2.55.0.windows.5
ffmpeg -version           → 9.0.2-full_build-www.gyan.dev
nvidia-smi                → command not found
java -version             → command not found
```
