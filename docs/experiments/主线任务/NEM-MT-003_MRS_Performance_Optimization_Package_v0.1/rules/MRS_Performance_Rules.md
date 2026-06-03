# MRS Performance Rules

## 性能指标

MRS 性能优化至少记录以下指标：

- audio_duration_sec
- input_file_size_mb
- wav_intermediate_size_mb
- load_time_sec
- resample_time_sec
- feature_extract_time_sec
- scoring_time_sec
- report_write_time_sec
- total_time_sec
- cache_hit
- scoring_mode
- cpu_peak_percent
- memory_peak_mb

## 模式定义

### off

不执行 MRS，仅执行音频处理主流程。

### quick_mrs

用于批量排序、快速筛选、Daily Run 快速报告。目标是低成本、低延迟、可批量。

### full_mrs

用于正式评分、实验分析、版本对比和深度报告。目标是完整性和稳定性优先。

### mrs_open_v031

当前已采纳的开放跑分基准，可作为 full_mrs 的一个实现版本。

## 生产原则

MRS 不应阻塞主流程。评分失败应记录为 scoring_failed，但音频处理任务仍可 completed。
