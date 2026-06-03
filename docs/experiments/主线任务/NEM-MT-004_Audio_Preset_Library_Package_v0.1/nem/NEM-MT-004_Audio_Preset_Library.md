# NEM-MT-004｜音频处理工艺库

## 1. 节点定义

MT-004 是 Moodify 的音频处理工艺库节点，目标是将 Runtime 与 MRS 产生的工程数据转化为可复用的声音处理 preset。

本节点关注的是：

```text
声音问题识别 -> 处理链设计 -> 参数实验 -> MRS 评估 -> preset 封装 -> 工艺库沉淀
```

## 2. 节点边界

### 负责

- Preset 分类体系；
- Preset 标准格式；
- Preset 注册表；
- Preset 版本规则；
- MRS 关联评估记录；
- Runtime preset 调用模板；
- 工艺库质量闸门；
- 第一批实验 preset 的沉淀规则。

### 不负责

- Runtime 基础运行能力；
- MRS 公式本身发明；
- MRS 性能优化；
- GUI 产品界面；
- 商业定价；
- 分发平台规避或指纹规避；
- 任何非法或不透明用途。

## 3. 关键判断

工艺库不是参数仓库，而是经验仓库。

每一个被保留的 preset 都必须回答：

1. 它解决什么声音问题？
2. 它适合什么输入？
3. 它不适合什么输入？
4. 它的处理链是什么？
5. 它的参数版本是什么？
6. 它让 MRS 如何变化？
7. 它是否引入副作用？
8. 它能否被 Runtime 批量复现？

## 4. Preset 生命周期

```text
IDEA -> EXPERIMENTAL -> CANDIDATE -> STABLE -> ADOPTED
                    \-> DEPRECATED
```

任何 preset 都不能跳过验证直接进入 ADOPTED。

## 5. 主要 AEP

- AEP-MT004-001｜Preset 分类体系
- AEP-MT004-002｜Preset Spec Schema
- AEP-MT004-003｜Preset Registry
- AEP-MT004-004｜实验到 preset 的沉淀流程
- AEP-MT004-005｜MRS 关联评估协议
- AEP-MT004-006｜副作用与高质量输入保护
- AEP-MT004-007｜Preset 版本管理
- AEP-MT004-008｜Runtime 调用接口
- AEP-MT004-009｜第一批实验 preset
- AEP-MT004-010｜工艺库采纳报告

## 6. 节点完成定义

当 Moodify 能够稳定地保存、复现、评估、升级一批声音处理 preset，并且这些 preset 可以通过 Runtime 批量调用、通过 MRS 记录真实度变化时，本节点才算完成。
