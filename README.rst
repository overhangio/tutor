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
2. 建议使用 Python ``3.10`` 以上版本，执行 ``pip install -e .``（或 ``hatch shell``）安装依赖。
3. 运行 ``edops --help`` 查看已有命令；目前仍会看到部分 Tutor 命令，后续会逐步替换。

目录结构速览
-------------

``tutor/`` 目录仍然保留 Tutor 的核心代码，我们会逐步重命名为 ``edops``。主要关注点：

``tutor/commands``  
    Typer CLI 命令，后续会增加 ``edops`` 专属子命令。
``tutor/templates``  
    Jinja 模板目录，`tutor/templates/edops/local/` 已包含 base/common/``zhjx-zlmediakit`` 的 Compose 模板。
``docs/``  
    后续迁移 edops 文档与使用示例，`docs/zhjx-modules.md` 用于记录模块变量需求，对应的元数据位于 `tutor/templates/config/edops-modules.yml`。

后续规划
--------

* 在 ``pyproject.toml`` 中完成包信息与依赖描述的迁移。
* 完成 base/common/``zhjx-zlmediakit`` 模块模板与配置注入。
* 增加 ``edops config save``、``edops local launch`` 的 zhjx 专属默认行为。
* 编写中文文档与示例，方便内部同事快速上手。
