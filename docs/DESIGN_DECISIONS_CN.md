# EdOps 核心设计决策

本文档记录 EdOps 开发过程中的关键设计决策和共识，供团队参考和后续开发遵循。

## 1. 构建策略：仅镜像管理，不构建源码 🏗️

### 决策
**EdOps 不负责源码构建，仅管理 Jenkins 产出的镜像。**

### 背景
在讨论 1.2 和 1.3 构建功能时，需要明确是"基于源码构建"还是"基于现有镜像"。最终确定采用"仅镜像管理"策略。

### 理由
1. **职责分离** - Jenkins CI/CD 已有完善的构建流水线和环境
2. **简化依赖** - EdOps 无需安装 Maven、Node.js、pnpm 等构建工具
3. **提升效率** - 避免在部署机器上进行耗时的编译操作
4. **统一流程** - 所有镜像都经过 Jenkins 质量检查后才进入部署环节

### 影响

#### EdOps 负责
- ✅ 从镜像仓库查询可用版本
- ✅ 拉取指定版本的镜像
- ✅ 管理镜像版本配置
- ✅ 记录部署历史
- ✅ 镜像版本回滚

#### Jenkins 负责
- 📦 Maven 构建 Java 服务
- 📦 pnpm 构建前端应用
- 📦 Docker 镜像打包
- 📦 推送镜像到仓库
- 📦 镜像质量检查

#### 可选支持
- 🔧 通过 Jenkins REST API 触发构建（`edops images build`）
- 🔧 查询 Jenkins 构建状态
- 🔧 作为便捷封装，不替代 Jenkins

### 实现
- `tutor/edops/image_registry.py` - 镜像仓库查询
- `tutor/commands/images.py` - 镜像管理命令
- 无 `builders.py` 或源码编译逻辑

### 代码示例
```bash
# EdOps 用法（仅镜像管理）
edops images versions ly-ac-gateway-svc    # 查询可用版本
edops config save --set EDOPS_VERSION_SVC_DEFAULT=v1.3.0
edops images pull all                      # 拉取镜像
edops local launch                         # 部署

# Jenkins 用法（构建）
jenkins build ly-ac-gateway-svc --branch develop
```

---

## 2. 配置策略：仅部署模式，无多环境 🔧

### 决策
**EdOps 只区分部署模式（local/portainer/k8s），不引入 dev/beta/prod 环境配置文件。**

### 背景
在讨论配置管理时，原计划包含多环境配置覆盖（`env/dev.yml`、`env/beta.yml`、`env/prod.yml`）。最终决定简化为仅部署模式。

### 理由
1. **避免复杂性** - 多环境配置会增加理解和维护成本
2. **单一配置源** - 所有环境共享同一个 `config.yml`，减少歧义
3. **部署模式已足够** - local/portainer/k8s 已能满足不同场景需求
4. **配置简单化** - 通过修改 `config.yml` 中的变量即可适配不同环境

### 部署模式说明

#### local 模式（单机）
```bash
edops local launch
# 使用模板: tutor/templates/edops/local/*.yml
# 适用场景: 单机 Docker Compose 部署
```

#### portainer 模式（Swarm）
```bash
edops portainer render
# 使用模板: tutor/templates/edops/portainer/*.yml（规划中）
# 适用场景: 多节点 Docker Swarm 集群
```

#### k8s 模式（Kubernetes）
```bash
edops k8s launch
# 使用模板: tutor/templates/k8s/*.yml
# 适用场景: Kubernetes 集群部署
```

### 环境差异处理

**不同环境的差异通过修改同一个 `config.yml` 实现**：

```yaml
# 开发环境
EDOPS_MASTER_NODE_IP: "127.0.0.1"
EDOPS_VERSION_SVC_DEFAULT: "latest"

# 生产环境（修改相同的配置文件）
EDOPS_MASTER_NODE_IP: "192.168.1.100"
EDOPS_VERSION_SVC_DEFAULT: "v1.3.0"
```

或通过不同的 `--root` 实现完全隔离：
```bash
edops --root ~/dev-root config save
edops --root /opt/prod-root config save
```

### 实现
- 无 `env/dev.yml`、`env/beta.yml` 等文件
- 无多环境加载逻辑
- 仅通过子命令区分部署模式

### 优势
- ✅ 配置文件少，易于理解
- ✅ 操作简单，学习曲线平缓
- ✅ 减少配置合并的复杂性
- ✅ 降低配置冲突的可能性

---

## 3. 双命令支持：edops 和 tutor 等价 🔀

### 决策
**提供 `edops` 和 `tutor` 两个命令，指向同一入口，功能完全相同。**

### 实现
```toml
# pyproject.toml
[project.scripts]
edops = "tutor.commands.cli:main"
tutor = "tutor.commands.cli:main"
```

### 理由
1. **向后兼容** - 保留 `tutor` 命令以兼容 Open edX 原有使用方式
2. **品牌标识** - `edops` 命令明确这是联奕智慧教学的定制版本
3. **灵活选择** - 用户可根据场景和习惯选择命令名称
4. **平滑过渡** - 从 Tutor 迁移过来的用户无需改变习惯

### 使用建议

#### 对于 zhjx 业务（推荐使用 edops）
```bash
edops config save
edops local status
edops images list
```

#### 对于 Open edX（可使用 tutor）
```bash
tutor local launch
tutor k8s start
```

#### 两者完全等价
```bash
edops --version  # edops, version 20.0.2
tutor --version  # edops, version 20.0.2（相同）

edops config list
tutor config list  # 完全相同的输出
```

### 文档规范
- 文档中统一使用 `edops` 命令
- 培训材料推荐使用 `edops`
- 但强调两者等价，用户可自由选择

---

## 4. 模块化架构 🧩

### 决策
**采用模块化架构，通过 `edops-modules.yml` 声明式管理所有模块。**

### 模块分类

#### 必选模块（required: true）
- **base** - nacos/mysql/redis/rabbitmq 等基础中间件
- **common** - 共享域服务与租户管理前端

#### 可选模块（required: false）
- **zhjx_zlmediakit** - ZLMediaKit 直播流接入
- **zhjx_sup** - AI 督导系统
- **zhjx_ilive_ecom** - 直播实训电商
- **zhjx_media** - 流媒体处理
- 其他业务模块...

### 模块定义结构
```yaml
module_name:
  required: true/false           # 是否必选
  description: "模块描述"
  template: "edops/local/*.yml"  # 模板路径
  target: "local/*.yml"          # 渲染目标
  depends_on: []                 # 依赖的模块
  images:                        # 镜像列表
    - name: service-name
      repository: "registry/image"
      version_var: VERSION_VAR
  health_checks:                 # 健康检查
    - service: service-name
      type: http/tcp
      url/host/port: ...
```

### 优势
- 声明式配置，易于理解和维护
- 自动依赖解析和排序
- 统一的健康检查定义
- 清晰的镜像版本映射

---

## 5. 历史可追溯 📜

### 决策
**所有部署/回滚/重启操作记录到 `deploy-history.yml`，实现完整的操作审计。**

### 记录内容
```yaml
records:
  - timestamp: "2024-12-05T10:30:00"
    module: common
    service: ly-ac-gateway-svc
    image: ly-ac-gateway-svc
    tag: v1.3.0
    operation: deploy
  - timestamp: "2024-12-05T11:00:00"
    module: common
    service: ly-ac-gateway-svc
    image: ly-ac-gateway-svc
    tag: v1.2.5
    operation: rollback
```

### 用途
1. **故障分析** - 追溯最近的变更
2. **回滚决策** - 查询可回滚的版本
3. **审计合规** - 记录所有操作历史
4. **统计分析** - 部署频率、成功率等

### 命令
```bash
edops local history                    # 查看历史
edops local history --module common    # 按模块过滤
edops local rollback common            # 回滚到上一版本
```

---

## 6. 健康检查优先 ❤️‍🩹

### 决策
**启动后必须验证基础服务可用性，健康检查配置在模块定义中声明。**

### 检查类型
- **HTTP** - 检查 HTTP 端点响应（如 `/health`、`/actuator/health`）
- **TCP** - 检查端口连通性（如数据库、Redis）
- **CONTAINER** - 检查容器状态（规划中）

### 配置示例
```yaml
health_checks:
  - service: zhjx-nacos
    type: http
    url: "http://{{EDOPS_MASTER_NODE_IP}}:8848/nacos/"
    timeout: 30
  - service: zhjx-mysql
    type: tcp
    host: "{{EDOPS_MASTER_NODE_IP}}"
    port: 3306
    timeout: 10
```

### 集成点
- `edops local launch` - 启动后自动检查
- `edops local healthcheck` - 手动触发检查
- `edops local status` - 显示健康状态

### 失败处理
- 显示清晰的错误消息
- 提供诊断建议
- 支持重试机制

---

## 7. 版本即配置 📌

### 决策
**镜像版本通过 `config.yml` 管理，部署 = 配置渲染 + 容器启动。**

### 原理
所有镜像版本定义在配置中：
```yaml
EDOPS_VERSION_SVC_DEFAULT: "v1.3.0"
EDOPS_VERSION_UI_CONSOLE: "v2.1.0"
EDOPS_VERSION_UI_AUTH: "v2.0.5"
```

模板中引用这些变量：
```yaml
services:
  ly-ac-gateway-svc:
    image: {{EDOPS_IMAGE_REGISTRY}}/ly-ac-gateway-svc:{{EDOPS_VERSION_SVC_DEFAULT}}
```

### 部署流程
```
修改 config.yml 版本
    ↓
edops config save
    ↓
edops local render（自动）
    ↓
生成新的 docker-compose.yml
    ↓
edops local restart
    ↓
使用新版本镜像重启容器
```

### 优势
- ✅ 版本管理集中化
- ✅ 易于追踪和回滚
- ✅ 支持批量升级
- ✅ 配置即文档

---

## 8. Fork 策略：保留 Open edX 能力 🔱

### 决策
**Fork Tutor 而非从零开发，保留对 Open edX 的完整支持。**

### 分支策略
- `edops-main` - 主开发分支
- 定期同步上游 Tutor 更新
- Open edX 部署能力完整保留

### 命名空间
- 包名：`edops`
- 代码目录：仍使用 `tutor/`
- 命令：提供 `edops` 和 `tutor` 双命令
- 配置前缀：新增 `EDOPS_*`，保留原有 `TUTOR_*`

### Open edX 集成
```bash
# 单独部署 Open edX
edops local launch

# 同时部署 Open edX + zhjx 模块
edops config save --set EDOPS_ENABLED_MODULES='["zhjx_zlmediakit"]'
edops local launch
```

---

## 9. 部署模式架构 🏛️

### 三种部署模式

#### local - 单机模式
- **技术栈**: Docker Compose
- **适用场景**: 开发测试、小规模部署、演示环境
- **模板位置**: `tutor/templates/edops/local/`
- **命令**: `edops local launch/start/stop`

#### portainer - Swarm 模式
- **技术栈**: Docker Swarm + Portainer
- **适用场景**: 多节点集群、中等规模生产环境
- **模板位置**: `tutor/templates/edops/portainer/`（规划中）
- **命令**: `edops portainer render/deploy`

#### k8s - Kubernetes 模式
- **技术栈**: Kubernetes + Helm
- **适用场景**: 大规模生产环境、云原生部署
- **模板位置**: `tutor/templates/k8s/`
- **命令**: `edops k8s launch/start/stop`

### 模板共享
- 所有模式共享同一个 `config.yml`
- 通过 Jinja 变量适配不同模式
- 模板按模式组织，互不干扰

---

## 10. 中文化策略 🌏

### 决策
**所有命令交互、帮助文本、用户消息统一使用中文。**

### 原因
1. **团队内部使用** - 主要用户是国内团队
2. **降低门槛** - 减少英文理解成本
3. **提升效率** - 快速理解命令含义
4. **本地化体验** - 更好的用户体验

### 中文化范围
- ✅ 命令帮助文本（`help=`）
- ✅ 选项说明（所有 `--option` 的 help）
- ✅ 用户消息（fmt.echo_info/error）
- ✅ 错误提示（TutorError）
- ✅ 函数文档字符串
- ✅ 代码注释

### 保持英文的部分
- ❌ 变量名
- ❌ 函数名
- ❌ 配置键名（如 `EDOPS_IMAGE_REGISTRY`）
- ❌ 日志 JSON 字段

### 双命令兼容
`edops` 和 `tutor` 命令都已中文化，输出完全相同。

---

## 11. 模块依赖管理 🔗

### 决策
**自动解析模块依赖关系，确保启动顺序正确。**

### 依赖声明
```yaml
base:
  depends_on: []           # 无依赖，最先启动

common:
  depends_on: ["base"]     # 依赖 base

zhjx_zlmediakit:
  depends_on: ["base"]     # 依赖 base
```

### 自动排序算法
```python
def _resolve_module_order(enabled: List[str]) -> List[str]:
    # 拓扑排序，处理依赖关系
    # 检测循环依赖
    # 返回正确的启动顺序
```

### 启动顺序保证
```
base (nacos/mysql/redis...)
  ↓
common (gateway/users/auth...)
  ↓
zhjx_zlmediakit/zhjx_sup/... (并行启动)
```

---

## 12. 数据与代码分离 📂

### 决策
**虚拟环境（代码）与项目根目录（数据）完全分离。**

### 架构
```
代码层（venv）
└── edops 命令
    └── tutor Python 包
        └── 逻辑和模板

数据层（root）
├── config.yml           # 配置
├── env/                 # 渲染的文件
├── data/                # 容器数据
└── deploy-history.yml   # 历史
```

### 优势
1. **灵活部署** - 一份代码可管理多个环境
2. **数据安全** - 配置和数据独立于代码仓库
3. **升级简单** - 更新代码不影响数据
4. **备份容易** - 只需备份 root 目录

### 使用示例
```bash
# 虚拟环境在源码目录
cd /Users/zhumin/zhjx/edops
source venv/bin/activate

# 但数据在不同位置
edops --root ~/dev-env local launch
edops --root /opt/prod-env local launch
```

---

## 决策时间线

| 日期 | 决策 | 阶段 |
|------|------|------|
| 2024-12-04 | 构建策略：仅镜像管理 | 第 2 阶段规划 |
| 2024-12-04 | 配置策略：仅部署模式 | 第 2 阶段规划 |
| 2024-12-04 | 双命令支持 | 继承 Tutor 设计 |
| 2024-12-05 | 全面中文化 | 第 2 阶段实施 |

---

## 后续演进

这些设计决策并非一成不变，可根据实际使用反馈调整：

### 可能的演进方向
1. **构建支持** - 如果需要本地快速构建，可增加可选的构建功能
2. **多环境配置** - 如果团队规模扩大，可考虑引入环境配置文件
3. **多语言支持** - 如果有国际化需求，可使用 i18n 框架
4. **插件机制** - 扩展第三方集成能力

### 调整原则
- 保持简单性优先
- 避免过度设计
- 基于实际需求驱动
- 向后兼容

---

## 参考文档

- [EdOps 需求文档](../../edops 工具 — 简要需求文档.md)
- [实施总结](reports/IMPLEMENTATION_SUMMARY.md)
- [CLI 参考手册](edops-cli.md)
- [快速开始](../QUICKSTART_CN.md)

---

**最后更新**: 2024年12月5日  
**维护者**: EdOps 开发团队

