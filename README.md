# 湖南大白熊的影刀RPA接口管理平台
- V0.0.1 
- win端，支持影刀社区版！！！暴露API供远程调用一键启动影刀机器人！！！

基于 Python Flet 框架开发的 Windows 桌面应用，用于管理影刀RPA机器人并提供 REST API 接口服务。

## 功能特性

- 🤖 **机器人列表展示** - 自动扫描并显示本地所有影刀机器人
- ▶️ **一键启动** - 点击按钮即可启动对应机器人
- 🔌 **REST API 接口** - 提供 HTTP 接口，支持远程调用启动机器人
- 📚 **接口文档** - 内置 API 接口文档，一键查看所有接口
- 🔍 **模糊搜索** - 支持按机器人名称模糊查询
- ⚙️ **灵活配置** - 支持配置用户路径和影刀程序路径
- 💾 **配置持久化** - 配置自动保存到用户目录，永久保留
- 🎨 **现代化UI** - 基于 Flet 框架的 Material Design 界面
- 👤 **作者信息** - 左上角展示作者信息，点击头像显示收款码

## 项目结构

```
yingdao_robot_run_api_manage/
├── api/                        # API 模块
│   ├── __init__.py
│   └── app.py                  # Flask API 服务
├── core/                       # 核心模块
│   ├── config.py               # 配置管理
│   ├── robot_data.py           # 机器人数据读取
│   └── robot_launcher.py       # 机器人启动
├── ui/                         # UI界面模块
│   ├── __init__.py
│   ├── api_doc_dialog.py       # 接口文档对话框
│   ├── config_dialog.py        # 配置对话框
│   ├── main_window.py          # 主窗口
│   └── robot_list_view.py      # 机器人列表视图
├── bear.png                    # 作者头像
├── sponsor.png                 # 收款码
├── main.py                     # 应用入口
├── requirements.txt            # 依赖列表
└── README.md                   # 项目说明
```

## 安装运行（建议使用venv虚拟环境！）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

## 使用说明

### 首次使用

1. 首次打开应用会自动弹出配置对话框
2. 配置两个路径：
   - **影刀用户ID文件夹路径**：如 `C:\Users\Administrator\AppData\Local\ShadowBot\users\64*************74`
     - 支持直接选择用户ID目录，也可以选择其下的 `apps` 文件夹
   - **ShadowBot.exe 路径**：如 `D:\Program Files (x86)\ShadowBot\ShadowBot.exe`
3. 点击"保存配置"完成设置
4. 系统会自动加载该用户下的所有机器人

### 日常使用

- **启动机器人**：点击机器人卡片右侧的"▶ 启动"按钮
- **刷新列表**：点击右上角的"刷新"按钮
- **修改配置**：点击右上角的"⚙️ 配置"按钮
- **查看接口文档**：点击"接口文档"按钮查看所有 API 接口

### API 接口

应用启动后会自动开启 API 服务（端口 16666），支持以下接口：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/status` | GET | 获取 API 服务状态 |
| `/api/config` | GET | 获取当前配置 |
| `/api/robots` | GET | 获取所有机器人列表 |
| `/api/robot/{uuid}` | GET | 获取指定机器人信息 |
| `/api/robots/search?name={keyword}` | GET | 根据名称模糊查询机器人 |
| `/api/robot/{uuid}/launch` | POST | 启动指定机器人 |

**调用示例：**

```python
import requests

# 获取机器人列表
response = requests.get('http://localhost:16666/api/robots')
robots = response.json()

# 根据名称模糊查询
response = requests.get('http://localhost:16666/api/robots/search?name=测试')
robots = response.json()

# 启动机器人
uuid = robots['data'][0]['uuid']
response = requests.post(f'http://localhost:16666/api/robot/{uuid}/launch')
result = response.json()
```

## 数据目录

配置文件保存在用户 AppData 目录，打包后也不会丢失：

- **Windows**: `%APPDATA%\yingdao_robot_manager\config.json`
  - 通常路径：`C:\Users\用户名\AppData\Roaming\yingdao_robot_manager\config.json`

## 技术栈

- **Python 3.8+**
- **Flet >= 0.25.0** - 跨平台UI框架（基于Flutter）
- **Flask >= 2.3.0** - REST API 框架
- **requests >= 2.31.0** - HTTP 请求库

## 打包 exe
#### 强烈建议使用venv虚拟环境打包！否则可能打出来的exe会很大！甚至超过1GB！！！

使用 PyInstaller 打包（需激活虚拟环境）：

```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 打包命令
pyinstaller --windowed --onefile --name "湖南大白熊的影刀RPA接口管理平台" --paths "./.venv/Lib/site-packages" --add-data "bear.ico;." --add-data "sponsor.png;." main.py  --icon bear.ico --add-data "./.venv/Lib/site-packages;." --noconfirm --clean
```

打包后的可执行文件在 `dist/` 目录下。

## 注意事项

1. 确保影刀客户端已正确安装
2. 配置的用户路径必须包含 `apps` 文件夹
3. 需要 Windows 系统才能启动机器人
4. API 服务端口为 16666，请确保端口未被占用

## 作者

**湖南大白熊** - 影刀RPA高级开发者^_^

- GitHub主页: [https://github.com/HnBigVolibear](https://github.com/HnBigVolibear)
- 本项目仓库开源地址：[https://github.com/HnBigVolibear/yingdao_robot_run_api_manage](https://github.com/HnBigVolibear/yingdao_robot_run_api_manage)

### Buy me a Coffee:

![img](./sponsor.png)

## License

MIT License
