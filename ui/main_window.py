"""
主窗口模块
负责整合所有UI组件
"""

import flet as ft
import os
from pathlib import Path

from core.config import config
from .config_dialog import ConfigDialog
from .robot_list_view import RobotListView
from .api_doc_dialog import ApiDocDialog
from api.app import start_api_server, stop_api_server, get_api_status


class MainWindow:
    """主窗口"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.config_dialog = None
        self.api_doc_dialog = None
        self.robot_list_view = None
        self.api_status_text = None
        
        self._setup_page()
        self._build_ui()
        self._check_config()
        self._start_api()
    
    def _setup_page(self):
        """设置页面属性"""
        self.page.title = "影刀RPA机器人管理调度系统"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 500
    
    def _build_ui(self):
        """构建UI"""
        self.robot_list_view = RobotListView(
            self.page,
            on_refresh=self._on_refresh,
        )
        
        self.api_status_text = ft.Text(
            "API 服务: 未启动",
            size=12,
            color=ft.Colors.GREY_600,
        )
        
        # 作者信息（左上角）- 美化版
        # 获取头像路径
        avatar_path = Path(__file__).parent.parent / "bear.ico"
        
        # 头像图片组件
        self.avatar_image = ft.Image(
            src=str(avatar_path),
            width=40,
            height=40,
            fit=ft.BoxFit.COVER,
            border_radius=ft.border_radius.all(20),
        )
        
        # GitHub 按钮（先创建，后面引用）
        self._github_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.OPEN_IN_NEW,
                        size=14,
                        color=ft.Colors.WHITE70,
                    ),
                    ft.Text(
                        "GitHub",
                        size=10,
                        color=ft.Colors.WHITE70,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=3,
                tight=True,
            ),
            on_click=lambda e: self._open_github(),
            on_hover=self._on_github_hover,
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=ft.border_radius.all(6),
            padding=ft.padding.only(left=6, right=6, top=3, bottom=3),
        )
        
        # 头像外层容器（保存引用以便悬停时修改）
        self.avatar_container = ft.Container(
            content=self.avatar_image,
            width=40,
            height=40,
            border_radius=ft.border_radius.all(20),
            bgcolor=ft.Colors.WHITE,
            padding=2,
            border=ft.border.all(2, ft.Colors.GREY_300),
            on_click=lambda e: self._show_sponsor_dialog(),
            on_hover=self._on_avatar_hover,
        )
        
        author_info = ft.Container(
            content=ft.Row(
                [
                    # 圆形头像带边框
                    self.avatar_container,
                    # 作者信息
                    ft.Column(
                        [
                            # 作者名称
                            ft.Text(
                                "湖南大白熊",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                no_wrap=True,
                            ),
                            # 身份和GitHub
                            ft.Row(
                                [
                                    ft.Text(
                                        "影刀RPA高级开发者",
                                        size=10,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                                    ),
                                    ft.Container(
                                        content=ft.Text("·", size=10, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                                        padding=ft.padding.only(left=2, right=2),
                                    ),
                                    # GitHub 按钮
                                    self._github_button,
                                ],
                                spacing=0,
                                tight=True,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=3,
                        tight=True,
                    ),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=12, right=15),
        )
        
        # 右上角按钮组
        action_buttons = ft.Row(
            [
                ft.Button(
                    "接口文档",
                    icon=ft.Icons.DESCRIPTION,
                    on_click=self._on_api_doc_click,
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="配置",
                    on_click=self._on_config_click,
                ),
            ],
            spacing=10,
        )
        
        # 自定义顶部栏（替代 AppBar，支持交互）
        custom_appbar = ft.Container(
            content=ft.Row(
                [
                    author_info,
                    ft.Container(
                        content=ft.Text(
                            "影刀RPA机器人管理调度系统",
                            size=18,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        expand=True,
                    ),
                    ft.Container(
                        content=self.api_status_text,
                        padding=ft.padding.only(left=10, right=10),
                    ),
                    ft.Container(
                        content=action_buttons,
                        padding=ft.padding.only(right=10),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE,
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
        )
        
        # 主内容区域 - 直接显示机器人列表
        self.content_area = ft.Container(
            content=self.robot_list_view.build(),
            expand=True,
            padding=10,
        )
        
        # 使用 Column 布局，顶部栏 + 内容区域
        main_layout = ft.Column(
            [
                custom_appbar,
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
        
        # 直接添加主布局
        self.page.add(main_layout)
    
    def _check_config(self):
        """检查配置"""
        if not config.is_configured():
            self._show_config_dialog(is_first_time=True)
        else:
            self.robot_list_view.load_robots()
    
    def _show_config_dialog(self, is_first_time=False):
        """显示配置对话框"""
        self.config_dialog = ConfigDialog(
            self.page,
            on_config_saved=self._on_config_saved,
        )
        self.config_dialog.show(is_first_time=is_first_time)
    
    def _on_config_click(self, e):
        """配置按钮点击"""
        self._show_config_dialog(is_first_time=False)
    
    def _on_config_saved(self):
        """配置保存后的回调"""
        if self.robot_list_view:
            self.robot_list_view.load_robots()
    
    def _on_api_doc_click(self, e):
        """接口文档按钮点击"""
        self.api_doc_dialog = ApiDocDialog(self.page)
        self.api_doc_dialog.show()
    
    def _on_refresh(self):
        """刷新回调"""
        pass
    
    def _on_avatar_hover(self, e):
        """头像悬停效果"""
        if e.data == True or e.data == "true":
            # 悬停时边框变蓝色，背景变亮
            self.avatar_container.border = ft.border.all(3, ft.Colors.BLUE)
            self.avatar_container.bgcolor = ft.Colors.BLUE_50
        else:
            # 恢复原始边框
            self.avatar_container.border = ft.border.all(2, ft.Colors.GREY_300)
            self.avatar_container.bgcolor = ft.Colors.WHITE
        self.avatar_container.update()
    
    def _show_sponsor_dialog(self):
        """显示收款码对话框"""
        sponsor_path = Path(__file__).parent.parent / "sponsor.png"
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("支持作者", text_align=ft.TextAlign.CENTER),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "感谢您的支持！",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Container(height=10),
                        ft.Image(
                            src=str(sponsor_path),
                            width=300,
                            height=300,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "扫码捐赠支持开发者",
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            actions=[
                ft.Button("关闭", on_click=lambda e: self._close_dialog(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.show_dialog(dialog)
        self._current_dialog = dialog
    
    def _close_dialog(self, e):
        """关闭对话框"""
        if hasattr(self, '_current_dialog') and self._current_dialog:
            self._current_dialog.open = False
            self._current_dialog.update()
    
    def _on_github_hover(self, e):
        """GitHub按钮悬停效果"""
        if e.data == True or e.data == "true":
            # 悬停时背景变亮，文字变白
            e.control.bgcolor = ft.Colors.BLUE_300
            e.control.content.controls[0].color = ft.Colors.WHITE
            e.control.content.controls[1].color = ft.Colors.WHITE
        else:
            # 恢复原始状态
            e.control.bgcolor = ft.Colors.TRANSPARENT
            e.control.content.controls[0].color = ft.Colors.WHITE70
            e.control.content.controls[1].color = ft.Colors.WHITE70
        e.control.update()
    
    def _open_github(self):
        """打开GitHub主页"""
        import webbrowser
        webbrowser.open("https://github.com/HnBigVolibear")
    
    def _start_api(self):
        """启动 API 服务"""
        if start_api_server(port=16666):
            self.api_status_text.value = "API 服务: 运行中 (端口 16666)"
            self.api_status_text.color = ft.Colors.YELLOW
        else:
            self.api_status_text.value = "API 服务: 启动失败"
            self.api_status_text.color = ft.Colors.RED
        self.page.update()


def main(page: ft.Page):
    """应用入口"""
    MainWindow(page)


if __name__ == "__main__":
    ft.run(main)
