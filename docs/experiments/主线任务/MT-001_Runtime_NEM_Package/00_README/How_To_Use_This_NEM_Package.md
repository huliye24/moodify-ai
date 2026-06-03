# 如何使用 MT-001 NEM 节点包

## 第一步：把压缩包解压到项目文档目录

建议路径：

```text
docs/nem/MT-001_Runtime_NEM_Package/
```

---

## 第二步：先读 NEM 总文件

```text
01_NEM_Node/NEM-MT-001_Runtime_Cloud_System.md
```

这个文件定义节点使命、边界、AEP 拆分、Gate 和完成标准。

---

## 第三步：按 AEP 顺序推进

```text
02_AEP_Atomic_Packages/
```

每个 AEP 是一个独立工程原子包。  
完成一个，就在文件里记录：

```text
状态：
证据：
问题：
下一步：
```

---

## 第四步：用 Gate 判断是否升级

```text
03_Evolution_Gates/Evolution_Gates.md
```

不要凭感觉判断节点完成，而要用 Gate 证明。

---

## 第五步：把运行结果写入报告

```text
06_Report_Templates/
```

每次 Day Run / 24h Run 都应该沉淀报告。

---

## 第六步：把证据写入 PoEW

```text
07_PoEW_Evidence/PoEW_Checklist.md
```

PoEW 是这个节点真实做功的证据，不是口头进度。
