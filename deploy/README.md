# deploy

当前目录用于存放 `youtube-parser` 的部署补充文件。

当前已经补齐：

- `compose.prod.yaml`
- `.env.prod.example`
- `scripts/build-release-image.sh`
- `scripts/export-release-bundle.sh`
- `scripts/deploy-prebuilt-release.sh`

## 手动发布步骤

当前推荐使用下面三段脚本完成发布：

- `scripts/build-release-image.sh`
- `scripts/export-release-bundle.sh`
- `scripts/deploy-prebuilt-release.sh`

### 1. 准备生产环境文件

```bash
cd /Users/apple/Workspace/linker-platform/parsers/youtube-parser/deploy
cp .env.prod.example .env.prod
```

至少确认：

- `YOUTUBE_PARSER_HOST_PORT`

### 2. 本地构建镜像

```bash
cd /Users/apple/Workspace/linker-platform/parsers/youtube-parser
IMAGE_TAG=20260323-<git短提交> ./scripts/build-release-image.sh
```

默认镜像名：`ballbase/youtube-parser`

### 3. 导出镜像 bundle

```bash
cd /Users/apple/Workspace/linker-platform/parsers/youtube-parser
IMAGE_TAG=20260323-<git短提交> ./scripts/export-release-bundle.sh
```

导出目录默认在：

```text
.tmp/release/<IMAGE_TAG>/
```

### 4. 上传服务器并更新

```bash
cd /Users/apple/Workspace/linker-platform/parsers/youtube-parser
DEPLOY_HOST=117.72.207.52 \
DEPLOY_USER=root \
DEPLOY_PASSWORD='服务器密码' \
DEPLOY_ENV_FILE=deploy/.env.prod \
IMAGE_TAG=20260323-<git短提交> \
./scripts/deploy-prebuilt-release.sh
```

默认服务器目录：

```text
/root/apps/parsers/youtube-parser
```

### 5. 发布后验证

```bash
curl -sS http://127.0.0.1:3000/api/v1/health
curl -sS http://127.0.0.1:3000/api/v1/capabilities
```

### 6. 回滚

```bash
DEPLOY_HOST=117.72.207.52 \
DEPLOY_USER=root \
DEPLOY_PASSWORD='服务器密码' \
DEPLOY_ENV_FILE=deploy/.env.prod \
IMAGE_TAG=<旧版本号> \
./scripts/deploy-prebuilt-release.sh
```
