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
                        DeployRecord.from_dict(r) for r in data.get("records", [])
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

        # 确定认证方法
        self.auth: t.Optional[t.Union[tuple[str, str], str]] = None
        if token:
            self.headers = {"Authorization": f"Bearer {token}"}
        elif username and password:
            self.auth = (username, password)
            self.headers = {}
        else:
            self.headers = {}

    def _get(self, path: str) -> requests.Response:
        """向仓库发起 GET 请求。"""
        url = f"https://{self.registry}/v2/{path}"
        try:
            if self.auth:
                response = requests.get(url, auth=self.auth, timeout=10)
            else:
                response = requests.get(url, headers=self.headers, timeout=10)
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


def get_registry_client(config: dict) -> RegistryClient:
    """从配置创建仓库客户端。"""
    registry = config.get("EDOPS_IMAGE_REGISTRY", "")
    if not registry:
        raise TutorError(
            "EDOPS_IMAGE_REGISTRY 未配置。请运行 'edops config save'"
        )

    # 尝试从环境变量或配置获取凭据
    token = os.getenv("EDOPS_IMAGE_REGISTRY_TOKEN") or config.get(
        "EDOPS_IMAGE_REGISTRY_TOKEN"
    )
    username = os.getenv("EDOPS_IMAGE_REGISTRY_USER") or config.get(
        "EDOPS_IMAGE_REGISTRY_USER"
    )
    password = os.getenv("EDOPS_IMAGE_REGISTRY_PASSWORD") or config.get(
        "EDOPS_IMAGE_REGISTRY_PASSWORD"
    )

    return RegistryClient(
        registry=registry,
        username=username,
        password=password,
        token=token,
    )
