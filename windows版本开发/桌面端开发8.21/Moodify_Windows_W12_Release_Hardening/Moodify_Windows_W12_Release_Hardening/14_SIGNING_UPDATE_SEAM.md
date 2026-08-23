# Code Signing & Update Seam

## Signing

若证书存在：
- sign installer
- sign executable if toolchain supports
- verify signature
- record certificate subject/thumbprint only as appropriate
- timestamp signature if supported

若不存在：

```text
SIGNING = NOT_CONFIGURED
```

必须明确 SmartScreen / trust 风险。

不得伪造签名状态。

## Update

如果已有成熟 updater：
重新审计：
- manifest authenticity
- HTTPS
- artifact hash/signature
- rollback
- interrupted download
- downgrade

如果没有：
只建立安全 seam。

禁止：

```text
download arbitrary exe
→ execute immediately
```

未来 update 至少要求：
```text
trusted manifest
+ hash/signature verification
```
