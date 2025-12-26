# EdOps 多环境配置管理指南

## 概述

EdOps 支持通过不同的根目录（`--root`）管理多个环境配置，每个环境拥有独立的配置文件和生成的 docker-compose、Nacos 配置文件。这种设计使得不同环境的配置可以完全隔离，避免相互干扰。

### 为什么需要多环境配置？

1. **配置隔离**：不同学校/客户的配置值不同，需要完全隔离
2. **安全性**：不同客户的敏感信息不应相互泄露
3. **灵活性**：可以同时管理多个客户或项目的配置
4. **可追溯性**：每个客户的配置变更历史独立管理

### 目录结构设计（按学校码/客户码划分）

项目需要为不同学校/客户交付独立配置，建议直接以“学校码”作为目录名。例如：

```
~/edops-envs/
├── lianyi/              # 联奕大学
│   ├── config.yml
│   └── env/
└── sysu/                # 中山大学
    ├── config.yml
    └── env/
```

目录命名建议使用有意义的标识符，如学校代码等。

## 配置初始化

### 步骤 1: 创建目录

```bash
# 创建配置目录（使用学校码）
mkdir -p ~/edops-envs/lianyi
```

### 步骤 2: 初始化配置

使用 `edops config save --init` 命令初始化配置。`--init` 选项会清理并重建环境目录，等同于 `--clean`，但提供了更明确的"初始化"语义。

```bash
# 联奕大学配置初始化
edops --root ~/edops-envs/lianyi config save --init \
  --set EDOPS_IMAGE_REGISTRY=zhjx-images.tencentcloudcr.com \
  --set EDOPS_MASTER_NODE_IP=192.168.1.10 \
  --set EDOPS_SCHOOL_ID=88888 \
  --set EDOPS_ENABLED_MODULES=base,common
```

**注意**：`config save` 命令会自动验证必需配置项（如 `EDOPS_IMAGE_REGISTRY`、`EDOPS_MASTER_NODE_IP`），如果缺失会提示错误。

### 步骤 3: 验证配置

```bash
# 验证配置是否完整
edops --root ~/edops-envs/lianyi config validate
```

### 必需配置项

以下配置项是 EdOps 运行所必需的：

- `EDOPS_IMAGE_REGISTRY`: Docker 镜像仓库地址
- `EDOPS_MASTER_NODE_IP`: 主节点 IP 地址
- `EDOPS_NETWORK_NAME`: Docker 网络名称（有默认值）
- `EDOPS_ENABLED_MODULES`: 启用的模块列表（至少包含 `base,common`）

### 常见错误及解决方案

#### 错误 1: `Missing configuration value: 'OPENEDX_SECRET_KEY'`

**原因**：Open edX 相关配置缺失（对于纯 zhjx 业务不是必需的，但系统会检查）

**解决方案**：已在最新版本中修复，`OPENEDX_SECRET_KEY` 会自动生成默认值。如果仍遇到此错误，请更新 EdOps 到最新版本。

#### 错误 2: `Configuration saved but env directory not created`

**原因**：`config save` 命令只保存配置，不会自动生成 `env/` 目录

**解决方案**：需要显式调用 `config save` 来生成配置文件，或使用 `local launch` 命令（会自动生成）

```bash
# 生成配置文件
edops --root ~/edops-envs/dev config save
```

## 配置管理

### 查看配置

```bash
# 查看所有配置
edops --root ~/edops-envs/school-a config list

# 查看 EdOps 相关配置
edops --root ~/edops-envs/school-a config list --filter EDOPS_

# 查看单个配置项
edops --root ~/edops-envs/school-a config get EDOPS_IMAGE_REGISTRY
```

### 修改配置

```bash
# 设置单个配置项
edops --root ~/edops-envs/school-a config save --set EDOPS_MASTER_NODE_IP=192.168.1.11

# 设置多个配置项
edops --root ~/edops-envs/school-a config save \
  --set EDOPS_MASTER_NODE_IP=192.168.1.11 \
  --set EDOPS_SCHOOL_ID=school-a-new

# 交互式配置（推荐首次使用）
edops --root ~/edops-envs/school-a config save --interactive
```

### 删除配置项

```bash
# 删除配置项
edops --root ~/edops-envs/school-a config save --unset EDOPS_SCHOOL_ID
```

### 配置优先级

配置值的优先级（从高到低）：

1. 环境变量（`EDOPS_*`）
2. `config.yml` 中的用户配置
3. `defaults.yml` 中的默认值
4. `base.yml` 中的随机生成值

## 生成配置文件

### 生成 Docker Compose 配置

`edops config save` 命令会自动生成 docker-compose 配置文件到 `env/` 目录：

```bash
# 生成所有配置文件（包括 docker-compose）
edops --root ~/edops-envs/school-a config save
```

生成的文件位置：
- `env/local/docker-compose.yml` - 基础服务配置
- `env/local/docker-compose.prod.yml` - 生产模式配置
- `env/edops/local/zhjx-base.yml` - base 模块配置
- `env/edops/local/zhjx-common.yml` - common 模块配置
- `env/edops/local/zhjx-*.yml` - 其他启用的模块配置

### 生成 Nacos 配置

使用 `edops nacos config render` 命令生成 Nacos 配置文件：

```bash
# 渲染所有 Nacos 配置到默认目录
edops --root ~/edops-envs/school-a nacos config render

# 渲染到指定目录
edops --root ~/edops-envs/school-a nacos config render --output /tmp/nacos-school-a

# 渲染特定服务的配置
edops --root ~/edops-envs/school-a nacos config render --service ly-ac-user-svc
```

生成的 Nacos 配置文件位置：
- `env/nacos/DEFAULT_GROUP/services/*.yaml` - 各服务配置
- `env/nacos/DEFAULT_GROUP/shared/*.yaml` - 共享配置

### 推送 Nacos 配置

```bash
# 渲染并推送到 Nacos
edops --root ~/edops-envs/school-a nacos config push

# 从指定目录推送
edops --root ~/edops-envs/school-a nacos config push --source /tmp/nacos-school-a

# 推送特定服务
edops --root ~/edops-envs/school-a nacos config push --service ly-ac-user-svc
```

## 多客户切换

### 使用 --root 参数

每次执行命令时指定客户根目录：

```bash
# 学校A操作
edops --root ~/edops-envs/school-a config list
edops --root ~/edops-envs/school-a local status

# 学校B操作
edops --root ~/edops-envs/school-b config list
edops --root ~/edops-envs/school-b local status
```

### 使用环境变量

设置 `TUTOR_ROOT` 环境变量，之后可以省略 `--root` 参数：

```bash
# 切换到学校A
export TUTOR_ROOT=~/edops-envs/school-a
edops config list
edops local status

# 切换到学校B
export TUTOR_ROOT=~/edops-envs/school-b
edops config list
edops local status
```

### 创建便捷脚本

创建客户切换脚本 `switch-customer.sh`：

```bash
#!/bin/bash
# switch-customer.sh

CUSTOMER=$1
CUSTOMER_DIR="$HOME/edops-envs/$CUSTOMER"

if [ ! -d "$CUSTOMER_DIR" ]; then
    echo "错误: 客户目录不存在: $CUSTOMER_DIR"
    exit 1
fi

export TUTOR_ROOT="$CUSTOMER_DIR"
echo "已切换到客户: $CUSTOMER"
echo "TUTOR_ROOT=$TUTOR_ROOT"
```

使用方式：

```bash
chmod +x switch-customer.sh
source switch-customer.sh school-a
edops config list  # 现在使用的是 school-a 的配置
```

## 最佳实践

### 1. 目录命名规范

直接使用学校码或客户码作为目录名：

- `school-a` - 学校A
- `school-b` - 学校B
- `customer-001` - 客户001
- `customer-002` - 客户002

建议使用有意义的标识符，便于识别和管理。

### 2. 配置隔离

**重要**：不同客户的配置应该完全独立：

- ✅ 每个客户有独立的 `config.yml`
- ✅ 敏感信息（密码、密钥）使用环境变量
- ✅ 不要在不同客户间共享配置文件

### 3. 敏感信息处理

**推荐方式**：使用环境变量存储敏感信息

```bash
# 设置环境变量（不写入配置文件）
export EDOPS_IMAGE_REGISTRY_PASSWORD="your-password"
export EDOPS_MYSQL_ROOT_PASSWORD="your-mysql-password"

# 然后执行命令
edops --root ~/edops-envs/school-a config save
```

**不推荐**：直接在 `config.yml` 中存储密码

```yaml
# ❌ 不推荐：密码明文存储在配置文件中
EDOPS_IMAGE_REGISTRY_PASSWORD: "your-password"
```

### 4. 配置版本控制

**推荐做法**：

- ✅ 将 `config.yml` 纳入版本控制（但排除敏感信息）
- ✅ 使用 `.gitignore` 排除包含敏感信息的配置
- ✅ 在仓库中保存配置模板（`config.yml.example`）

`.gitignore` 示例：

```
# 排除包含敏感信息的配置文件
edops-envs/*/config.yml
edops-envs/*/env/
```

`config.yml.example` 示例：

```yaml
# 配置模板（不含敏感信息）
EDOPS_IMAGE_REGISTRY: "your-registry.com"
EDOPS_MASTER_NODE_IP: "192.168.1.10"
EDOPS_SCHOOL_ID: "your-school-id"
EDOPS_ENABLED_MODULES: ["base", "common"]
# 敏感信息通过环境变量设置
```

### 5. 配置同步与差异管理

不同客户的配置通常有相似的基础配置，但某些值不同：

**基础配置相同**：
- `EDOPS_IMAGE_REGISTRY`
- `EDOPS_NETWORK_NAME`
- 模块启用列表

**客户特定配置**：
- `EDOPS_MASTER_NODE_IP` - 不同客户的服务器 IP
- `EDOPS_SCHOOL_ID` - 不同客户的学校 ID
- 数据库连接信息
- 第三方服务配置（SMS、SES 等）

**管理建议**：
1. 创建配置模板，记录所有配置项
2. 使用脚本批量设置相同的基础配置
3. 使用环境变量管理客户特定的差异

### 6. 配置验证

在部署前验证配置：

```bash
# 验证配置完整性
edops --root ~/edops-envs/school-a config validate

# 检查生成的配置文件
ls -la ~/edops-envs/school-a/env/local/
ls -la ~/edops-envs/school-a/env/nacos/
```

## 完整工作流程示例

### 场景：为新客户创建配置

```bash
# 1. 创建客户目录
mkdir -p ~/edops-envs/school-a

# 2. 设置环境变量（敏感信息）
export EDOPS_IMAGE_REGISTRY_PASSWORD="school-a-password"
export EDOPS_MYSQL_ROOT_PASSWORD="school-a-mysql-password"

# 3. 初始化配置
edops --root ~/edops-envs/school-a config save \
  --set EDOPS_IMAGE_REGISTRY=zhjx-images.tencentcloudcr.com \
  --set EDOPS_MASTER_NODE_IP=10.0.1.100 \
  --set EDOPS_SCHOOL_ID=school-a \
  --set EDOPS_ENABLED_MODULES=base,common,zhjx_sup

# 4. 验证配置
edops --root ~/edops-envs/school-a config validate

# 5. 生成 Docker Compose 配置
edops --root ~/edops-envs/school-a config save

# 6. 生成 Nacos 配置
edops --root ~/edops-envs/school-a nacos config render

# 7. 推送 Nacos 配置（可选）
edops --root ~/edops-envs/school-a nacos config push

# 8. 查看生成的配置
ls -la ~/edops-envs/school-a/env/
```

### 场景：日常客户配置管理

```bash
# 切换到学校A
export TUTOR_ROOT=~/edops-envs/school-a

# 查看配置
edops config list --filter EDOPS_

# 修改配置
edops config save --set EDOPS_MASTER_NODE_IP=192.168.1.11

# 重新生成配置
edops config save
edops nacos config render

# 查看服务状态
edops local status
```

## 故障排查

### 问题 1: 配置文件未生成

**症状**：执行 `config save` 后，`env/` 目录不存在或为空

**解决方案**：
```bash
# 确保配置已保存
edops --root ~/edops-envs/school-a config save

# 检查 config.yml 是否存在
cat ~/edops-envs/school-a/config.yml

# 手动触发配置生成
edops --root ~/edops-envs/school-a config save --clean
```

### 问题 2: 配置值未生效

**症状**：修改配置后，生成的配置文件中的值未更新

**解决方案**：
```bash
# 1. 确认配置已保存
edops --root ~/edops-envs/school-a config get EDOPS_MASTER_NODE_IP

# 2. 清理并重新生成
edops --root ~/edops-envs/school-a config save --clean

# 3. 检查生成的配置文件
cat ~/edops-envs/school-a/env/local/docker-compose.yml | grep EDOPS_MASTER_NODE_IP
```

### 问题 3: 环境变量未生效

**症状**：设置了环境变量，但配置中未使用

**解决方案**：
```bash
# 1. 确认环境变量已设置
echo $EDOPS_IMAGE_REGISTRY_PASSWORD

# 2. 重新加载配置（环境变量在 config save 时读取）
edops --root ~/edops-envs/school-a config save

# 3. 验证配置
edops --root ~/edops-envs/school-a config get EDOPS_IMAGE_REGISTRY_PASSWORD
```

### 问题 4: 多客户配置混淆

**症状**：在错误的客户目录执行了命令

**解决方案**：
```bash
# 1. 检查当前使用的客户目录
edops --root ~/edops-envs/school-a config printroot

# 2. 明确指定客户目录
edops --root ~/edops-envs/school-a config list

# 3. 使用环境变量固定客户目录
export TUTOR_ROOT=~/edops-envs/school-a
```

## 相关文档

- [快速开始指南](../QUICKSTART_CN.md)
- [配置抽象方案](CONFIGURATION_ABSTRACTION_CN.md)
- [Nacos 配置管理](NACOS_CONFIG_MANAGEMENT_CN.md)
- [CLI 命令参考](edops-cli.md)

## 总结

多客户配置管理是 EdOps 的核心功能之一，通过合理使用 `--root` 参数或 `TUTOR_ROOT` 环境变量，可以轻松管理多个客户的配置。关键要点：

1. ✅ 每个客户使用独立的根目录（以学校码/客户码命名）
2. ✅ 敏感信息使用环境变量
3. ✅ 配置变更后重新生成配置文件
4. ✅ 部署前验证配置完整性
5. ✅ 遵循配置命名和管理规范

