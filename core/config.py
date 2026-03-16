"""
配置管理模块
负责配置的读取、保存和验证
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


def _get_config_dir() -> Path:
    """获取配置文件目录（用户 AppData 目录）"""
    # Windows: %APPDATA%/yingdao_robot_manager
    # 其他系统: ~/.yingdao_robot_manager
    if os.name == 'nt':
        # Windows 系统
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = Path(app_data) / "yingdao_robot_manager"
    else:
        # 其他系统
        config_dir = Path.home() / ".yingdao_robot_manager"
    
    return config_dir


class Config:
    """配置管理类"""
    
    CONFIG_FILE = _get_config_dir() / "config.json"
    
    DEFAULT_CONFIG = {
        "user_path": "",
        "exe_path": "",
        "last_updated": None
    }
    
    def __init__(self):
        self._config = self.DEFAULT_CONFIG.copy()
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._config.update(loaded_config)
        except Exception:
            pass
        return self._config.copy()
    
    def save(self) -> bool:
        """保存配置到文件"""
        try:
            self._ensure_config_dir()
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get(self, key: str, default=None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        self._config[key] = value
        return self.save()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置"""
        # 规范化用户路径（支持选择用户ID或apps文件夹）
        if "user_path" in updates:
            updates["user_path"] = self._normalize_user_path(updates["user_path"])
        
        self._config.update(updates)
        return self.save()
    
    def _normalize_user_path(self, path: str) -> str:
        """
        规范化用户路径
        支持两种情况：
        1. 选择到用户ID这一级: .../users/123456
        2. 选择到apps文件夹: .../users/123456/apps
        """
        if not path:
            return path
        
        path = path.strip()
        
        # 如果路径以 apps 结尾，提取父目录
        if path.endswith("\\apps") or path.endswith("/apps"):
            return str(Path(path).parent)
        
        return path
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(
            self._config.get("user_path") and 
            self._config.get("exe_path") and
            os.path.exists(self._config.get("user_path", "")) and
            os.path.exists(self._config.get("exe_path", ""))
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """验证配置是否完整"""
        errors = []
        
        user_path = self._config.get("user_path", "")
        exe_path = self._config.get("exe_path", "")
        
        if not user_path:
            errors.append("未配置影刀用户ID文件夹路径")
        elif not os.path.exists(user_path):
            errors.append(f"用户ID文件夹不存在: {user_path}")
        elif not os.path.exists(os.path.join(user_path, "apps")):
            errors.append(f"用户文件夹下未找到 apps 目录: {user_path}")
        
        if not exe_path:
            errors.append("未配置 ShadowBot.exe 路径")
        elif not os.path.exists(exe_path):
            errors.append(f"ShadowBot.exe 不存在: {exe_path}")
        elif not exe_path.lower().endswith("shadowbot.exe"):
            errors.append("可执行文件必须是 ShadowBot.exe")
        
        return len(errors) == 0, errors
    
    def get_apps_path(self) -> Optional[str]:
        """获取 apps 文件夹完整路径"""
        user_path = self._config.get("user_path")
        if user_path and os.path.exists(user_path):
            apps_path = os.path.join(user_path, "apps")
            if os.path.exists(apps_path):
                return apps_path
        return None
    
    def get_user_id(self) -> Optional[str]:
        """获取用户ID（从user_path路径中提取）"""
        user_path = self._config.get("user_path")
        if user_path:
            return Path(user_path).name
        return None
    
    def clear(self):
        """清除配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        if self.CONFIG_FILE.exists():
            self.CONFIG_FILE.unlink()


# 全局配置实例
config = Config()
