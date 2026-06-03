# AI Execution Rules

1. 每次只执行一个 AEP。
2. 执行前读取 `00_NODE_STATUS.md`。
3. 执行前读取当前 Gate。
4. 修改规则文件前必须写入 Decision Log。
5. 不得跳过 sample_id、registry、rights_status。
6. 不得把未授权或权限不确定样本标记为可公开、可商用或可训练。
7. 不得提供规避平台识别、版权检测、指纹检测或隐藏来源的设计。
8. 只允许围绕合法的样本管理、研究测试、质量评估和数据资产沉淀进行设计。
