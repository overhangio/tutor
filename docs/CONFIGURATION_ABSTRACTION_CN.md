# EdOps 配置抽象方案

## 概述

本文档描述 EdOps 配置系统的抽象设计，参考 Open edX/Tutor 的配置管理方式，确保不同环境（dev/local/k8s）部署的一致性。

**相关文档**：
- [Nacos 配置管理方案](./NACOS_CONFIG_MANAGEMENT_CN.md) - 业务服务 Nacos 配置的抽象和模板化

## 配置层次结构

EdOps 配置系统采用三层抽象：

1. **基础配置（base.yml）**：包含随机生成的敏感信息（密码、密钥等）
2. **默认配置（defaults.yml）**：包含所有配置项的默认值，按功能模块组织
3. **用户配置（config.yml）**：用户自定义的配置覆盖值

### 配置加载顺序

```
base.yml (随机生成) 
  ↓
defaults.yml (默认值)
  ↓
config.yml (用户覆盖)
  ↓
环境变量 (TUTOR_* 或 EDOPS_*)
  ↓
最终配置
```

## 配置分类

### 1. 全局配置（Global）

#### 1.1 应用标识
- `EDOPS_APP_NAME`: 应用名称，默认为 "edops"
- `EDOPS_NETWORK_NAME`: Docker 网络名称，默认为 "zhjx-network"
- `EDOPS_BASE_PATH`: 基础路径，默认为 "/home/zhjx"
- `EDOPS_SCHOOL_ID`: 学校标识，默认为 "demo-school"

#### 1.2 镜像仓库
- `EDOPS_IMAGE_REGISTRY`: Docker 镜像仓库地址，默认为 "zhjx-images.tencentcloudcr.com"
- `EDOPS_IMAGE_REGISTRY_USER`: 仓库认证用户名（可选）
- `EDOPS_IMAGE_REGISTRY_PASSWORD`: 仓库认证密码（可选）
- `EDOPS_IMAGE_REGISTRY_TOKEN`: 仓库认证 Token（可选，优先级高于用户名密码）

#### 1.3 版本管理
- `EDOPS_VERSION_SVC_DEFAULT`: 默认业务服务版本，默认为 "latest"
- `EDOPS_VERSION_UI_AUTH`: 认证 UI 版本，默认为 "latest"
- `EDOPS_VERSION_UI_CONSOLE`: 管理控制台 UI 版本，默认为 "latest"

### 2. 基础设施配置（Infrastructure）

#### 2.1 网络配置
- `EDOPS_MASTER_NODE_IP`: 主节点 IP 地址，默认为 "127.0.0.1"
- `EDOPS_NETWORK_NAME`: Docker 网络名称（见全局配置）

#### 2.2 存储路径
- `EDOPS_BASE_PATH`: 基础存储路径（见全局配置）
- `EDOPS_NGINX_CONF`: Nginx 配置文件路径，默认为 "{{ EDOPS_BASE_PATH }}/nginx.conf"
- `EDOPS_CERT_KEY_FILE`: SSL 证书私钥路径，默认为 "{{ EDOPS_BASE_PATH }}/portal_ly-sky_com.key"
- `EDOPS_CERT_CRT_FILE`: SSL 证书文件路径，默认为 "{{ EDOPS_BASE_PATH }}/portal_ly-sky_com.crt"
- `EDOPS_MEDIA_CONF_PATH`: 媒体服务配置路径，默认为 "{{ EDOPS_BASE_PATH }}/media/conf"
- `EDOPS_MEDIA_LOG_PATH`: 媒体服务日志路径，默认为 "{{ EDOPS_BASE_PATH }}/media/log"
- `EDOPS_MEDIA_WEB_PATH`: 媒体服务 Web 路径，默认为 "{{ EDOPS_BASE_PATH }}/media/www"

### 3. 基础服务配置（Base Services）

#### 3.1 MySQL
- `EDOPS_MYSQL_ROOT_PASSWORD`: MySQL root 密码（随机生成，存储在 base.yml）
- `EDOPS_MYSQL_HOST`: MySQL 主机地址，默认为 "{{ EDOPS_MASTER_NODE_IP }}"
- `EDOPS_MYSQL_PORT`: MySQL 端口，默认为 3306
- `EDOPS_MYSQL_ROOT_USER`: MySQL root 用户名，默认为 "root"

#### 3.2 Redis
- `EDOPS_REDIS_HOST`: Redis 主机地址，默认为 "zhjx-redis"
- `EDOPS_REDIS_PORT`: Redis 端口，默认为 6379
- `EDOPS_REDIS_PASSWORD`: Redis 密码（可选）

#### 3.3 RabbitMQ
- `EDOPS_RABBITMQ_DEFAULT_USER`: RabbitMQ 默认用户名，默认为 "admin"
- `EDOPS_RABBITMQ_DEFAULT_PASS`: RabbitMQ 默认密码（随机生成，存储在 base.yml）
- `EDOPS_RABBITMQ_HOST`: RabbitMQ 主机地址，默认为 "zhjx-rabbitmq"
- `EDOPS_RABBITMQ_PORT`: RabbitMQ 端口，默认为 5672
- `EDOPS_RABBITMQ_MANAGEMENT_PORT`: RabbitMQ 管理端口，默认为 15672

#### 3.4 Nacos
- `EDOPS_NACOS_HOST`: Nacos 主机地址，默认为 "zhjx-nacos"
- `EDOPS_NACOS_PORT`: Nacos 端口，默认为 8848
- `EDOPS_NACOS_USER`: Nacos 用户名，默认为 "nacos"
- `EDOPS_NACOS_PASSWORD`: Nacos 密码（从 RabbitMQ 密码复用或单独配置）
- `EDOPS_NACOS_SERVER_ADDR`: Nacos 服务器地址，默认为 "http://zhjx-nacos:8848"
- `EDOPS_NACOS_NAMESPACE`: Nacos 命名空间（可选，用于多环境隔离）

**注意**：业务服务的 Nacos 配置管理请参考 [Nacos 配置管理方案](./NACOS_CONFIG_MANAGEMENT_CN.md)。

#### 3.5 MinIO
- `EDOPS_MINIO_ROOT_USER`: MinIO root 用户名，默认为 "admin"
- `EDOPS_MINIO_ROOT_PASSWORD`: MinIO root 密码（随机生成，存储在 base.yml）
- `EDOPS_MINIO_API_PORT`: MinIO API 端口，默认为 59000
- `EDOPS_MINIO_CONSOLE_PORT`: MinIO 控制台端口，默认为 59001
- `EDOPS_MINIO_HOST`: MinIO 主机地址，默认为 "zhjx-minio"
- `EDOPS_MINIO_SERVER_URL`: MinIO 服务器 URL，默认为 "http://{{ EDOPS_MASTER_NODE_IP }}:{{ EDOPS_MINIO_API_PORT }}"

#### 3.6 Elasticsearch
- `EDOPS_ELASTICSEARCH_HOST`: Elasticsearch 主机地址，默认为 "zhjx-elasticsearch"
- `EDOPS_ELASTICSEARCH_PORT`: Elasticsearch 端口，默认为 9200

#### 3.7 Kafka
- `EDOPS_KAFKA_HOST`: Kafka 主机地址，默认为 "zhjx-kafka"
- `EDOPS_KAFKA_PORT`: Kafka 端口，默认为 9092

#### 3.8 EMQX
- `EDOPS_EMQX_HOST`: EMQX 主机地址，默认为 "zhjx-emqx"
- `EDOPS_EMQX_MQTT_PORT`: EMQX MQTT 端口，默认为 1883
- `EDOPS_EMQX_WS_PORT`: EMQX WebSocket 端口，默认为 8083
- `EDOPS_EMQX_WSS_PORT`: EMQX WSS 端口，默认为 8084
- `EDOPS_EMQX_DASHBOARD_PORT`: EMQX 管理面板端口，默认为 18083

### 4. 业务服务配置（Business Services）

#### 4.1 API 网关
- `EDOPS_API_GATEWAY_URL`: API 网关 URL，默认为 "http://ly-ac-gateway-svc:50000"
- `EDOPS_API_GATEWAY_HOST`: API 网关主机地址，默认为 "ly-ac-gateway-svc"
- `EDOPS_API_GATEWAY_PORT`: API 网关端口，默认为 50000

#### 4.2 租户服务
- `EDOPS_API_TENANT_URL`: 租户服务 URL，默认为 "http://{{ EDOPS_MASTER_NODE_IP }}:{{ EDOPS_API_TENANT_PORT }}"
- `EDOPS_API_TENANT_PORT`: 租户服务端口，默认为 50004
- `EDOPS_API_TENANT_HOST`: 租户服务主机地址，默认为 "ly-ac-tenant-svc"

#### 4.3 对象存储服务
- `EDOPS_API_OBJECT_STORAGE_URL`: 对象存储服务 URL，默认为 "http://{{ EDOPS_MASTER_NODE_IP }}:{{ EDOPS_API_OBJECT_STORAGE_PORT }}"
- `EDOPS_API_OBJECT_STORAGE_PORT`: 对象存储服务端口，默认为 50007
- `EDOPS_API_OBJECT_STORAGE_HOST`: 对象存储服务主机地址，默认为 "ly-ac-object-storage-svc"

#### 4.4 业务服务通用配置
- `EDOPS_SVC_JVM_OPTS`: 业务服务 JVM 参数，默认为 "-Xms1G -Xmx2G -XX:MaxMetaspaceSize=256M -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp -XX:+UseStringDeduplication"
- `EDOPS_SVC_DISCOVERY`: 服务发现地址，默认为 "zhjx-nacos"
- `EDOPS_SVC_NACOS_GROUP`: Nacos 分组，默认为 "DEFAULT_GROUP"
- `EDOPS_SVC_PROFILE_ACTIVE`: Spring Profile，默认为 "dev"

### 5. 模块配置（Modules）

#### 5.1 模块启用
- `EDOPS_ENABLED_MODULES`: 启用的模块列表，默认为空数组 `[]`
  - 可选值：`zhjx_zlmediakit`, `zhjx_sup`, `zhjx_ilive_ecom`, `zhjx_media`, `zhjx_ykt`
  - `base` 和 `common` 模块始终启用，无需在此列表中

#### 5.2 媒体服务（zlmediakit）
- `EDOPS_ZLMEDIAKIT_IMAGE`: ZLMediaKit 镜像，默认为 "{{ EDOPS_IMAGE_REGISTRY }}/library/zlmediakit:master"
- `EDOPS_ZLMEDIAKIT_HOST`: ZLMediaKit 主机地址，默认为 "zlmediakit"
- `EDOPS_ZLMEDIAKIT_HTTP_PORT`: HTTP 端口，默认为 80
- `EDOPS_ZLMEDIAKIT_RTMP_PORT`: RTMP 端口，默认为 1935
- `EDOPS_ZLMEDIAKIT_RTSP_PORT`: RTSP 端口，默认为 554

### 6. 安全配置（Security）

#### 6.1 证书配置
- `EDOPS_CERT_KEY_FILE`: SSL 证书私钥路径（见基础设施配置）
- `EDOPS_CERT_CRT_FILE`: SSL 证书文件路径（见基础设施配置）
- `EDOPS_ENABLE_HTTPS`: 是否启用 HTTPS，默认为 false

#### 6.2 应用密钥
- `EDOPS_ISPOT_APP_SOURCE`: iSpot 应用密钥（随机生成，存储在 base.yml）

## 配置抽象原则

### 1. 环境无关性
所有配置项都应该通过变量引用，而不是硬编码。例如：
- ✅ `image: {{ EDOPS_IMAGE_REGISTRY }}/ly-sky.com/ly-ac-gateway-svc:{{ EDOPS_VERSION_SVC_DEFAULT }}`
- ❌ `image: zhjx-images.tencentcloudcr.com/ly-sky.com/ly-ac-gateway-svc:latest`

### 2. 分层抽象
- **基础设施层**：网络、存储、基础服务（MySQL、Redis、RabbitMQ 等）
- **业务服务层**：业务服务配置（网关、租户、对象存储等）
- **应用层**：UI 应用、版本管理

### 3. 默认值策略
- **安全敏感信息**：存储在 `base.yml`，随机生成
- **环境相关**：提供合理的默认值，可通过环境变量覆盖
- **业务相关**：提供默认值，但建议在 `config.yml` 中明确配置

### 4. 配置验证
- 必需配置项在启动时验证
- 提供配置验证命令：`edops config validate`

## 环境差异处理

### Dev 环境
- 使用本地开发镜像
- 端口映射到宿主机
- 启用调试模式

### Local 环境
- 使用生产镜像
- 标准端口配置
- 生产模式

### K8s 环境
- 使用 Kubernetes 资源定义
- 通过 ConfigMap 和 Secret 管理配置
- 支持多命名空间部署

## 配置迁移指南

### 从硬编码迁移到变量

**迁移前（zhjx-hub/稳定1panel版本/zhjx-common.yaml）：**
```yaml
services:
  ly-ac-gateway-svc:
    image: ${IMAGE_REGISTRY}/ly-sky.com/ly-ac-gateway-svc:${VERSION_SVC_DEFAULT}
    environment:
      mysqlHost: ${MASTER_NODE_IP}
      mysqlPassword: LianYi@123
```

**迁移后（edops/tutor/templates/edops/local/zhjx-common.yml）：**
```yaml
services:
  ly-ac-gateway-svc:
    image: {{ EDOPS_IMAGE_REGISTRY }}/ly-sky.com/ly-ac-gateway-svc:{{ EDOPS_VERSION_SVC_DEFAULT }}
    environment:
      mysqlHost: {{ EDOPS_MASTER_NODE_IP }}
      mysqlPassword: {{ EDOPS_MYSQL_ROOT_PASSWORD }}
```

### 变量命名规范

1. **前缀统一**：所有 EdOps 配置项使用 `EDOPS_` 前缀
2. **模块分组**：使用下划线分隔模块，如 `EDOPS_MYSQL_*`, `EDOPS_REDIS_*`
3. **语义清晰**：变量名应清晰表达其用途
4. **避免冲突**：不与 Tutor 核心配置项冲突

## 配置文档生成

配置文档应自动生成，包含：
- 配置项说明
- 默认值
- 环境变量覆盖方式
- 配置示例

## 配置使用示例

### 查看当前配置

```bash
# 查看所有 EdOps 配置
edops config list --filter EDOPS_

# 查看特定配置项
edops config get EDOPS_IMAGE_REGISTRY
edops config get EDOPS_MASTER_NODE_IP
```

### 设置配置值

```bash
# 设置单个配置项
edops config save --set EDOPS_IMAGE_REGISTRY=my-registry.com
edops config save --set EDOPS_MASTER_NODE_IP=192.168.1.100

# 设置多个配置项
edops config save --set EDOPS_IMAGE_REGISTRY=my-registry.com --set EDOPS_MASTER_NODE_IP=192.168.1.100
```

### 通过环境变量覆盖

```bash
# 使用环境变量（优先级高于 config.yml）
export EDOPS_IMAGE_REGISTRY=my-registry.com
export EDOPS_MASTER_NODE_IP=192.168.1.100

# 然后运行命令
edops local launch
```

### 不同环境的配置

#### 开发环境（dev）
```yaml
EDOPS_MASTER_NODE_IP: "127.0.0.1"
EDOPS_IMAGE_REGISTRY: "localhost:5000"
EDOPS_SVC_PROFILE_ACTIVE: "dev"
```

#### 生产环境（local/k8s）
```yaml
EDOPS_MASTER_NODE_IP: "192.168.1.100"
EDOPS_IMAGE_REGISTRY: "zhjx-images.tencentcloudcr.com"
EDOPS_SVC_PROFILE_ACTIVE: "prod"
```

## 配置验证

配置验证确保所有必需的配置项都已设置，并且值符合预期格式。

```bash
# 验证配置
edops config validate
```

验证规则：
- 必需配置项不能为空
- IP 地址格式验证
- 端口范围验证
- URL 格式验证

## 配置迁移检查清单

从硬编码迁移到变量化配置时，请检查：

- [ ] 所有镜像地址使用 `{{ EDOPS_IMAGE_REGISTRY }}` 变量
- [ ] 所有版本号使用版本变量（`{{ EDOPS_VERSION_* }}`）
- [ ] 所有 IP 地址使用 `{{ EDOPS_MASTER_NODE_IP }}` 变量
- [ ] 所有密码使用随机生成变量（`{{ EDOPS_*_PASSWORD }}`）
- [ ] 所有端口使用配置变量
- [ ] 所有路径使用 `{{ EDOPS_BASE_PATH }}` 相关变量
- [ ] 所有服务发现地址使用配置变量

## 已完成的工作

1. ✅ 分析现有配置变量，按功能模块分类
2. ✅ 设计配置抽象层次结构（全局配置、模块配置、环境覆盖）
3. ✅ 重构 defaults.yml，按模块组织配置变量
4. ✅ 创建配置文档，说明各配置项的用途和默认值
5. ⏳ 创建配置验证机制
6. ⏳ 确保 dev/local/k8s 环境配置一致性（通过变量抽象实现）

