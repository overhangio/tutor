"""EdOps 的镜像仓库管理。"""
from __future__ import annotations

import json
import os
import typing as t
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import requests

from tutor import fmt
from tutor.exceptions import TutorError


@dataclass
class DeployRecord:
    """部署操作记录。"""

    timestamp: str
    module: str
    service: str
    image: str
    tag: str
    operation: str  # deploy, rollback, restart

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DeployRecord":
        """从字典创建。"""
        return cls(**data)


class DeployHistory:
    """管理部署历史记录。"""

    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.records: list[DeployRecord] = []
        self._load()

    def _load(self) -> None:
        """从文件加载历史。"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.records = [
                        DeployRecord.from_dict(r)
                        for r in data.get("records", [])
                    ]
            except Exception as e:
                fmt.echo_error(f"加载部署历史失败: {e}")
                self.records = []

    def _save(self) -> None:
        """保存历史到文件。"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(
                {"records": [r.to_dict() for r in self.records]},
                f,
                indent=2
            )

    def add_record(
        self,
        module: str,
        service: str,
        image: str,
        tag: str,
        operation: str
    ) -> None:
        """添加新的部署记录。"""
        record = DeployRecord(
            timestamp=datetime.now().isoformat(),
            module=module,
            service=service,
            image=image,
            tag=tag,
            operation=operation,
        )
        self.records.append(record)
        self._save()

    def get_module_history(self, module: str) -> list[DeployRecord]:
        """获取指定模块的部署历史。"""
        return [r for r in self.records if r.module == module]

    def get_service_history(self, service: str) -> list[DeployRecord]:
        """获取指定服务的部署历史。"""
        return [r for r in self.records if r.service == service]

    def get_last_deployment(self, module: str) -> t.Optional[DeployRecord]:
        """获取模块的最后一次部署记录。"""
        module_records = self.get_module_history(module)
        if module_records:
            return module_records[-1]
        return None


class RegistryClient:
    """Docker Registry HTTP API V2 客户端。"""

    def __init__(
        self,
        registry: str,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        token: t.Optional[str] = None,
    ):
        self.registry = registry.rstrip("/")
        self.username = username
        self.password = password
        self.token = token
        self._cached_token: t.Optional[str] = None

        # 确定认证方法
        self.auth: t.Optional[t.Union[tuple[str, str], str]] = None
        if token:
            self._cached_token = token
            self.headers = {"Authorization": f"Bearer {token}"}
        elif username and password:
            self.auth = (username, password)
            self.headers = {}
        else:
            self.headers = {}

    def _get_token_from_auth_server(
        self, auth_server: str, service: str, scope: str
    ) -> str:
        """从认证服务器获取 token。"""
        import urllib.parse

        params = {
            "service": service,
            "scope": scope,
        }
        auth_url = f"{auth_server}?{urllib.parse.urlencode(params)}"

        try:
            # 尝试 GET 请求（标准 Docker Registry）
            response = requests.get(
                auth_url,
                auth=(self.username, self.password),
                timeout=10,
            )
            
            # 如果 GET 返回 405 或 400，尝试 POST（某些 Harbor/TCR 实现）
            if response.status_code in (400, 405):
                response = requests.post(
                    auth_url,
                    auth=(self.username, self.password),
                    timeout=10,
                )
            
            response.raise_for_status()
            data = response.json()
            
            # 支持不同的响应格式
            token = data.get("token") or data.get("access_token", "")
            if not token:
                raise TutorError(
                    f"认证服务器响应中未找到 token。"
                    f"响应: {data}"
                )
            
            return token
        except requests.exceptions.HTTPError as e:
            # 提供更详细的错误信息
            error_detail = ""
            try:
                error_detail = f" 响应内容: {e.response.text}"
            except Exception:
                pass
            raise TutorError(
                f"从认证服务器获取 token 失败: {e}{error_detail}"
            ) from e
        except Exception as e:
            raise TutorError(
                f"从认证服务器获取 token 失败: {e}"
            ) from e

    def _parse_www_authenticate(self, www_auth: str) -> dict:
        """解析 WWW-Authenticate 头。"""
        result = {}
        if not www_auth.startswith("Bearer "):
            return result

        # 解析 Bearer realm="...",service="...",scope="..."
        parts = www_auth[7:].split(",")
        for part in parts:
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                # 移除引号
                value = value.strip('"')
                result[key.strip()] = value

        return result

    def _get_token(self, repository: str, action: str = "pull") -> str:
        """获取访问指定 repository 的 token。"""
        # 先尝试无认证请求，获取 WWW-Authenticate 头
        url = f"https://{self.registry}/v2/{repository}/tags/list"
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.RequestException:
            # 如果请求失败，尝试使用 Basic Auth
            response = requests.get(url, auth=self.auth, timeout=10)

        if response.status_code != 401:
            # 如果不需要认证，返回空字符串
            return ""

        www_auth = response.headers.get("WWW-Authenticate", "")
        if not www_auth or "Bearer" not in www_auth:
            raise TutorError(
                "仓库返回了 401 错误，但未提供有效的认证信息。"
                f"响应: {response.text}"
            )

        # 解析 WWW-Authenticate 头
        auth_info = self._parse_www_authenticate(www_auth)
        realm = auth_info.get("realm", "")
        service = auth_info.get("service", self.registry)
        
        # 使用完整的 repository 路径作为 scope（腾讯云 TCR 需要）
        # scope 格式: repository:namespace/repo:action
        scope = f"repository:{repository}:{action}"
        
        # 如果 WWW-Authenticate 头中已经有 scope，使用它（可能包含多个 scope）
        if "scope" in auth_info:
            # 如果已有 scope，可能需要合并或使用原有的
            existing_scope = auth_info["scope"]
            # 检查是否需要添加我们的 scope
            if repository not in existing_scope:
                # 合并多个 scope（用空格分隔）
                scope = f"{existing_scope} repository:{repository}:{action}"
            else:
                scope = existing_scope

        if not realm:
            raise TutorError(
                "无法从 WWW-Authenticate 头中解析认证服务器地址。"
                f"WWW-Authenticate: {www_auth}"
            )

        if not self.username or not self.password:
            raise TutorError(
                "需要用户名和密码来获取 token，但未配置。"
                "请设置 EDOPS_IMAGE_REGISTRY_USER 和 "
                "EDOPS_IMAGE_REGISTRY_PASSWORD。"
            )

        # 从认证服务器获取 token
        return self._get_token_from_auth_server(realm, service, scope)

    def _get(self, path: str) -> requests.Response:
        """向仓库发起 GET 请求。"""
        url = f"https://{self.registry}/v2/{path}"
        try:
            # 如果已有 token，直接使用
            if self._cached_token:
                headers = {"Authorization": f"Bearer {self._cached_token}"}
                response = requests.get(url, headers=headers, timeout=10)
            elif self.auth:
                # 使用 Basic Auth
                response = requests.get(url, auth=self.auth, timeout=10)
            elif self.headers:
                # 使用 Token Auth
                response = requests.get(url, headers=self.headers, timeout=10)
            else:
                # 无认证
                response = requests.get(url, timeout=10)

            # 如果返回 401，尝试获取 token
            if response.status_code == 401:
                www_auth = response.headers.get("WWW-Authenticate", "")
                if (
                    "Bearer" in www_auth
                    and self.auth
                    and not self._cached_token
                ):
                    # 从 path 中提取完整的 repository 名称
                    # path 格式通常是:
                    # repository/tags/list 或 repository/manifests/tag
                    # 对于腾讯云 TCR，repository 可能是 ly-sky.com/ly-ac-gateway-svc
                    # 需要移除最后的 /tags/list 或 /manifests/tag 部分
                    repository = path
                    if "/tags/list" in repository:
                        repository = repository.replace("/tags/list", "")
                    elif "/manifests/" in repository:
                        # 移除 /manifests/tag 部分
                        repository = repository.rsplit("/manifests/", 1)[0]
                    # 获取 token
                    try:
                        self._cached_token = self._get_token(repository)
                        # 使用新获取的 token 重试请求
                        auth_header = (
                            f"Bearer {self._cached_token}"
                        )
                        headers = {"Authorization": auth_header}
                        response = requests.get(
                            url, headers=headers, timeout=10
                        )
                    except Exception as e:
                        raise TutorError(
                            f"获取认证 token 失败: {e}"
                        ) from e

            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise TutorError(f"仓库 API 请求失败: {e}") from e

    def list_tags(self, repository: str) -> list[str]:
        """列出仓库的所有标签。"""
        try:
            response = self._get(f"{repository}/tags/list")
            data = response.json()
            return data.get("tags", [])
        except Exception as e:
            fmt.echo_error(
                f"列出 {repository} 的标签失败: {e}"
            )
            return []

    def get_manifest(
        self, repository: str, tag: str
    ) -> t.Optional[dict]:
        """获取指定镜像标签的 manifest。"""
        try:
            response = self._get(f"{repository}/manifests/{tag}")
            return response.json()
        except Exception as e:
            fmt.echo_error(
                f"获取 {repository}:{tag} 的 manifest 失败: {e}"
            )
            return None


def resolve_repository_path(config: dict, service_name: str) -> str:
    """
    从服务名解析完整的 repository 路径。

    首先尝试从模块元数据中查找，如果找不到则直接使用服务名。

    Args:
        config: EdOps 配置字典
        service_name: 服务名称（如 ly-ac-gateway-svc）

    Returns:
        完整的 repository 路径（如 ly-sky.com/ly-ac-gateway-svc）
    """
    from tutor.edops import modules as edops_modules
    from tutor import env as tutor_env

    # 从模块元数据中查找
    modules_list = edops_modules.get_enabled_modules(config)
    for module in modules_list:
        for image in module.images:
            if image.name == service_name:
                # 渲染 repository 路径
                full_repo = tutor_env.render_str(config, image.repository)
                # 移除 registry 前缀，只保留 repository 路径
                registry = config.get("EDOPS_IMAGE_REGISTRY", "")
                if registry and full_repo.startswith(f"{registry}/"):
                    return full_repo[len(f"{registry}/"):]
                return full_repo

    # 如果找不到，直接使用服务名（向后兼容）
    return service_name


def get_registry_client(config: dict) -> RegistryClient:
    """从配置创建仓库客户端。"""
    registry = config.get("EDOPS_IMAGE_REGISTRY", "")
    if not registry:
        raise TutorError(
            "EDOPS_IMAGE_REGISTRY 未配置。请运行 'edops config save'"
        )

    # 尝试从环境变量或配置获取凭据（环境变量优先）
    token = os.getenv("EDOPS_IMAGE_REGISTRY_TOKEN") or config.get(
        "EDOPS_IMAGE_REGISTRY_TOKEN"
    )
    username = os.getenv("EDOPS_IMAGE_REGISTRY_USER") or config.get(
        "EDOPS_IMAGE_REGISTRY_USER"
    )
    password = os.getenv("EDOPS_IMAGE_REGISTRY_PASSWORD") or config.get(
        "EDOPS_IMAGE_REGISTRY_PASSWORD"
    )

    # 调试信息：检查是否获取到认证信息
    if not username and not token:
        fmt.echo_warning(
            "未配置镜像仓库认证信息。"
            "请设置 EDOPS_IMAGE_REGISTRY_USER 和 EDOPS_IMAGE_REGISTRY_PASSWORD，"
            "或设置 EDOPS_IMAGE_REGISTRY_TOKEN。"
        )

    return RegistryClient(
        registry=registry,
        username=username,
        password=password,
        token=token,
    )
