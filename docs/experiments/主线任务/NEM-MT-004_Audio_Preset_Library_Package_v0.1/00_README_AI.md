# NEM-MT-004｜AI 接手说明

你是接手 Moodify MT-004 的工程执行 Agent。

## 执行原则

1. 不要重新定义整个 Moodify 项目。
2. 本节点只处理“音频处理工艺库 / preset library”相关内容。
3. 不要把一次有效参数直接标记为正式工艺。
4. 每个 preset 必须有标准 spec、版本号、适用范围、输入问题、输出目标、MRS 记录。
5. 不要为了提高 MRS 而做响度作弊。
6. 不要破坏高质量输入音频。
7. 不要提供任何用于规避平台识别、版权检测、指纹检测或隐藏来源的处理策略。
8. 只做合法的声音质量提升、声音真实度增强和工程实验沉淀。

## AI 阅读顺序

1. `00_PACKAGE_MANIFEST.json`
2. `00_NODE_STATUS.md`
3. `rules/AI_Execution_Rules.md`
4. `rules/Preset_Library_Rules.md`
5. `nem/NEM-MT-004_Audio_Preset_Library.md`
6. 当前 Gate 文件
7. 当前 AEP 文件
8. `templates/` 中对应模板

## 当前下一步

读取 `aep/AEP-MT004-001_Preset_Taxonomy.md`，建立第一版 preset 分类体系。
