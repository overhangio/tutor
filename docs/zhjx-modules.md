# zhjx 模块清单（首批）

本文件将 Tutor 的插件/模块概念映射到联奕智慧教学场景。具体元数据写入 `tutor/templates/config/edops-modules.yml`，供 `edops config` 与 `edops local render` 使用。配置项 `EDOPS_ENABLED_MODULES` 用于按需启用可选模块（默认仅加载所有 `required: true` 的模块）。首批目标模块：**base**、**common**、**zhjx-zlmediakit**。

> 补充：`1panel` 为单机 Docker 运维面板；`portainer` 用于多节点 / Swarm 集群。当前模板按 1panel（单机）编排，后续可为 portainer 模式新增模板。

## base（必选）
- **模板来源**：`tutor/templates/edops/local/zhjx-base.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-base.yaml`）
- **职责**：提供 nacos、mysql、redis、rabbitmq、minio、sentinel、emqx、kafka、elasticsearch、nginx、kkfileview 等基础组件。
- **依赖**：需在宿主机准备证书与 nginx 配置，默认指向 `/home/zhjx/*.crt/*.key`。
- **关键变量**
  - `MASTER_NODE_IP`：决定 nacos/mysql/minio 等服务对外地址。
  - `NACOS_DB_PASSWORD` / `MYSQL_ROOT_PASSWORD`
  - `PORTAL_CERT_PATH`：nginx 证书映射路径。
  - 镜像仓库 `IMAGE_REGISTRY`（默认为 `zhjx-images.tencentcloudcr.com`）。
- **edops 操作约束**：任何 `edops build/deploy` 均需先检查 base 是否健康；`edops rollback` 需提供镜像/数据备份策略。

## common（必选）
- **模板来源**：`tutor/templates/edops/local/zhjx-common.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-common.yaml`）
- **职责**：部署共享域服务（认证、用户、后台、网关、对象存储 API、基础数据等）以及 `ly-ac-console-ui` 前端。
- **依赖**：需依赖 base 中的 nacos/mysql；默认通过 `zhjx-network` 互通。
- **关键变量**
  - `IMAGE_REGISTRY`
  - `VERSION_UI_AUTH`、`VERSION_UI_CONSOLE`、`VERSION_SVC_DEFAULT`
  - `SCHOOL_ID`
  - `MASTER_NODE_IP`（用于拼接 `API_TENANT_URL`、`API_OBJECT_STORAGE_URL`）
- **edops 行为**：默认随 base 自动启用；后续将暴露 `edops config set common.version.svc` 等命令方便批量升级。

## zhjx-zlmediakit（可选）
- **模板来源**：`tutor/templates/edops/local/zhjx-zlmediakit.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-zlmediakit.yaml`）
- **职责**：部署 ZLMediaKit，用于 RTMP/RTSP/HTTP-FLV/HLS 等直播流接入。
- **依赖**：需要 `base` 网络，使用宿主机目录 `/home/zhjx/media` 保存配置、日志与静态资源。
- **关键变量**
  - `MEDIA_CONF_PATH`、`MEDIA_LOG_PATH`、`MEDIA_WEB_PATH`
  - 对外端口（默认 1935/8080/8443/554/10000/UDP 等）
- **edops 行为**：默认关闭，通过 `edops plugins enable zhjx-zlmediakit` 启用，并在部署前同步证书/配置。

> 说明：未来新增 `zhjx-sup`、`zhjx-ilive-ecom` 等模块时，沿用同一格式即可。待 `config/modules.yml` 引入后，edops 将根据 `required`、`depends_on` 属性自动处理部署顺序。
