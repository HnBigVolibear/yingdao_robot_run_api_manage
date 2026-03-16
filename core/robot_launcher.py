"""
机器人启动模块
负责生成和执行启动命令
"""

import os
import subprocess
import tempfile
import logging
import sys
import uuid
from pathlib import Path
from typing import Optional, Tuple

from core.config import config

# 配置日志输出到控制台
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class RobotLauncher:
    """机器人启动器"""
    
    def __init__(self):
        self.exe_path = config.get("exe_path", "")
    
    def generate_launch_command(self, robot_uuid: str) -> str:
        """生成启动命令"""
        exe_path = self.exe_path
        
        # 构建启动命令
        # 格式: start "" "ShadowBot.exe路径" shadowbot:Run?robot-uuid=UUID
        command = f'@echo off\nstart "" "{exe_path}" shadowbot:Run?robot-uuid={robot_uuid}'
        
        return command
    
    def launch(self, robot_uuid: str) -> Tuple[bool, str]:
        """启动机器人"""
        is_valid, errors = config.validate()
        if not is_valid:
            return False, f"配置错误: {'; '.join(errors)}"
        
        try:
            exe_path = config.get("exe_path")
            
            # 使用 os.startfile 启动，这是 Windows 启动文件的标准方式
            # 构建完整的 URL
            url = f'shadowbot:Run?robot-uuid={robot_uuid}'
            
            # 使用 os.startfile 启动
            os.startfile(exe_path, 'open', url)
            
            return True, "机器人启动成功"
            
        except Exception as e:
            logger.error(f"启动异常: {str(e)}")
            import traceback
            logger.error(f"异常堆栈:\n{traceback.format_exc()}")
            return False, f"启动失败: {str(e)}"
    
    def create_batch_file(self, robot_uuid: str, robot_name: str, output_dir: Optional[str] = None) -> Tuple[bool, str]:
        """创建批处理启动文件"""
        try:
            command = self.generate_launch_command(robot_uuid)
            
            # 清理文件名中的非法字符
            safe_name = "".join(c for c in robot_name if c.isalnum() or c in (' ', '_', '-')).strip()
            if not safe_name:
                safe_name = "robot"
            
            filename = f"启动_{safe_name}_{robot_uuid[:8]}.bat"
            
            # 确定输出目录
            if output_dir is None:
                output_dir = Path.home() / "Desktop"
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / filename
            
            # 写入批处理文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(command)
            
            return True, str(file_path)
            
        except Exception as e:
            return False, f"创建批处理文件失败: {str(e)}"
    
    def copy_launch_command(self, robot_uuid: str) -> str:
        """复制启动命令到剪贴板"""
        return self.generate_launch_command(robot_uuid)


# 全局启动器实例
launcher = RobotLauncher()
