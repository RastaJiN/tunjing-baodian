# 吞鲸宝典 GitHub 同步与仓库维护

> 宝典本体在本地 skills 目录开发，同时镜像到 GitHub 仓库，供另一台工作机 clone 使用。
> 本文件记录实际能跑通的同步方式与踩过的坑。

## 仓库

- 本地路径：`C:\Users\Rasta\AppData\Local\hermes\skills\tunjing-baodian`
- 远程：`https://github.com/RastaJiN/tunjing-baodian`（main 分支）

## 同步方式：GitHub REST API（不要依赖 git push）

本机 git push 走 HTTPS 时容易被代理层打断 TLS（`schannel: failed to receive handshake` 或 `error:0A000126: unexpected eof`），即使浏览器能访问 GitHub。

**稳定做法**：用 Python + urllib 走 `contents` API 逐文件 PUT。流程：

1. `GET /repos/{owner}/{repo}/contents/{path}` 拿现有 `sha`（新文件会 404，忽略即可）；
2. `PUT` 同一 URL，body = `{"message": ..., "content": base64, "sha": <有新文件时必填>}`；
3. 删除用 `DELETE` + `sha`；
4. 验证：`GET /repos/{owner}/{repo}/git/trees/main?recursive=1` 读回完整文件清单。

要点：
- **必须逐文件提交**，不能用 git push 代替；大文件（PNG）单独 PUT 即可。
- **一定要读回 tree 验证**：PUT 返回 200 不代表意图完整，
  常见错误是把二进制文件或缓存一起推上去。
- 推送脚本写一次性用完就删，不要把 Token 写进仓库任何文件。

## 仓库卫生

- 提交前排除 `__pycache__/` 与 `.git/`，`.pyc` 被推上云端会污染仓库。
- 目录改名后（如 `tunjing-adult-drama-engine` → `tunjing-baodian`），GitHub 旧路径文件不会自动消失，
  要显式 `DELETE` 或重建仓库。

## 命名红线

宝典对外文件名、标题、描述一律不出现 `adult` 与「成人」字样，统一用「精品漫剧」。
唯一的例外是**磁盘上真实存在的权重文件名**（如 `qwen21-nsfw-image-edit.safetensors`、
`femaledVaginus-nsfw-v1_3-fine`）——这些字符串改一个字 LoRA 就加载不到，
文档中可以出现，但不得手改。

## 跨机验证

目标机 clone 后先跑：

```bash
python scripts/dryrun_test.py
```

全绿再接入 ComfyUI（默认 `http://127.0.0.1:8188`）。
