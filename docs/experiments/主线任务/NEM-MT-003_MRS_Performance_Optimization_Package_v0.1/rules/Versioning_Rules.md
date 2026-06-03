# Versioning Rules｜MT-003

## 节点版本

- v0.1：节点容器创建，待执行性能基线。
- v0.2：完成 profiling baseline。
- v0.3：完成 quick/full 模式设计。
- v0.4：完成缓存与并行验证。
- v0.5：完成批量生产测试。
- v1.0：进入 ADOPT。

## 配置版本

所有影响评分结果或耗时的配置都必须记录版本号。

## 缓存版本

特征缓存必须绑定：

- MRS formula version
- feature extractor version
- sample hash
- config hash
