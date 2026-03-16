"""
API 文档对话框模块
点击按钮弹出大框框展示接口文档
"""

import flet as ft
from api.app import get_api_status


class ApiDocDialog:
    """API 文档对话框"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.dialog = None
    
    def show(self):
        """显示 API 文档对话框"""
        api_status = get_api_status()
        base_url = f"http://localhost:{api_status['port']}"
        
        # 创建文档内容 - 使用 TextField 来实现可选中复制
        doc_content = ft.Column(
            [
                # 标题和状态
                ft.Row(
                    [
                        ft.Text(
                            "API 接口文档",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "● 运行中" if api_status['running'] else "● 未启动",
                                color=ft.Colors.GREEN if api_status['running'] else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=ft.padding.only(left=20),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    f"基础地址: {base_url}",
                    size=14,
                    color=ft.Colors.BLUE,
                    selectable=True,
                ),
                ft.Divider(),
                
                # 接口列表
                self._create_api_section(
                    "GET /api/status",
                    "获取 API 服务状态",
                    "无",
                    '''{
    "success": true,
    "status": "running",
    "configured": true
}'''
                ),
                
                ft.Divider(),
                
                self._create_api_section(
                    "GET /api/config",
                    "获取当前配置",
                    "无",
                    '''{
    "success": true,
    "data": {
        "user_path": "C:\\Users\\...",
        "exe_path": "D:\\...\\ShadowBot.exe"
    }
}'''
                ),
                
                ft.Divider(),
                
                self._create_api_section(
                    "GET /api/robots",
                    "获取所有机器人列表",
                    "无",
                    '''{
    "success": true,
    "count": 22,
    "data": [
        {
            "uuid": "xxx-xxx",
            "name": "机器人名称",
            "version": "1.0",
            "author": "作者",
            "description": "描述"
        }
    ]
}'''
                ),
                
                ft.Divider(),
                
                self._create_api_section(
                    "GET /api/robot/{uuid}",
                    "获取指定机器人的详细信息",
                    "uuid: 机器人的 UUID",
                    '''{
    "success": true,
    "data": {
        "uuid": "xxx-xxx",
        "name": "机器人名称",
        "version": "1.0",
        "author": "作者",
        "description": "描述",
        "flow_count": 5,
        "command_count": 10
    }
}'''
                ),
                
                ft.Divider(),
                
                self._create_api_section(
                    "POST /api/robot/{uuid}/launch",
                    "启动指定机器人（最核心的接口！）",
                    "uuid: 机器人的 UUID",
                    '''{
    "success": true,
    "message": "机器人启动成功"
}'''
                ),
                
                ft.Divider(),
                
                self._create_api_section(
                    "GET /api/robots/search?name={keyword}",
                    "根据机器人名称模糊查询",
                    "name: 机器人名称关键字（支持模糊匹配，不区分大小写）",
                    '''{
    "success": true,
    "count": 2,
    "data": [
        {
            "uuid": "xxx-xxx",
            "name": "测试机器人A",
            "version": "1.0",
            "author": "作者",
            "description": "描述"
        },
        {
            "uuid": "yyy-yyy",
            "name": "测试机器人B",
            "version": "2.0",
            "author": "作者",
            "description": "描述"
        }
    ]
}'''
                ),
                
                ft.Divider(),
                
                # 调用示例
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "调用示例",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text("Python 示例:", weight=ft.FontWeight.BOLD),
                            ft.TextField(
                                value='''import requests

# 获取机器人列表
response = requests.get('http://localhost:16666/api/robots')
robots = response.json()

# 根据名称模糊查询
response = requests.get('http://localhost:16666/api/robots/search?name=测试')
robots = response.json()

# 启动机器人
uuid = robots['data'][0]['uuid']
response = requests.post(f'http://localhost:16666/api/robot/{uuid}/launch')
result = response.json()''',
                                multiline=True,
                                read_only=True,
                                min_lines=14,
                                max_lines=14,
                                text_size=12,
                                bgcolor=ft.Colors.GREY_100,
                                border_color=ft.Colors.TRANSPARENT,
                                expand=True,
                            ),
                            
                            ft.Text("cURL 示例:", weight=ft.FontWeight.BOLD),
                            ft.TextField(
                                value='''# 获取机器人列表
curl http://localhost:16666/api/robots

# 根据名称模糊查询
curl "http://localhost:16666/api/robots/search?name=测试"

# 启动机器人
curl -X POST http://localhost:16666/api/robot/{uuid}/launch''',
                                multiline=True,
                                read_only=True,
                                min_lines=5,
                                max_lines=5,
                                text_size=12,
                                bgcolor=ft.Colors.GREY_100,
                                border_color=ft.Colors.TRANSPARENT,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
        )
        
        # 创建对话框
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("API 接口文档"),
            content=ft.Container(
                content=doc_content,
                width=800,
                height=600,
                padding=20,
            ),
            actions=[
                ft.Button("关闭", on_click=self._on_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.show_dialog(self.dialog)
    
    def _create_api_section(self, endpoint: str, description: str, params: str, response: str) -> ft.Control:
        """创建 API 接口说明区块"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        endpoint,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                        selectable=True,
                    ),
                    ft.Text(description, size=14, selectable=True),
                    ft.Text(f"参数: {params}", size=12, color=ft.Colors.GREY_600, selectable=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("响应示例:", size=12, weight=ft.FontWeight.BOLD, selectable=True),
                                # 使用 TextField 来显示代码，方便复制
                                ft.TextField(
                                    value=response,
                                    multiline=True,
                                    read_only=True,
                                    min_lines=6,
                                    max_lines=6,
                                    text_size=11,
                                    bgcolor=ft.Colors.GREY_100,
                                    border_color=ft.Colors.TRANSPARENT,
                                    expand=True,
                                ),
                            ],
                            spacing=5,
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=5,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.only(bottom=10),
        )
    
    def _on_close(self, e):
        """关闭对话框"""
        if self.dialog:
            self.dialog.open = False
            self.dialog.update()
