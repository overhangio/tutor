# EdOps CLI 参考手册

EdOps 是联奕智慧教学团队的统一部署工具，基于 Tutor 构建，用于管理微服务、前端工程和 Open edX 子系统的部署。

## 核心概念

### 部署模式

EdOps 支持多种部署模式：

- **local**: 单机 Docker Compose 部署
- **portainer**: Docker Swarm / Portainer 多节点部署
- **k8s**: Kubernetes 部署（规划中）

### 模块系统

EdOps 采用模块化架构：

- **base**: 必选，提供 nacos/mysql/redis/rabbitmq 等基础中间件
- **common**: 必选，提供共享域服务与租户管理前端
- **zhjx_***: 可选业务模块，如 zhjx_zlmediakit、zhjx_sup 等

## 配置管理命令

### edops config save

创建并保存配置。

```bash
edops config save --interactive
edops config save --set EDOPS_MASTER_NODE_IP=192.168.1.100
```

选项：
- `-i, --interactive`: 交互式配置
- `-s, --set KEY=VAL`: 设置配置项
- `-e, --env-only`: 仅更新环境目录，不修改 config.yml

### edops config get

获取单个配置项的值。

```bash
edops config get EDOPS_IMAGE_REGISTRY
```

### edops config list

列出所有配置项。

```bash
edops config list
edops config list --filter EDOPS_
edops config list --format json
```

选项：
- `--filter PREFIX`: 按前缀过滤
- `--format [text|json|yaml]`: 输出格式

### edops config validate

验证配置完整性。

```bash
edops config validate
```

检查必需的配置项：
- `EDOPS_IMAGE_REGISTRY`
- `EDOPS_MASTER_NODE_IP`
- `EDOPS_NETWORK_NAME`


## 部署命令

### edops local launch

首次部署或完整重启平台。

```bash
edops local launch
edops local launch --pullimages
```

选项：
- `--pullimages`: 拉取最新镜像
- `--no-health-check`: 跳过健康检查

### edops local start

启动服务。

```bash
edops local start
edops local start zhjx-nacos zhjx-mysql
```

### edops local stop

停止服务。

```bash
edops local stop
edops local stop zhjx-nacos
```

### edops local restart

重启服务。

```bash
edops local restart
edops local restart zhjx-nacos
```

### edops local status

查看详细的服务状态。

```bash
edops local status
edops local status --module base
edops local status --format json
```

选项：
- `--module NAME`: 过滤模块
- `--format [table|json]`: 输出格式

### edops local logs

查看服务日志。

```bash
edops local logs
edops local logs --follow
edops local logs --tail 100 zhjx-nacos
```

### edops local healthcheck

手动触发健康检查。

```bash
edops local healthcheck
edops local healthcheck base
```

### edops local history

查看部署历史。

```bash
edops local history
edops local history --module common
edops local history --limit 50
```

选项：
- `--module NAME`: 过滤模块
- `--service NAME`: 过滤服务
- `--limit N`: 显示记录数

### edops local rollback

回滚到之前的版本。

```bash
edops local rollback common
edops local rollback common --version v1.2.3
```

## 镜像管理命令

### edops images list

列出所有模块的镜像及版本。

```bash
edops images list
edops images list --module common
```

### edops images versions

查询镜像仓库中的可用版本。

```bash
edops images versions ly-ac-gateway-svc
```

### edops images inspect

查看镜像详细信息。

```bash
edops images inspect ly-ac-gateway-svc
edops images inspect ly-ac-gateway-svc --tag v1.2.3
```

### edops images pull

拉取镜像。

```bash
edops images pull ly-ac-gateway-svc
```

### edops images build permissions

构建 Permissions 镜像。

Permissions 镜像用于在容器启动前设置数据目录的所有权，避免权限问题。

```bash
# 构建 permissions 镜像
edops images build permissions

# 推送到镜像仓库
docker tag ${EDOPS_IMAGE_REGISTRY}/library/permissions:v1.0.0 ${EDOPS_IMAGE_REGISTRY}/library/permissions:v1.0.0
docker push ${EDOPS_IMAGE_REGISTRY}/library/permissions:v1.0.0
```

**UID 分配说明**：

- **中间件服务**：
  - RabbitMQ/Redis: UID 999
  - MinIO/Elasticsearch/KKFileView/ZLMediaKit: UID 1000
  - Kafka: UID 1001
- **业务服务**：
  - Spring Boot 微服务: UID 1000（预留，当前无数据目录挂载）

## Portainer 命令（实验性）

### edops portainer render

渲染 Portainer / Swarm 模板。

```bash
edops portainer render
edops portainer render base
```

注意：Portainer 模板支持目前处于实验阶段。

## 常见场景

### 首次部署

```bash
# 1. 配置系统
edops config save --interactive

# 2. 验证配置
edops config validate

# 3. 启动平台
edops local launch --pullimages
```

### 版本升级

```bash
# 1. 更新版本配置
edops config save --set EDOPS_VERSION_SVC_DEFAULT=v1.3.0

# 2. 拉取新镜像
edops images pull all

# 3. 重启服务
edops local restart
```

### 故障回滚

```bash
# 1. 查看历史
edops local history --module common

# 2. 回滚到之前版本
edops local rollback common

# 3. 重启服务
edops local restart
```

### 健康检查

```bash
# 检查所有模块
edops local healthcheck

# 检查特定模块
edops local healthcheck base

# 查看服务状态
edops local status
```

## 配置文件

### config.yml

主配置文件，位于 `$(edops config printroot)/config.yml`。

关键配置项：

```yaml
EDOPS_IMAGE_REGISTRY: zhjx-images.tencentcloudcr.com
EDOPS_MASTER_NODE_IP: 192.168.1.100
EDOPS_NETWORK_NAME: zhjx-network
EDOPS_VERSION_SVC_DEFAULT: latest
EDOPS_VERSION_UI_CONSOLE: latest
EDOPS_VERSION_UI_AUTH: latest
EDOPS_ENABLED_MODULES:
  - zhjx_zlmediakit
```

### edops-modules.yml

模块定义文件，位于 `tutor/templates/config/edops-modules.yml`。

定义了所有模块的元数据：
- 依赖关系
- 健康检查
- 镜像映射

### deploy-history.yml

部署历史记录文件，位于 `$(edops config printroot)/deploy-history.yml`。

记录所有部署、回滚、重启操作。

## 环境变量

EdOps 支持以下环境变量：

- `TUTOR_ROOT`: EdOps 根目录（默认：`~/.local/share/tutor`）
- `EDOPS_IMAGE_REGISTRY_TOKEN`: 镜像仓库访问令牌
- `EDOPS_IMAGE_REGISTRY_USER`: 镜像仓库用户名
- `EDOPS_IMAGE_REGISTRY_PASSWORD`: 镜像仓库密码

## 最佳实践

### 版本管理

- 使用语义化版本号（如 `v1.2.3`）
- 为每次发布创建 Git 标签
- 在生产环境固定版本，避免使用 `latest`

### 健康检查

- 部署后始终运行 `edops local healthcheck`
- 监控 `edops local status` 输出
- 配置告警系统监控容器状态

### 回滚策略

- 在升级前记录当前版本
- 保留最近 3-5 个版本的镜像
- 测试环境先验证升级流程

### 配置管理

- 使用 `edops config save` 而不是手动编辑 `config.yml`
- 敏感信息通过环境变量注入
- 定期备份 `config.yml` 和 `deploy-history.yml`

## 故障排查

### 服务无法启动

```bash
# 1. 检查日志
edops local logs --tail 100 <service-name>

# 2. 检查状态
edops local status

# 3. 检查配置
edops config validate
```

### 健康检查失败

```bash
# 1. 手动触发检查
edops local healthcheck <module>

# 2. 检查网络连接
docker network ls
docker network inspect zhjx-network

# 3. 重启相关服务
edops local restart <module>
```

### 镜像拉取失败

```bash
# 1. 检查仓库配置
edops config get EDOPS_IMAGE_REGISTRY

# 2. 测试认证
docker login zhjx-images.tencentcloudcr.com

# 3. 手动拉取测试
docker pull zhjx-images.tencentcloudcr.com/<image>:<tag>
```

## 开发与贡献

EdOps 基于 Tutor 构建，遵循以下开发规范：

- Python 3.10+
- 使用 Typer/Click 构建 CLI
- 使用 Jinja2 渲染模板
- 遵循 PEP 8 代码风格

详见 `CONTRIBUTING.md`。

