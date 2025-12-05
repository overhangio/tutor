# EdOps 测试指南

## 🧪 健康检查命令测试

### 前置条件
由于健康检查需要访问实际服务，需要先配置：

```bash
# 激活环境
cd /Users/zhumin/zhjx/edops
source venv/bin/activate

# 配置 IP 地址（指向您的服务器）
edops config save --set EDOPS_MASTER_NODE_IP=192.168.1.100
```

### 测试场景 1: 服务未启动（预期失败）

```bash
# 测试健康检查（服务未运行）
edops local healthcheck base

# 预期输出：
# 正在检查 base...
# 正在检查 zhjx-nacos 的健康状态...
# ✗ zhjx-nacos 健康检查失败
# 正在检查 zhjx-mysql 的健康状态...
# ✗ zhjx-mysql 健康检查失败
# ...
# ✗ 部分健康检查失败
```

### 测试场景 2: 本地测试（模拟服务）

如果想测试命令逻辑而不实际部署服务，可以：

```bash
# 1. 修改配置指向本地
edops config save --set EDOPS_MASTER_NODE_IP=127.0.0.1

# 2. 启动一个简单的 HTTP 服务器（模拟 nacos）
python3 -m http.server 8848 &

# 3. 运行健康检查
edops local healthcheck base
# nacos 的 HTTP 检查会成功（返回 200）
# mysql/redis 的 TCP 检查会失败（端口未监听）

# 4. 停止测试服务器
kill %1
```

### 测试场景 3: 完整部署环境

如果已经部署了 zhjx 服务：

```bash
# 1. 确保配置正确
edops config get EDOPS_MASTER_NODE_IP
# 应该显示您的服务器 IP

# 2. 运行健康检查
edops local healthcheck

# 3. 检查特定模块
edops local healthcheck base
edops local healthcheck common
```

---

## 🖼️ 镜像管理命令测试

### 测试镜像列表

```bash
# 列出所有模块的镜像
edops images list

# 预期输出：
# EdOps 模块镜像:
#
# base:
#   （base 模块使用外部镜像，无自定义镜像）
#
# common:
#   ly-ac-gateway-svc              zhjx-images.tencentcloudcr.com/ly-ac-gateway-svc:latest
#   ly-ac-user-svc                 zhjx-images.tencentcloudcr.com/ly-ac-user-svc:latest
#   ...

# 只看 common 模块
edops images list --module common
```

### 测试版本查询（需要仓库访问权限）

```bash
# 查询服务的可用版本
edops images versions ly-ac-gateway-svc

# 如果遇到认证错误，需要配置：
export EDOPS_IMAGE_REGISTRY_USER=your_username
export EDOPS_IMAGE_REGISTRY_PASSWORD=your_password

# 或者
edops config save \
  --set EDOPS_IMAGE_REGISTRY_USER=your_username \
  --set EDOPS_IMAGE_REGISTRY_PASSWORD=your_password
```

### 测试镜像检查

```bash
# 检查镜像详情
edops images inspect ly-ac-gateway-svc --tag latest
```

---

## 📜 部署历史测试

### 测试历史记录

```bash
# 查看历史（可能为空）
edops local history

# 如果为空，说明：
# ✓ 历史功能正常，只是还没有记录
# ✓ deploy-history.yml 会在首次部署时创建
```

### 模拟历史记录（可选）

```bash
# 手动创建历史文件进行测试
cat > $(edops config printroot)/deploy-history.yml << 'EOF'
records:
  - timestamp: "2024-12-05T10:00:00"
    module: "common"
    service: "ly-ac-gateway-svc"
    image: "ly-ac-gateway-svc"
    tag: "v1.2.0"
    operation: "deploy"
  - timestamp: "2024-12-05T11:00:00"
    module: "common"
    service: "ly-ac-gateway-svc"
    image: "ly-ac-gateway-svc"
    tag: "v1.3.0"
    operation: "deploy"
EOF

# 再次查看历史
edops local history

# 预期输出：
# 部署历史:
# → 2024-12-05 common          ly-ac-gateway-svc              v1.3.0     (deploy)
# → 2024-12-05 common          ly-ac-gateway-svc              v1.2.0     (deploy)
```

---

## 🔧 配置管理测试

### 测试配置命令

```bash
# 获取配置项
edops config get EDOPS_IMAGE_REGISTRY

# 列出所有 EdOps 配置
edops config list --filter EDOPS_

# 验证配置
edops config validate

# 如果验证失败，说明需要配置：
edops config save --interactive
```

### 测试配置格式

```bash
# 文本格式（默认）
edops config list --filter EDOPS_

# JSON 格式
edops config list --filter EDOPS_ --format json

# YAML 格式
edops config list --filter EDOPS_ --format yaml
```

---

## 🔍 调试技巧

### 1. 查看 root 目录

```bash
# 查看项目根目录位置
edops config printroot

# 查看目录内容
ls -la $(edops config printroot)

# 查看配置文件
cat $(edops config printroot)/config.yml

# 查看历史文件
cat $(edops config printroot)/deploy-history.yml
```

### 2. 验证模板渲染

```python
# 在 Python 中测试
python3 << 'EOF'
from tutor import config as tutor_config
from tutor import env as tutor_env

# 加载配置
config = tutor_config.load("$(edops config printroot)")

# 测试渲染
template = "http://{{EDOPS_MASTER_NODE_IP}}:8848/nacos/"
rendered = tutor_env.render_str(config, template)
print(f"渲染结果: {rendered}")
EOF
```

### 3. 检查模块加载

```python
# 验证模块正确加载
python3 << 'EOF'
from tutor.edops import modules
from tutor.edops.health import HealthCheckType

all_modules = modules._load_modules()

# 检查 base 模块
base = all_modules['base']
print(f"✓ base 模块加载成功")
print(f"  健康检查数量: {len(base.health_checks)}")

for check in base.health_checks:
    print(f"  - {check.service}: {check.type}")
    print(f"    类型正确: {isinstance(check.type, HealthCheckType)}")

# 检查 common 模块
common = all_modules['common']
print(f"\n✓ common 模块加载成功")
print(f"  镜像数量: {len(common.images)}")

for img in common.images:
    print(f"  - {img.name}")
EOF
```

---

## ⚠️ 已知限制

### 插件警告（可忽略）
```
⚠️  Failed to enable plugin 'indigo': plugin 'indigo' is not installed.
⚠️  Failed to enable plugin 'mfe': plugin 'mfe' is not installed.
```

**说明**: 这些是 Open edX 的插件，不影响 EdOps 功能。可以在 `config.yml` 中移除：
```yaml
PLUGINS: []  # 清空插件列表
```

### 健康检查需要服务运行
HTTP 和 TCP 健康检查需要目标服务实际运行。如果服务未启动：
- ✗ 健康检查会失败
- ✅ 命令本身不会崩溃
- ✅ 会显示友好的错误消息

---

## 📋 完整测试清单

### 功能测试
- [x] `edops --version` - 显示版本号
- [x] `edops config list` - 列出配置
- [x] `edops config validate` - 验证配置
- [ ] `edops local healthcheck` - 需要实际服务或配置 IP
- [x] `edops local history` - 显示历史（可能为空）
- [x] `edops images list` - 列出镜像
- [ ] `edops images versions <service>` - 需要仓库权限

### Bug 验证
- [x] Bug #1 (类型转换) - 已修复，类型正确转换
- [x] Bug #2 (镜像名称) - 已修复，名称一致
- [ ] Bug #3 (模板渲染) - 已修复，需要实际服务验证

---

## 🎯 下一步

### 最小化测试（无需实际服务）
```bash
# 这些命令不需要实际服务就能测试
edops --help
edops config list --filter EDOPS_
edops images list
edops local history
```

### 完整测试（需要服务）
```bash
# 1. 配置正确的服务器 IP
edops config save --set EDOPS_MASTER_NODE_IP=<your-server-ip>

# 2. 运行健康检查
edops local healthcheck

# 3. 如果服务运行中，应该能看到：
# ✓ zhjx-nacos 健康
# ✓ zhjx-mysql 健康
# ...
```

---

**建议**: 先运行最小化测试验证命令功能，再进行完整的服务集成测试。

