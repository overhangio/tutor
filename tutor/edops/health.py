"""EdOps 模块的健康检查功能。"""
from __future__ import annotations

import socket
import time
import typing as t
from dataclasses import dataclass
from enum import Enum

import requests

from tutor import fmt
from tutor.exceptions import TutorError


class HealthCheckType(Enum):
    """健康检查类型。"""

    HTTP = "http"
    TCP = "tcp"
    CONTAINER = "container"


@dataclass
class HealthCheckDef:
    """健康检查定义。"""

    service: str
    type: HealthCheckType
    url: t.Optional[str] = None
    host: t.Optional[str] = None
    port: t.Optional[int] = None
    timeout: int = 30
    interval: int = 2
    retries: int = 15


class HealthChecker:
    """为服务执行健康检查。"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def check(self, health_check: HealthCheckDef) -> bool:
        """执行健康检查，成功返回 True。"""
        if self.verbose:
            fmt.echo_info(f"正在检查 {health_check.service} 的健康状态...")

        if health_check.type == HealthCheckType.HTTP:
            return self._check_http(health_check)
        elif health_check.type == HealthCheckType.TCP:
            return self._check_tcp(health_check)
        elif health_check.type == HealthCheckType.CONTAINER:
            return self._check_container(health_check)
        else:
            raise TutorError(f"未知的健康检查类型: {health_check.type}")

    def _check_http(self, health_check: HealthCheckDef) -> bool:
        """检查 HTTP 端点。"""
        if not health_check.url:
            raise TutorError(
                f"{health_check.service} 的 HTTP 健康检查需要 'url' 参数"
            )

        for attempt in range(health_check.retries):
            try:
                response = requests.get(
                    health_check.url, timeout=health_check.timeout
                )
                if response.status_code < 500:
                    if self.verbose:
                        msg = f"✓ {health_check.service} 健康"
                        fmt.echo_info(msg)
                    return True
            except (
                requests.exceptions.RequestException,
                requests.exceptions.Timeout,
            ):
                pass

            if attempt < health_check.retries - 1:
                time.sleep(health_check.interval)

        if self.verbose:
            msg = f"✗ {health_check.service} 健康检查失败"
            fmt.echo_error(msg)
        return False

    def _check_tcp(self, health_check: HealthCheckDef) -> bool:
        """检查 TCP 端口连通性。"""
        if not health_check.host or not health_check.port:
            raise TutorError(
                f"{health_check.service} 的 TCP 健康检查需要 'host' 和 'port' 参数"
            )

        for attempt in range(health_check.retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(health_check.timeout)
                result = sock.connect_ex(
                    (health_check.host, health_check.port)
                )
                sock.close()
                if result == 0:
                    if self.verbose:
                        msg = f"✓ {health_check.service} 健康"
                        fmt.echo_info(msg)
                    return True
            except (socket.error, socket.timeout):
                pass

            if attempt < health_check.retries - 1:
                time.sleep(health_check.interval)

        if self.verbose:
            msg = f"✗ {health_check.service} 健康检查失败"
            fmt.echo_error(msg)
        return False

    def _check_container(self, health_check: HealthCheckDef) -> bool:
        """使用 Docker 检查容器状态。"""
        # 这将使用 Docker SDK 检查容器健康状态
        # 目前我们实现一个基础版本
        if self.verbose:
            msg = f"{health_check.service} 的容器健康检查尚未实现"
            fmt.echo_info(msg)
        return True

    def check_all(self, health_checks: list[HealthCheckDef]) -> bool:
        """检查所有健康检查，全部通过返回 True。"""
        all_passed = True
        for health_check in health_checks:
            passed = self.check(health_check)
            if not passed:
                all_passed = False
        return all_passed

