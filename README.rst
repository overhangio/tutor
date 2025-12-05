EdOps：面向 zhjx 体系的统一部署 CLI
===================================

EdOps 是在 `Tutor <https://github.com/overhangio/tutor>`__ 框架基础上二次开发的命令行工具，目标是把联奕智慧教学团队的 base/common/``zhjx-*`` 业务系统统一到一套配置、构建与部署流程里。它仍然沿用 Tutor 的 Typer CLI、模板渲染与插件机制，但默认能力全部面向混合教学、AI 督导、直播电商等业务场景。

目前我们聚焦以下三类工作：

* **命令体验迁移**：把 ``tutor`` 命令改造成 ``edops``，保留 ``config``、``local``、``dev``、``k8s`` 等核心子命令。
* **模板替换**：用 `zhjx-hub/稳定1panel版本/` 里的 Compose 模板替换 Open edX 相关模板，优先支持 base、common、``zhjx-zlmediakit``。
* **插件化模块**：把 ``zhjx-*`` 业务子系统抽象为插件（默认关闭），base/common 作为核心插件自动启用。

核心特性
--------

* **多环境统一**：沿用 Tutor 的 ``dev``、``local``、``k8s`` 三种模式，保证开发/单机/集群行为一致。
* **集中配置**：所有镜像版本、域名、数据库参数统一记录在 ``edops-config.yml``，支持按环境覆盖。
* **模块化控制**：base（nacos、mysql、minio、redis、MQ 等）和 common（用户、认证、后台、网关）始终启用，``zhjx-*`` 模块通过 ``EDOPS_ENABLED_MODULES`` 配置按需开启。
* **日志追溯**：继承 Tutor 的日志与命令输出体系，便于对每一次构建、部署、回滚进行审计。

快速开始
--------

1. 克隆本仓库并切换到 ``edops-main`` 分支。
2. 创建虚拟环境：``python3 -m venv venv && source venv/bin/activate``
3. 安装 EdOps：``pip install -e .``
4. 查看帮助：``edops --help``（全中文交互）
5. 详细指南：查看 ``QUICKSTART_CN.md``

文档导航
--------

**快速上手**
  ``QUICKSTART_CN.md``
    5 分钟快速开始指南

**参考文档**
  ``docs/edops-cli.md``
    完整的 CLI 命令参考手册
  ``docs/DESIGN_DECISIONS_CN.md``
    核心设计决策和技术共识
  ``docs/zhjx-modules.md``
    模块说明和配置

**报告归档**
  ``docs/reports/``
    实施报告、Bug 修复记录、测试指南等
  ``docs/reports/README.md``
    报告目录索引

目录结构
--------

``tutor/``
    核心代码（保留 tutor 目录名以兼容上游）
``tutor/commands/``
    CLI 命令实现（已中文化）
``tutor/edops/``
    EdOps 专属模块（健康检查、镜像管理、模块定义）
``tutor/templates/edops/``
    EdOps 部署模板（base/common/zhjx-* 模块）
``docs/``
    文档目录（参考文档和报告归档）
``tests/``
    单元测试

当前状态
--------

✅ **第 2 阶段已完成**（2024年12月5日）

* ✅ 镜像管理：查询、列表、版本管理
* ✅ 配置增强：get/list/validate/render 命令
* ✅ 部署增强：status/healthcheck/history/rollback 命令
* ✅ 健康检查：HTTP/TCP 自动检测
* ✅ 历史追踪：完整的操作审计
* ✅ 全面中文化：所有命令和消息
* ✅ 双命令支持：edops ≡ tutor

详见：``docs/reports/PHASE2_COMPLETION_CN.md``
