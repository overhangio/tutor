# Nacos 配置管理抽象方案

## 概述

本文档描述如何在 EdOps 中对 zhjx 业务服务的 Nacos 配置进行抽象和模板化管理，确保不同环境部署的一致性。

## 当前状态

### 配置存储位置

Nacos 配置文件存储在：
```
zhjx-hub/稳定版本80-443/config/nacos-配置/nacos_config/DEFAULT_GROUP/
```

### 配置文件结构

1. **业务服务配置**：每个服务对应一个 YAML 文件
   - `ly-ac-tenant-svc.yaml`
   - `ly-ac-classroom-svc.yaml`
   - `ly-ac-user-svc.yaml`
   - ... (共 20+ 个服务)

2. **共享配置**：
   - `ly.yaml` - 全局共享配置
   - `ly-config.properties` - 属性配置
   - `gateway-route-config.json` - 网关路由配置
   - `sentinel-gateway.json` - Sentinel 配置

3. **特殊分组**：
   - `SEATA_GROUP/` - Seata 分布式事务配置

## 配置抽象设计

### 1. 配置变量分类

#### 1.1 基础设施变量（Infrastructure Variables）

这些变量在所有服务配置中通用：

```yaml
# 数据源配置
mysqlHost: ${mysqlHost}          # → EDOPS_MYSQL_HOST
mysqlPort: ${mysqlPort}            # → EDOPS_MYSQL_PORT
mysqlUser: ${mysqlUser}            # → EDOPS_MYSQL_ROOT_USER
mysqlPassword: ${mysqlPassword}    # → EDOPS_MYSQL_ROOT_PASSWORD

# Redis 配置
spring.redis.host: ${spring.redis.host}        # → EDOPS_REDIS_HOST
spring.redis.port: ${spring.redis.port}        # → EDOPS_REDIS_PORT
spring.redis.password: ${spring.redis.password} # → EDOPS_REDIS_PASSWORD
spring.redis.database: ${spring.redis.database} # → EDOPS_REDIS_DATABASE

# Nacos 发现配置
spring.cloud.nacos.discovery.ip: ${spring.application.name}
spring.cloud.nacos.discovery.port: 8080
spring.cloud.nacos.discovery.server-addr: ${serverAddr}  # → EDOPS_NACOS_SERVER_ADDR
```

#### 1.2 业务特定变量（Business Variables）

这些变量因服务而异，需要单独配置：

```yaml
# 邮件服务（SES）
sesEnabled: ${sesEnabled}
sesName: ${sesName}
sesEndPoint: ${sesEndPoint}
sesSecretId: ${sesSecretId}
sesSecretKey: ${sesSecretKey}
sesFromEmailAddress: ${sesFromEmailAddress}

# 短信服务（SMS）
smsEnabled: ${smsEnabled}
smsName: ${smsName}
smsAccessKey: ${smsAccessKey}
smsSecretKey: ${smsSecretKey}
smsSignName: ${smsSignName}

# MQTT 配置
mqttDashboardHost: ${mqttDashboardHost}
mqttDashboardAdmin: ${mqttDashboardAdmin}
mqttDashboardPassword: ${mqttDashboardPassword}
mqttDashboardPort: ${mqttDashboardPort}

# 第三方服务配置
reviewLinkAppKey: ${reviewLinkAppKey}
reviewLinkAppSecret: ${reviewLinkAppSecret}
reviewLinkAddress: ${reviewLinkAddress}
```

#### 1.3 安全敏感变量（Security Variables）

这些变量需要随机生成或从密钥管理服务获取：

```yaml
# 令牌密钥
ly.tenant.security.secret: ${EDOPS_TENANT_SECRET_KEY}  # 随机生成

# RSA 密钥对
tenant.system.public-key: ${EDOPS_TENANT_PUBLIC_KEY}
tenant.system.private-key: ${EDOPS_TENANT_PRIVATE_KEY}
```

### 2. 配置模板化方案

#### 2.1 模板目录结构

```
edops/tutor/templates/nacos/
├── DEFAULT_GROUP/
│   ├── services/
│   │   ├── ly-ac-tenant-svc.yml.j2      # 业务服务配置模板
│   │   ├── ly-ac-classroom-svc.yml.j2
│   │   └── ...
│   ├── shared/
│   │   ├── ly.yml.j2                    # 共享配置模板
│   │   ├── ly-config.properties.j2
│   │   └── gateway-route-config.json.j2
│   └── metadata.yml                     # 配置元数据
└── SEATA_GROUP/
    └── seataServer.properties.j2
```

#### 2.2 模板变量映射

在 `tutor/templates/config/defaults.yml` 中添加 Nacos 配置变量：

```yaml
# ----------------------------------------------------------------------------
# Nacos Configuration Variables
# ----------------------------------------------------------------------------
# Redis configuration for services
EDOPS_REDIS_DATABASE: 0

# Service-specific configuration
EDOPS_SES_ENABLED: false
EDOPS_SES_NAME: ""
EDOPS_SES_END_POINT: ""
EDOPS_SES_SECRET_ID: ""
EDOPS_SES_SECRET_KEY: ""
EDOPS_SES_FROM_EMAIL_ADDRESS: ""

EDOPS_SMS_ENABLED: false
EDOPS_SMS_NAME: ""
EDOPS_SMS_ACCESS_KEY: ""
EDOPS_SMS_SECRET_KEY: ""
EDOPS_SMS_SIGN_NAME: ""

# MQTT configuration
EDOPS_MQTT_DASHBOARD_HOST: "{{ EDOPS_EMQX_HOST }}"
EDOPS_MQTT_DASHBOARD_ADMIN: "admin"
EDOPS_MQTT_DASHBOARD_PASSWORD: ""
EDOPS_MQTT_DASHBOARD_PORT: "{{ EDOPS_EMQX_DASHBOARD_PORT }}"

# Third-party service configuration
EDOPS_REVIEW_LINK_APP_KEY: ""
EDOPS_REVIEW_LINK_APP_SECRET: ""
EDOPS_REVIEW_LINK_ADDRESS: ""
```

在 `tutor/templates/config/base.yml` 中添加安全变量：

```yaml
# Nacos security variables (randomly generated)
EDOPS_TENANT_SECRET_KEY: "{{ 64|random_string }}"
EDOPS_TENANT_PUBLIC_KEY: ""  # 从密钥管理服务获取或手动配置
EDOPS_TENANT_PRIVATE_KEY: ""  # 从密钥管理服务获取或手动配置
```

#### 2.3 配置模板示例

**业务服务配置模板** (`ly-ac-tenant-svc.yml.j2`):

```yaml
spring:
  application:
    name: ly-ac-tenant-svc
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://{{ EDOPS_MYSQL_HOST }}:{{ EDOPS_MYSQL_PORT }}/ly_ac_tenant_db?useUnicode=true&characterEncoding=UTF-8&useSSL=false&serverTimezone=Asia/Shanghai
    username: {{ EDOPS_MYSQL_ROOT_USER }}
    password: {{ EDOPS_MYSQL_ROOT_PASSWORD }}

logging:
  config: classpath:logback-tsf.xml

ses:
  enabled: {{ EDOPS_SES_ENABLED }}
  name: {{ EDOPS_SES_NAME }}
  endPoint: {{ EDOPS_SES_END_POINT }}
  secretId: {{ EDOPS_SES_SECRET_ID }}
  secretKey: {{ EDOPS_SES_SECRET_KEY }}
  fromEmailAddress: {{ EDOPS_SES_FROM_EMAIL_ADDRESS }}
  template-info-map:
    captcha:
      is-enable: {{ EDOPS_SES_CAPTCHA_IS_ENABLE }}
      template-id: {{ EDOPS_SES_CAPTCHA_TEMPLATE_ID }}
      template-data: {{ EDOPS_SES_CAPTCHA_TEMPLATE_DATA }}
      subject: {{ EDOPS_SES_CAPTCHA_SUBJECT }}

ly:
  tenant:
    tenant-mode: false
    security:
      header: Authorization
      secret: {{ EDOPS_TENANT_SECRET_KEY }}
      expireTime: 1440
      skipUrls:
        - /v1/hardware-product/list/entity
        - /v1/hardware-product/categories/list/entity
  loadbalancer:
    enabled: true
    prior-ip-pattern:
      - 100.64.*.*

tenant:
  prefix-initialize-link: {{ EDOPS_TENANT_PREFIX_INITIALIZE_LINK }}
  secure-key: UIuqNdAyioWvFdfr
  system:
    public-key: {{ EDOPS_TENANT_PUBLIC_KEY }}
    private-key: {{ EDOPS_TENANT_PRIVATE_KEY }}
```

**共享配置模板** (`ly.yml.j2`):

```yaml
# 全局共享配置
spring:
  redis:
    host: {{ EDOPS_REDIS_HOST }}
    port: {{ EDOPS_REDIS_PORT }}
    password: {{ EDOPS_REDIS_PASSWORD }}
    database: {{ EDOPS_REDIS_DATABASE }}

# 其他全局配置...
```

### 3. 配置注入机制

#### 3.1 配置渲染流程

```
1. 读取配置模板（.j2 文件）
   ↓
2. 加载 EdOps 配置（defaults.yml + config.yml + 环境变量）
   ↓
3. 渲染模板（Jinja2）
   ↓
4. 生成最终配置文件
   ↓
5. 通过 Nacos API 或配置文件导入到 Nacos
```

#### 3.2 配置注入命令

```bash
# 渲染所有 Nacos 配置
edops nacos config render

# 渲染特定服务的配置
edops nacos config render ly-ac-tenant-svc

# 将配置推送到 Nacos
edops nacos config push

# 从 Nacos 导出配置
edops nacos config export

# 验证配置
edops nacos config validate
```

### 4. 配置管理命令设计

#### 4.1 配置渲染命令

```python
@click.command(name="render", help="渲染 Nacos 配置模板")
@click.option("--service", help="指定服务名称（可选）")
@click.option("--output", help="输出目录（默认：env/nacos/config）")
@click.pass_obj
def nacos_config_render(context: Context, service: str, output: str) -> None:
    """
    渲染 Nacos 配置模板，将变量替换为实际值。
    """
    config = tutor_config.load(context.root)
    
    if service:
        # 渲染单个服务配置
        render_service_config(config, service, output)
    else:
        # 渲染所有配置
        render_all_configs(config, output)
```

#### 4.2 配置推送命令

```python
@click.command(name="push", help="推送配置到 Nacos")
@click.option("--service", help="指定服务名称（可选）")
@click.option("--group", default="DEFAULT_GROUP", help="Nacos 分组")
@click.option("--namespace", help="Nacos 命名空间（可选）")
@click.pass_obj
def nacos_config_push(context: Context, service: str, group: str, namespace: str) -> None:
    """
    将渲染后的配置推送到 Nacos 服务器。
    """
    config = tutor_config.load(context.root)
    nacos_client = get_nacos_client(config)
    
    if service:
        push_service_config(nacos_client, service, group, namespace)
    else:
        push_all_configs(nacos_client, group, namespace)
```

### 5. Nacos 客户端集成

#### 5.1 Nacos 客户端实现

```python
# tutor/edops/nacos_client.py

class NacosClient:
    def __init__(self, config: Config):
        self.server_addr = config.get("EDOPS_NACOS_SERVER_ADDR")
        self.username = config.get("EDOPS_NACOS_USER", "nacos")
        self.password = config.get("EDOPS_NACOS_PASSWORD")
        self.namespace = config.get("EDOPS_NACOS_NAMESPACE", "")
        
    def publish_config(
        self,
        data_id: str,
        group: str,
        content: str,
        config_type: str = "yaml"
    ) -> bool:
        """
        发布配置到 Nacos。
        """
        # 使用 Nacos Python SDK 或 HTTP API
        pass
    
    def get_config(
        self,
        data_id: str,
        group: str
    ) -> str:
        """
        从 Nacos 获取配置。
        """
        pass
    
    def delete_config(
        self,
        data_id: str,
        group: str
    ) -> bool:
        """
        删除 Nacos 配置。
        """
        pass
```

### 6. 配置元数据管理

#### 6.1 配置元数据文件

创建 `tutor/templates/nacos/metadata.yml` 定义配置元数据：

```yaml
services:
  ly-ac-tenant-svc:
    data_id: ly-ac-tenant-svc.yaml
    group: DEFAULT_GROUP
    template: services/ly-ac-tenant-svc.yml.j2
    variables:
      required:
        - EDOPS_MYSQL_HOST
        - EDOPS_MYSQL_PORT
        - EDOPS_MYSQL_ROOT_USER
        - EDOPS_MYSQL_ROOT_PASSWORD
      optional:
        - EDOPS_SES_ENABLED
        - EDOPS_SES_NAME
        - EDOPS_TENANT_SECRET_KEY
    dependencies: []
    
  ly-ac-classroom-svc:
    data_id: ly-ac-classroom-svc.yaml
    group: DEFAULT_GROUP
    template: services/ly-ac-classroom-svc.yml.j2
    variables:
      required:
        - EDOPS_MYSQL_HOST
        - EDOPS_REDIS_HOST
      optional:
        - EDOPS_REVIEW_LINK_APP_KEY
    dependencies: []

shared:
  ly:
    data_id: ly.yaml
    group: DEFAULT_GROUP
    template: shared/ly.yml.j2
    variables:
      required:
        - EDOPS_REDIS_HOST
        - EDOPS_REDIS_PORT
```

### 7. 环境差异处理

#### 7.1 环境特定配置

不同环境可以有不同的配置覆盖：

```yaml
# config/dev/nacos-overrides.yml
EDOPS_SES_ENABLED: false
EDOPS_SMS_ENABLED: false
EDOPS_SVC_PROFILE_ACTIVE: dev

# config/prod/nacos-overrides.yml
EDOPS_SES_ENABLED: true
EDOPS_SES_NAME: "prod-ses"
EDOPS_SMS_ENABLED: true
EDOPS_SVC_PROFILE_ACTIVE: prod
```

#### 7.2 配置优先级

```
1. 环境特定覆盖文件（最高优先级）
2. 用户 config.yml
3. defaults.yml（默认值）
4. base.yml（随机生成）
```

### 8. 配置验证

#### 8.1 配置验证规则

```python
def validate_nacos_config(config: Config, service: str) -> List[str]:
    """
    验证 Nacos 配置是否完整和有效。
    
    Returns:
        错误列表，空列表表示验证通过
    """
    errors = []
    metadata = load_nacos_metadata()
    service_meta = metadata.services.get(service)
    
    if not service_meta:
        return [f"服务 {service} 的元数据不存在"]
    
    # 检查必需变量
    for var in service_meta.variables.required:
        if not config.get(var):
            errors.append(f"必需配置项 {var} 未设置")
    
    # 验证配置值格式
    if config.get("EDOPS_MYSQL_PORT"):
        try:
            port = int(config.get("EDOPS_MYSQL_PORT"))
            if not (1 <= port <= 65535):
                errors.append(f"MySQL 端口 {port} 超出有效范围")
        except ValueError:
            errors.append("MySQL 端口必须是数字")
    
    return errors
```

### 9. 实施步骤

1. **创建模板目录结构**
   - 在 `tutor/templates/nacos/` 下创建模板文件
   - 将现有配置文件转换为 Jinja2 模板

2. **添加配置变量**
   - 在 `defaults.yml` 中添加 Nacos 相关配置变量
   - 在 `base.yml` 中添加安全变量（随机生成）

3. **实现 Nacos 客户端**
   - 创建 `tutor/edops/nacos_client.py`
   - 实现配置的增删改查功能

4. **实现配置管理命令**
   - `edops nacos config render` - 渲染配置
   - `edops nacos config push` - 推送配置
   - `edops nacos config export` - 导出配置
   - `edops nacos config validate` - 验证配置

5. **创建配置元数据**
   - 定义 `metadata.yml` 文件
   - 描述每个服务的配置需求

6. **集成到部署流程**
   - 在 `edops local launch` 中自动渲染和推送配置
   - 支持配置的增量更新

### 10. 优势

1. **统一管理**：所有 Nacos 配置通过 EdOps 统一管理
2. **环境一致性**：不同环境使用相同的模板，确保一致性
3. **版本控制**：配置模板纳入 Git 版本控制
4. **自动化**：配置渲染和推送自动化，减少人工错误
5. **可扩展**：易于添加新服务或修改现有配置

### 11. 注意事项

1. **敏感信息**：密码、密钥等敏感信息不应提交到 Git，应通过密钥管理服务或环境变量提供
2. **配置备份**：推送配置前应备份现有配置
3. **配置回滚**：支持配置回滚到之前的版本
4. **配置差异**：不同环境的配置差异应通过覆盖文件管理，而不是修改模板

## 实施状态

1. ✅ 创建 Nacos 配置模板目录结构
2. ✅ 将现有配置文件转换为 Jinja2 模板
3. ✅ 实现 Nacos 客户端
4. ✅ 实现配置管理命令
5. ⏳ 集成到部署流程（待完成）

## 使用示例

### 1. 渲染配置

```bash
# 渲染所有配置
edops nacos config render

# 渲染共享配置
edops nacos config render --shared

# 渲染特定服务配置
edops nacos config render --service ly-ac-user-svc

# 指定输出目录
edops nacos config render --output /tmp/nacos-config
```

### 2. 推送配置到 Nacos

```bash
# 推送所有配置
edops nacos config push

# 推送共享配置
edops nacos config push --shared

# 推送特定服务配置
edops nacos config push --service ly-ac-user-svc

# 指定配置源目录
edops nacos config push --source /tmp/nacos-config
```

### 3. 从 Nacos 导出配置

```bash
# 导出所有配置
edops nacos config export

# 指定输出目录
edops nacos config export --output /tmp/nacos-export
```

### 4. 验证配置

```bash
# 验证所有配置
edops nacos config validate

# 验证特定服务配置
edops nacos config validate --service ly-ac-user-svc
```

## 配置变量说明

### 必需配置变量

在 `defaults.yml` 中已定义默认值，但以下变量需要在 `config.yml` 或环境变量中设置：

- `EDOPS_NACOS_SERVER_ADDR`: Nacos 服务器地址（例如：`nacos:8848`）
- `EDOPS_NACOS_USER`: Nacos 用户名（默认：`nacos`）
- `EDOPS_NACOS_PASSWORD`: Nacos 密码（默认：`nacos`）
- `EDOPS_MYSQL_HOST`: MySQL 主机地址
- `EDOPS_MYSQL_PORT`: MySQL 端口
- `EDOPS_MYSQL_ROOT_USER`: MySQL root 用户
- `EDOPS_MYSQL_ROOT_PASSWORD`: MySQL root 密码
- `EDOPS_REDIS_HOST`: Redis 主机地址
- `EDOPS_REDIS_PORT`: Redis 端口
- `EDOPS_REDIS_PASSWORD`: Redis 密码
- `EDOPS_RABBITMQ_HOST`: RabbitMQ 主机地址
- `EDOPS_RABBITMQ_PORT`: RabbitMQ 端口
- `EDOPS_RABBITMQ_DEFAULT_USER`: RabbitMQ 用户名
- `EDOPS_RABBITMQ_DEFAULT_PASS`: RabbitMQ 密码

### 可选配置变量

以下变量可根据实际需求配置：

- 腾讯云相关配置（SMS、SES、验证码、直播等）
- CAS 配置
- 企微、钉钉配置
- 流媒体配置
- 其他第三方服务配置

详细列表请参考 `tutor/templates/config/defaults.yml` 中的 `Nacos Configuration Variables` 部分。

