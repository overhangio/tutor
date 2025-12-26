#! /bin/sh
# Set ownership for zhjx module data directories
# 
# 中间件服务 UID 分配：
# - RabbitMQ: UID 999 (rabbitmq user)
# - Redis: UID 999 (redis user, shared with RabbitMQ)
# - MinIO: UID 1000 (minio user)
# - Elasticsearch: UID 1000 (elasticsearch user, shared with MinIO)
# - Kafka: UID 1001 (bitnami kafka user)
# - KKFileView: UID 1000 (shared with MinIO/Elasticsearch)
# - ZLMediaKit: UID 1000 (shared with MinIO/Elasticsearch)
#
# 业务服务 UID 分配（预留，当前无数据目录）：
# - Spring Boot 微服务: UID 1000 (shared with MinIO/Elasticsearch)

# 中间件服务
setowner 999 /mounts/rabbitmq
setowner 999 /mounts/redis
setowner 1000 /mounts/minio
setowner 1000 /mounts/elasticsearch
setowner 1001 /mounts/kafka
setowner 1000 /mounts/kkfileview
{% if RUN_ZHJX_ZLMEDIAKIT %}setowner 1000 /mounts/zlmediakit/conf /mounts/zlmediakit/log /mounts/zlmediakit/www{% endif %}

# 业务服务数据目录（预留，当前未使用）
# 如果未来业务服务需要数据目录，取消注释并添加相应路径：
# setowner 1000 /mounts/business-services

{{ patch("local-docker-compose-permissions-zhjx-command") }}

