"""
机器人数据模块
负责扫描文件夹、读取和解析机器人信息
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class RobotInfo:
    """机器人信息数据类"""
    uuid: str
    name: str
    version: str
    description: str
    author: str = "未知"
    main: str = ""
    modified_time: datetime = None # type: ignore
    raw_data: Dict[str, Any] = field(default_factory=dict)


class RobotDataManager:
    """机器人数据管理器"""
    
    def __init__(self, apps_path: str):
        self.apps_path = apps_path
        self.robots: List[RobotInfo] = []
    
    def scan_robots(self) -> List[RobotInfo]:
        """扫描机器人列表"""
        self.robots = []
        
        if not self.apps_path or not os.path.exists(self.apps_path):
            return self.robots
        
        try:
            for item in os.listdir(self.apps_path):
                if item.endswith("_temp"):
                    continue
                
                item_path = os.path.join(self.apps_path, item)
                
                if os.path.isdir(item_path):
                    robot_info = self._read_robot_info(item, item_path)
                    if robot_info:
                        self.robots.append(robot_info)
            
            self.robots.sort(key=lambda r: r.modified_time or datetime.min, reverse=True)
            
        except Exception:
            pass
        
        return self.robots
    
    def _read_robot_info(self, uuid: str, robot_dir: str) -> Optional[RobotInfo]:
        """读取单个机器人的信息"""
        xbot_robot_path = os.path.join(robot_dir, "xbot_robot")
        modified_time = None
        
        if os.path.exists(xbot_robot_path):
            try:
                modified_time = datetime.fromtimestamp(os.path.getmtime(xbot_robot_path))
            except Exception:
                pass
        
        package_paths = [
            os.path.join(robot_dir, "xbot_robot", "package.json"),
            os.path.join(robot_dir, "package.json"),
            os.path.join(robot_dir, "robot.json"),
            os.path.join(robot_dir, "config.json"),
        ]
        
        for package_path in package_paths:
            if os.path.exists(package_path):
                try:
                    with open(package_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return self._parse_robot_info(uuid, data, modified_time)
                except Exception:
                    continue
        
        return RobotInfo(
            uuid=uuid,
            name=uuid,
            version="未知",
            description="无法读取机器人详细信息",
            modified_time=modified_time
        )
    
    def _parse_robot_info(self, uuid: str, data: Dict[str, Any], modified_time: datetime = None) -> RobotInfo:
        """解析机器人信息"""
        return RobotInfo(
            uuid=uuid,
            name=data.get("name", uuid),
            version=data.get("version", "1.0.0"),
            description=data.get("description", "暂无描述"),
            author=data.get("author", "未知"),
            main=data.get("main", ""),
            modified_time=modified_time,
            raw_data=data
        )
    
    def get_robot_by_uuid(self, uuid: str) -> Optional[RobotInfo]:
        """通过 UUID 获取机器人信息"""
        for robot in self.robots:
            if robot.uuid == uuid:
                return robot
        return None
    
    def get_robots_count(self) -> int:
        """获取机器人数量"""
        return len(self.robots)


def create_mock_robots(count: int = 5) -> List[RobotInfo]:
    """创建模拟数据（用于演示）"""
    mock_data = [
        {
            "uuid": "3d1c3cc8-a4e4-48c4-984f-61be9e94a031",
            "name": "演示-数据采集机器人",
            "version": "2.1.0",
            "description": "自动采集网页数据并导出到Excel",
            "author": "张三",
            "modified_time": datetime(2024, 1, 15, 10, 30, 0)
        },
        {
            "uuid": "8f5e2b9c-1d3a-4e6b-9c8d-2a4b6c8d0e2f",
            "name": "演示-报表生成机器人",
            "version": "1.5.2",
            "description": "每日自动生成业务报表并发送邮件",
            "author": "李四",
            "modified_time": datetime(2024, 1, 20, 14, 45, 0)
        },
        {
            "uuid": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
            "name": "演示-文件整理机器人",
            "version": "1.0.0",
            "description": "自动整理和归档文件",
            "author": "赵六",
            "modified_time": datetime(2024, 1, 10, 16, 0, 0)
        }
    ]
    
    robots = []
    for item in mock_data[:count]:
        robots.append(RobotInfo(
            uuid=item["uuid"],
            name=item["name"],
            version=item["version"],
            description=item["description"],
            author=item["author"],
            main="main.xbot",
            modified_time=item["modified_time"]
        ))
    
    robots.sort(key=lambda r: r.modified_time or datetime.min, reverse=True)
    
    return robots
