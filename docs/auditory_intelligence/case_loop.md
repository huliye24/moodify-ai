# 案例循环（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）

## 概念流程

```text
1. 注册源
2. 运行 before 扫描
3. 记录听觉观察
4. 建立处理假设与计划
5. 产生一个或多个候选
6. 注册干预记录
7. 运行 after 扫描
8. 比较前后
9. 运行技术判断
10. 进行人耳听音评估
11. 记录接受与拒绝候选
12. 建立学习记录
13. 审查权利与数据集资格
14. 提交或排除学习记录
```

## 支持的案例形态

- 一个源、多个候选；
- 接受与拒绝候选并存；
- 中性结果；
- 失败干预；
- 过度处理标签；
- 技术通过但艺术拒绝；
- 技术拒绝；
- 未决不确定性。

## 学习状态（与生命周期正交）

NOT_STARTED → CAPTURE_PENDING → CAPTURED → REVIEW_PENDING →
COMMITTED / EXCLUDED / INVALID

生产案例可以 COMPLETED 而学习状态 EXCLUDED，但排除原因必须显式。
生产案例绝不能悄悄出现在训练导出中。

## CLI

```bash
python -m moodify case observations add <proj> <case> --file observation.json
python -m moodify case intervention register <proj> <case> --candidate-id K --file intervention.json
python -m moodify case listening evaluate <proj> <case> --file evaluation.json
python -m moodify case learning build <proj> <case>
python -m moodify case learning review <proj> <case> --rights rights.json --eligibility PENDING_REVIEW
python -m moodify case learning commit <proj> <case> --by reviewer
python -m moodify learning dataset export --dataset-id D --project-dir P --output ./exports/D
```
