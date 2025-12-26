"""
Nacos 配置管理客户端。

提供与 Nacos 服务器交互的功能，包括配置的发布、获取、删除等操作。
"""

import base64
import typing as t
import urllib.parse

import requests

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions
from tutor import fmt


class NacosClient:
    """
    Nacos 配置管理客户端。

    提供配置的增删改查功能，支持通过 Nacos Open API 进行操作。
    """

    def __init__(self, config: tutor_config.Config):
        """
        初始化 Nacos 客户端。

        Args:
            config: EdOps 配置字典
        """
        self.server_addr = config.get("EDOPS_NACOS_SERVER_ADDR", "")
        if not self.server_addr:
            raise exceptions.TutorError(
                "未配置 Nacos 服务器地址。请设置 EDOPS_NACOS_SERVER_ADDR。"
            )

        # 移除协议前缀（如果有）
        if self.server_addr.startswith("http://") or self.server_addr.startswith(
            "https://"
        ):
            self.base_url = self.server_addr
        else:
            self.base_url = f"http://{self.server_addr}"

        self.username = config.get("EDOPS_NACOS_USER", "nacos")
        self.password = config.get("EDOPS_NACOS_PASSWORD", "nacos")
        self.namespace = config.get("EDOPS_NACOS_NAMESPACE", "")
        self.config = config

        # 获取访问令牌
        self._access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        """
        获取 Nacos 访问令牌。

        Returns:
            访问令牌字符串
        """
        url = f"{self.base_url}/nacos/v1/auth/login"
        params = {"username": self.username, "password": self.password}

        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("accessToken", "")
        except requests.exceptions.RequestException as e:
            raise exceptions.TutorError(
                f"无法连接到 Nacos 服务器 {self.base_url}: {e}"
            )
        except (KeyError, ValueError) as e:
            raise exceptions.TutorError(f"无法解析 Nacos 认证响应: {e}")

    def publish_config(
        self,
        data_id: str,
        group: str,
        content: str,
        config_type: str = "yaml",
    ) -> bool:
        """
        发布配置到 Nacos。

        Args:
            data_id: 配置 ID
            group: 配置分组（默认：DEFAULT_GROUP）
            content: 配置内容
            config_type: 配置类型（yaml、properties、json 等）

        Returns:
            是否发布成功
        """
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            "dataId": data_id,
            "group": group,
            "content": content,
            "type": config_type,
        }

        if self.namespace:
            params["tenant"] = self.namespace

        if self._access_token:
            params["accessToken"] = self._access_token

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            if response.text == "true":
                fmt.echo_info(f"配置已发布: {group}/{data_id}")
                return True
            else:
                fmt.echo_warning(
                    f"配置发布可能失败: {group}/{data_id}，响应: {response.text}"
                )
                return False
        except requests.exceptions.RequestException as e:
            fmt.echo_error(f"发布配置失败 {group}/{data_id}: {e}")
            return False

    def get_config(
        self,
        data_id: str,
        group: str,
    ) -> t.Optional[str]:
        """
        从 Nacos 获取配置。

        Args:
            data_id: 配置 ID
            group: 配置分组（默认：DEFAULT_GROUP）

        Returns:
            配置内容，如果不存在则返回 None
        """
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            "dataId": data_id,
            "group": group,
        }

        if self.namespace:
            params["tenant"] = self.namespace

        if self._access_token:
            params["accessToken"] = self._access_token

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            fmt.echo_error(f"获取配置失败 {group}/{data_id}: {e}")
            return None

    def delete_config(
        self,
        data_id: str,
        group: str,
    ) -> bool:
        """
        删除 Nacos 配置。

        Args:
            data_id: 配置 ID
            group: 配置分组（默认：DEFAULT_GROUP）

        Returns:
            是否删除成功
        """
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            "dataId": data_id,
            "group": group,
        }

        if self.namespace:
            params["tenant"] = self.namespace

        if self._access_token:
            params["accessToken"] = self._access_token

        try:
            response = requests.delete(url, params=params, timeout=10)
            response.raise_for_status()

            if response.text == "true":
                fmt.echo_info(f"配置已删除: {group}/{data_id}")
                return True
            else:
                fmt.echo_warning(
                    f"配置删除可能失败: {group}/{data_id}，响应: {response.text}"
                )
                return False
        except requests.exceptions.RequestException as e:
            fmt.echo_error(f"删除配置失败 {group}/{data_id}: {e}")
            return False

    def render_template(self, template_path: str) -> str:
        """
        渲染配置模板。

        Args:
            template_path: 模板路径（相对于 templates/nacos/）

        Returns:
            渲染后的配置内容
        """
        renderer = tutor_env.Renderer(self.config)
        return renderer.render_template(template_path)


def get_nacos_client(config: tutor_config.Config) -> NacosClient:
    """
    获取 Nacos 客户端实例。

    Args:
        config: EdOps 配置字典

    Returns:
        NacosClient 实例
    """
    return NacosClient(config)

