"""
配置对话框UI模块
负责首次配置和路径设置界面
"""

import flet as ft
from pathlib import Path

from core.config import config


class ConfigDialog:
    """配置对话框"""
    
    def __init__(self, page: ft.Page, on_config_saved=None):
        self.page = page
        self.on_config_saved = on_config_saved
        self.dialog = None
        self.user_path_field = None
        self.exe_path_field = None
        
    def show(self, is_first_time=False):
        """显示配置对话框"""
        current_user_path = config.get("user_path", "")
        current_exe_path = config.get("exe_path", "")
        
        self.user_path_field = ft.TextField(
            label="影刀用户ID文件夹路径",
            value=current_user_path,
            hint_text=r"例如: C:\...\users\64************74",
            expand=True,
        )
        
        self.exe_path_field = ft.TextField(
            label="ShadowBot.exe 路径",
            value=current_exe_path,
            hint_text=r"例如: D:\Program Files (x86)\ShadowBot\ShadowBot.exe",
            expand=True,
        )
        
        content = ft.Column(
            [
                ft.Text(
                    "欢迎使用影刀RPA机器人管理调度系统" if is_first_time else "配置影刀路径",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "请配置以下路径以开始使用：" if is_first_time else "修改配置：",
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
                ft.Divider(),
                
                ft.Column(
                    [
                        ft.Text("1. 影刀用户ID文件夹路径", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "可以选择用户ID目录或其下的apps文件夹",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "• 例如: C:\\Users\\Administrator\\AppData\\Local\\ShadowBot\\users\\64******74",
                            size=11,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Row(
                            [
                                self.user_path_field,
                                ft.Button(
                                    "浏览",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    on_click=self._browse_user_path,
                                ),
                            ],
                        ),
                    ],
                    spacing=5,
                ),
                
                ft.Divider(),
                
                ft.Column(
                    [
                        ft.Text("2. ShadowBot.exe 路径", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "• 例如：D:\\Program Files (x86)\\ShadowBot\\ShadowBot.exe",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Row(
                            [
                                self.exe_path_field,
                                ft.Button(
                                    "浏览",
                                    icon=ft.Icons.FILE_OPEN,
                                    on_click=self._browse_exe_path,
                                ),
                            ],
                        ),
                    ],
                    spacing=5,
                ),
                
                ft.Divider(),
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("💡 如何找到这些路径？", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                            ft.Text("• 用户ID路径：随便打开一个机器人应用，右键点击某个流程块————打开所在文件夹位置 即可！", size=12),
                            ft.Text("• 可选择用户ID目录，也可以直接选择其下的 apps 文件夹", size=12),
                            ft.Text("• EXE路径：右键桌面影刀图标 → 属性 → 目标，复制路径", size=12),
                        ],
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=10,
                    border_radius=5,
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("配置"),
            content=content,
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.Button("保存配置", on_click=self._on_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.show_dialog(self.dialog)
    
    async def _browse_user_path(self, e):
        """浏览用户路径"""
        directory_path = await ft.FilePicker().get_directory_path()
        if directory_path:
            self.user_path_field.value = directory_path
            self.user_path_field.update()
    
    async def _browse_exe_path(self, e):
        """浏览EXE路径"""
        files = await ft.FilePicker().pick_files(
            dialog_title="选择 ShadowBot.exe",
            allowed_extensions=["exe"],
        )
        if files and len(files) > 0:
            self.exe_path_field.value = files[0].path
            self.exe_path_field.update()
    
    def _on_save(self, e):
        """保存配置"""
        user_path = self.user_path_field.value.strip()
        exe_path = self.exe_path_field.value.strip()
        
        if not user_path:
            self._show_error("请输入影刀用户ID文件夹路径")
            return
        
        if not exe_path:
            self._show_error("请输入 ShadowBot.exe 路径")
            return
        
        success = config.update({
            "user_path": user_path,
            "exe_path": exe_path,
        })
        
        if success:
            self._close_dialog()
            if self.on_config_saved:
                self.on_config_saved()
            self._show_success("配置保存成功")
        else:
            self._show_error("配置保存失败")
    
    def _on_cancel(self, e):
        """取消"""
        self._close_dialog()
    
    def _close_dialog(self):
        """关闭对话框"""
        if self.dialog:
            self.dialog.open = False
            self.dialog.update()
    
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
