from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

import importlib_resources

from tutor import exceptions, serialize
from tutor.types import Config, get_typed

MODULES_CONFIG_PATH = (
    importlib_resources.files("tutor") / "templates" / "config" / "edops-modules.yml"
)


@dataclass(frozen=True)
class ImageDef:
    """服务的镜像定义。"""

    name: str
    repository: str
    version_var: str


@dataclass(frozen=True)
class HealthCheckDef:
    """服务的健康检查定义。"""

    service: str
    type: str
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    timeout: int = 30


@dataclass(frozen=True)
class ModuleDef:
    name: str
    required: bool
    template: str
    target: str
    depends_on: List[str]
    health_checks: List[HealthCheckDef]
    images: List[ImageDef]


_MODULE_CACHE: Dict[str, ModuleDef] | None = None


def _load_modules() -> Dict[str, ModuleDef]:
    global _MODULE_CACHE
    if _MODULE_CACHE is not None:
        return _MODULE_CACHE
    raw = serialize.load(MODULES_CONFIG_PATH.read_text(encoding="utf-8"))
    modules_section = raw.get("modules", {})
    modules: Dict[str, ModuleDef] = {}
    for name, meta in modules_section.items():
        # 解析健康检查
        health_checks = []
        for hc in meta.get("health_checks", []):
            health_checks.append(
                HealthCheckDef(
                    service=hc["service"],
                    type=hc["type"],
                    url=hc.get("url"),
                    host=hc.get("host"),
                    port=hc.get("port"),
                    timeout=hc.get("timeout", 30),
                )
            )

        # 解析镜像
        images = []
        for img in meta.get("images", []):
            images.append(
                ImageDef(
                    name=img["name"],
                    repository=img["repository"],
                    version_var=img["version_var"],
                )
            )

        modules[name] = ModuleDef(
            name=name,
            required=bool(meta.get("required", False)),
            template=meta["template"],
            target=meta["target"],
            depends_on=list(meta.get("depends_on", [])),
            health_checks=health_checks,
            images=images,
        )
    _MODULE_CACHE = modules
    return modules


def _resolve_module_order(enabled: List[str]) -> List[str]:
    modules = _load_modules()
    ordered: List[str] = []
    visited: Set[str] = set()
    visiting: Set[str] = set()

    def add(name: str) -> None:
        if name in visited:
            return
        if name in visiting:
            raise exceptions.TutorError(
                f"Circular dependency detected in EdOps modules: '{name}'"
            )
        module = modules.get(name)
        if not module:
            raise exceptions.TutorError(f"Unknown EdOps module '{name}'")
        visiting.add(name)
        for dep in module.depends_on:
            add(dep)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)

    for module in modules.values():
        if module.required:
            add(module.name)
    for name in enabled:
        add(name)
    return ordered


def get_enabled_modules(config: Config) -> List[ModuleDef]:
    enabled = get_typed(config, "EDOPS_ENABLED_MODULES", list, [])
    order = _resolve_module_order(enabled)
    modules = _load_modules()
    return [modules[name] for name in order]


def get_enabled_module_targets(config: Config) -> List[str]:
    return [module.target for module in get_enabled_modules(config)]


def render_modules(root_env: str, config: Config) -> List[str]:
    """
    将已启用的模块模板渲染到环境中的目标路径。
    """
    modules = get_enabled_modules(config)
    if not modules:
        return []
    from tutor import env as tutor_env  # 延迟导入以避免循环依赖

    renderer = tutor_env.Renderer(config)
    rendered_paths: List[str] = []
    for module in modules:
        content = renderer.render_template(module.template)
        dst = os.path.join(root_env, module.target)
        tutor_env.write_to(content, dst)
        rendered_paths.append(dst)
    return rendered_paths


def get_module_images(module_name: str, config: Config) -> List[ImageDef]:
    """获取指定模块的所有镜像。"""
    modules = _load_modules()
    if module_name not in modules:
        return []
    return modules[module_name].images


def get_all_enabled_images(config: Config) -> List[tuple[str, ImageDef]]:
    """获取所有已启用模块的镜像及其模块名称。"""
    modules = get_enabled_modules(config)
    result = []
    for module in modules:
        for image in module.images:
            result.append((module.name, image))
    return result
