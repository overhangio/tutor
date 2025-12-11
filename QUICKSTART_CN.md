# EdOps 快速开始

## 安装完成 ✓

EdOps 已成功安装在虚拟环境中。

## 使用方法

### 1. 激活虚拟环境

每次使用 edops 前，需要先激活虚拟环境：

```bash
cd /Users/zhumin/zhjx/edops
source venv/bin/activate
```

激活后，命令行提示符会显示 `(venv)`。

### 2. 验证安装

```bash
edops --version
# 输出：edops, version 20.0.2
```

### 3. 查看可用命令

```bash
edops --help
```

## 常用命令

### 配置管理

```bash
# 交互式配置
edops config save --interactive

# 查看配置项
edops config get EDOPS_IMAGE_REGISTRY

# 列出所有 EdOps 配置
edops config list --filter EDOPS_

# 验证配置
edops config validate

# 渲染模块模板
edops config render base
```

### 部署管理

```bash
# 查看服务状态
edops local status

# 运行健康检查
edops local healthcheck

# 查看部署历史
edops local history

# 查看日志
edops local logs --follow
```

### 镜像管理

```bash
# 列出模块镜像
edops images list

# 查询可用版本
edops images versions ly-ac-gateway-svc

# 检查镜像详情
edops images inspect ly-ac-gateway-svc --tag latest
```

#### Docker Registry 认证配置

使用 `edops images versions` 和 `inspect` 命令查询镜像仓库时，需要配置认证信息。

**方式 1：使用环境变量（推荐）**

```bash
# 设置认证信息
export EDOPS_IMAGE_REGISTRY_USER="tcr\$edops"
export EDOPS_IMAGE_REGISTRY_PASSWORD="your-password"

# 或使用 Token
export EDOPS_IMAGE_REGISTRY_TOKEN="your-token"
```

**方式 2：使用配置文件**

```bash
# 使用 edops config save --set 命令
edops config save --set EDOPS_IMAGE_REGISTRY_USER="tcr\$edops"
edops config save --set EDOPS_IMAGE_REGISTRY_PASSWORD="your-password"

# 或使用 Token
edops config save --set EDOPS_IMAGE_REGISTRY_TOKEN="your-token"

# 也可以一次设置多个值
edops config save --set EDOPS_IMAGE_REGISTRY_USER="tcr\$edops" --set EDOPS_IMAGE_REGISTRY_PASSWORD="your-password"
```

**腾讯云 TCR 认证示例**

```bash
# 腾讯云 TCR 用户名格式：tcr$<namespace>
export EDOPS_IMAGE_REGISTRY_USER="tcr\$edops"
export EDOPS_IMAGE_REGISTRY_PASSWORD="jLLz5qLCFX8tOwiKbRA3Au1q3Ib8RKZW"

# 验证配置
edops images versions ly-ac-gateway-svc
```

**注意**：
- 用户名中的 `$` 符号在 shell 中需要转义为 `\$`，或在配置文件中直接使用 `tcr$edops`
- 密码和 Token 等敏感信息建议使用环境变量，避免写入配置文件
- 如果未配置认证信息，查询镜像仓库时会返回 401 Unauthorized 错误

## 退出虚拟环境

使用完毕后，可以退出虚拟环境：

```bash
deactivate
```

## 创建别名（可选）

为了更方便使用，可以在 `~/.zshrc` 中添加别名：

```bash
alias edops='source /Users/zhumin/zhjx/edops/venv/bin/activate && edops'
```

然后重新加载配置：

```bash
source ~/.zshrc
```

之后就可以直接使用 `edops` 命令了。

## 首次部署流程

```bash
# 1. 激活环境
cd /Users/zhumin/zhjx/edops
source venv/bin/activate

# 2. 配置系统
edops config save --interactive

# 3. 验证配置
edops config validate

# 4. 启动平台（如果已有模块模板）
edops local launch --pullimages

# 5. 检查状态
edops local status
edops local healthcheck
```

## 文档链接

- 完整 CLI 文档：`docs/edops-cli.md`
- 模块说明：`docs/zhjx-modules.md`
- 设计决策：`docs/DESIGN_DECISIONS_CN.md`
- 实施报告：`docs/reports/` 目录

## 故障排查

### 命令找不到

确保已激活虚拟环境：
```bash
source /Users/zhumin/zhjx/edops/venv/bin/activate
```

### 查看日志

```bash
edops local logs --tail 100 <service-name>
```

### 检查配置

```bash
edops config list --filter EDOPS_
edops config printroot
```

## 开发模式

当前安装为可编辑模式（`pip install -e .`），代码修改会立即生效，无需重新安装。

## 更新依赖

```bash
cd /Users/zhumin/zhjx/edops
source venv/bin/activate
pip install -e . --upgrade
```

