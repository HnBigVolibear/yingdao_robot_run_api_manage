"""
Flask API 应用
提供机器人管理的 REST API 接口
"""

import threading
import logging
from flask import Flask, jsonify

from core.config import config
from core.robot_data import RobotDataManager
from core.robot_launcher import launcher

app: Optional[Flask] = None
api_thread: Optional[threading.Thread] = None
api_running = False


def create_app() -> Flask:
    """创建 Flask 应用"""
    flask_app = Flask(__name__)
    flask_app.logger.setLevel(logging.WARNING)
    
    # 配置 JSON 响应编码，确保中文正常显示
    flask_app.config['JSON_AS_ASCII'] = False
    
    @flask_app.route('/api/robots', methods=['GET'])
    def get_robots():
        """
        获取机器人列表
        
        Returns:
            JSON: {
                "success": true,
                "data": [
                    {
                        "uuid": "xxx",
                        "name": "机器人名称",
                        "version": "1.0.0",
                        "description": "描述",
                        "author": "作者"
                    }
                ]
            }
        """
        try:
            manager = RobotDataManager(config.get_apps_path())
            robots = manager.scan_robots()
            
            data = []
            for robot in robots:
                data.append({
                    "uuid": robot.uuid,
                    "name": robot.name,
                    "version": robot.version,
                    "description": robot.description,
                    "author": robot.author
                })
            
            response_data = {
                "success": True,
                "data": data,
                "count": len(data)
            }
            return jsonify(response_data)
        except Exception as e:
            error_data = {
                "success": False,
                "error": str(e)
            }
            return jsonify(error_data), 500
    
    @flask_app.route('/api/robot/<uuid>', methods=['GET'])
    def get_robot(uuid: str):
        """
        获取单个机器人信息
        
        Args:
            uuid: 机器人 UUID
            
        Returns:
            JSON: {
                "success": true,
                "data": {
                    "uuid": "xxx",
                    "name": "机器人名称",
                    "version": "1.0.0",
                    "description": "描述",
                    "author": "作者"
                }
            }
        """
        try:
            manager = RobotDataManager(config.get_apps_path())
            robots = manager.scan_robots()
            
            for robot in robots:
                if robot.uuid == uuid:
                    response_data = {
                        "success": True,
                        "data": {
                            "uuid": robot.uuid,
                            "name": robot.name,
                            "version": robot.version,
                            "description": robot.description,
                            "author": robot.author
                        }
                    }
                    return jsonify(response_data)
            
            error_data = {
                "success": False,
                "error": f"未找到 UUID 为 {uuid} 的机器人"
            }
            return jsonify(error_data), 404
        except Exception as e:
            error_data = {
                "success": False,
                "error": str(e)
            }
            return jsonify(error_data), 500
    
    @flask_app.route('/api/robots/search', methods=['GET'])
    def search_robots():
        """
        根据机器人名称模糊查询
        
        Query Args:
            name: 机器人名称（支持模糊匹配）
            
        Returns:
            JSON: {
                "success": true,
                "count": 2,
                "data": [
                    {
                        "uuid": "xxx",
                        "name": "机器人名称",
                        "version": "1.0.0",
                        "description": "描述",
                        "author": "作者"
                    }
                ]
            }
        """
        from flask import request
        
        try:
            search_name = request.args.get('name', '').strip()
            
            if not search_name:
                error_data = {
                    "success": False,
                    "error": "请提供 name 参数"
                }
                return jsonify(error_data), 400
            
            manager = RobotDataManager(config.get_apps_path())
            robots = manager.scan_robots()
            
            # 模糊匹配：不区分大小写，查找名称中包含搜索词的机器人
            matched_robots = [
                robot for robot in robots 
                if search_name.lower() in robot.name.lower()
            ]
            
            data = []
            for robot in matched_robots:
                data.append({
                    "uuid": robot.uuid,
                    "name": robot.name,
                    "version": robot.version,
                    "description": robot.description,
                    "author": robot.author
                })
            
            response_data = {
                "success": True,
                "count": len(data),
                "data": data
            }
            return jsonify(response_data)
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": str(e)
            }
            return jsonify(error_data), 500
    
    @flask_app.route('/api/robot/<uuid>/launch', methods=['POST'])
    def launch_robot(uuid: str):
        """
        启动机器人
        
        Args:
            uuid: 机器人 UUID
            
        Returns:
            JSON: {
                "success": true,
                "message": "机器人启动成功"
            }
        """
        try:
            # 使用与页面启动按钮相同的 launcher.launch 方法
            success, message = launcher.launch(uuid)
            
            if success:
                response_data = {
                    "success": True,
                    "message": message
                }
                return jsonify(response_data)
            else:
                error_data = {
                    "success": False,
                    "error": message
                }
                return jsonify(error_data), 500
                
        except Exception as e:
            error_data = {
                "success": False,
                "error": str(e)
            }
            return jsonify(error_data), 500
    
    @flask_app.route('/api/status', methods=['GET'])
    def get_status():
        """
        获取 API 状态
        
        Returns:
            JSON: {
                "success": true,
                "status": "running",
                "configured": true
            }
        """
        response_data = {
            "success": True,
            "status": "running",
            "configured": config.is_configured()
        }
        return jsonify(response_data)
    
    @flask_app.route('/api/config', methods=['GET'])
    def get_config():
        """
        获取当前配置信息
        
        Returns:
            JSON: {
                "success": true,
                "data": {
                    "user_path": "xxx",
                    "exe_path": "xxx",
                    "is_configured": true
                }
            }
        """
        response_data = {
            "success": True,
            "data": {
                "user_path": config.get("user_path", ""),
                "exe_path": config.get("exe_path", ""),
                "is_configured": config.is_configured()
            }
        }
        return jsonify(response_data)
    
    @flask_app.errorhandler(404)
    def not_found(e):
        error_data = {
            "success": False,
            "error": "接口不存在"
        }
        return jsonify(error_data), 404
    
    @flask_app.errorhandler(500)
    def server_error(e):
        error_data = {
            "success": False,
            "error": "服务器内部错误"
        }
        return jsonify(error_data), 500
    
    return flask_app


def start_api_server(host: str = "0.0.0.0", port: int = 16666, daemon: bool = True) -> bool:
    """
    启动 API 服务器
    
    Args:
        host: 监听地址，默认 0.0.0.0（所有网卡）
        port: 监听端口，默认 16666
        daemon: 是否作为守护线程运行
        
    Returns:
        是否启动成功
    """
    global app, api_thread, api_running
    
    if api_running:
        return False
    
    try:
        app = create_app()
        api_running = True
        
        def run_server():
            # 不抑制 werkzeug 日志，让所有输出都显示
            app.run(host=host, port=port, threaded=True, use_reloader=False)
        
        api_thread = threading.Thread(target=run_server, daemon=daemon)
        api_thread.start()
        
        return True
        
    except Exception as e:
        api_running = False
        return False


def stop_api_server():
    """停止 API 服务器"""
    global api_running
    api_running = False


def get_api_status() -> dict:
    """
    获取 API 服务状态
    
    Returns:
        {
            "running": bool,
            "host": str,
            "port": int
        }
    """
    return {
        "running": api_running,
        "host": "0.0.0.0",
        "port": 16666
    }
