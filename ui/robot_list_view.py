"""
机器人列表视图模块
负责显示机器人列表和启动按钮
"""

import flet as ft
from typing import List, Callable

from core.robot_data import RobotInfo, RobotDataManager, create_mock_robots
from core.robot_launcher import launcher
from core.config import config


class RobotListView:
    """机器人列表视图"""
    
    def __init__(self, page: ft.Page, on_refresh=None):
        self.page = page
        self.on_refresh = on_refresh
        self.robot_manager: RobotDataManager = None
        self.robots: List[RobotInfo] = []
        self.list_view = None
        self.loading_indicator = None
        
    def build(self) -> ft.Control:
        """构建列表视图"""
        # 创建加载指示器
        self.loading_indicator = ft.ProgressRing(visible=False)
        
        # 创建列表视图
        self.list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )
        
        # 获取用户ID
        user_id = config.get_user_id()
        title_text = f"{user_id} 的机器人列表" if user_id else "机器人列表"
        
        # 标题文本（保存引用以便更新）
        self.title_text = ft.Text(
            title_text,
            size=24,
            weight=ft.FontWeight.BOLD,
        )
        
        # 返回主布局
        return ft.Column(
            [
                # 标题栏
                ft.Container(
                    content=ft.Row(
                        [
                            self.title_text,
                            ft.Row(
                                [
                                    self.loading_indicator,
                                    ft.Button(
                                        "刷新",
                                        icon=ft.Icons.REFRESH,
                                        on_click=self._on_refresh,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=20, right=20, top=20, bottom=10),
                ),
                
                # 列表区域
                ft.Container(
                    content=self.list_view,
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def load_robots(self):
        """加载机器人列表"""
        # 显示加载指示器
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            # 获取 apps 路径
            apps_path = config.get_apps_path()
            
            if apps_path:
                # 使用实际路径加载
                self.robot_manager = RobotDataManager(apps_path)
                self.robots = self.robot_manager.scan_robots()
            else:
                # 使用模拟数据
                self.robots = create_mock_robots(5)
            
            # 渲染列表
            self._render_robots()
            
        except Exception as e:
            self._show_error(f"加载机器人失败: {str(e)}")
        finally:
            # 隐藏加载指示器
            self.loading_indicator.visible = False
            self.page.update()
    
    def _render_robots(self):
        """渲染机器人列表"""
        self.list_view.controls.clear()
        
        if not self.robots:
            # 显示空状态
            self.list_view.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SMART_TOY_OUTLINED, size=64, color=ft.Colors.GREY_400),
                            ft.Text(
                                "暂无机器人",
                                size=18,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "请检查配置的路径是否正确",
                                size=14,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            # 渲染每个机器人卡片
            for robot in self.robots:
                card = self._create_robot_card(robot)
                self.list_view.controls.append(card)
        
        self.page.update()
    
    def _create_robot_card(self, robot: RobotInfo) -> ft.Control:
        """创建机器人卡片"""
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    robot.name,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"版本: {robot.version}",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                        ),
                                        ft.Text(
                                            f"作者: {robot.author}",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                    spacing=15,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"UUID: {robot.uuid}",
                                            size=12,
                                            color=ft.Colors.GREY_500,
                                            selectable=True,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.CONTENT_COPY,
                                            icon_size=14,
                                            icon_color=ft.Colors.GREY_500,
                                            tooltip="复制UUID",
                                            on_click=lambda e, uuid=robot.uuid: self._copy_uuid_sync(uuid),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                ft.Text(
                                    f"描述：{robot.description}" if robot.description else "描述：暂无",
                                    size=13,
                                    color=ft.Colors.GREY_700,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=5,
                            expand=True,
                        ),
                        
                        ft.Button(
                            "▶ 启动",
                            style=ft.ButtonStyle(
                                bgcolor={
                                    ft.ControlState.DEFAULT: ft.Colors.GREEN,
                                    ft.ControlState.HOVERED: ft.Colors.GREEN_700,
                                },
                                color=ft.Colors.WHITE,
                            ),
                            on_click=lambda e, r=robot: self._on_launch(r),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
            ),
            elevation=2,
        )
    
    def _copy_uuid_sync(self, uuid: str):
        """复制UUID到剪贴板（同步包装）"""
        import asyncio
        asyncio.create_task(self._copy_uuid(uuid))
    
    async def _copy_uuid(self, uuid: str):
        """复制UUID到剪贴板"""
        await ft.Clipboard().set(uuid)
        self._show_success("UUID已复制到剪贴板")
    
    def _on_launch(self, robot: RobotInfo):
        """启动机器人"""
        success, message = launcher.launch(robot.uuid)
        
        if success:
            self._show_success(f"机器人「{robot.name}」启动成功")
        else:
            self._show_error(message)
    
    def _on_refresh(self, e):
        """刷新列表"""
        self.load_robots()
        if self.on_refresh:
            self.on_refresh()
    
    def _show_error(self, message: str):
        """显示错误提示"""
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.RED_400,
            )
        )
    
    def _show_success(self, message: str):
        """显示成功提示"""
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.GREEN_400,
            )
        )
