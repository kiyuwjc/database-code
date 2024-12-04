import random
from flask import Flask, request, jsonify
from redis import Redis
from multiprocessing import Process

# 初始化 Flask 应用
app = Flask(__name__)

# 默认的 Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MAX_ITER = 500

# 创建 Redis 连接池
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@app.route("/", methods=["POST"])
def set_key():
    """处理 POST 请求，将键值对存储到 Redis 中"""
    data = request.json
    # 修改数据格式以匹配测试脚本的生成格式
    if not isinstance(data, dict) or len(data) != 1:
        return jsonify({"status": "error", "message": "Invalid input format"}), 400
    
    # 提取第一个键值对（测试脚本格式为 {"key-123": "value 123"}）
    key, value = next(iter(data.items()))
    
    # 验证键值是否存在
    if not key or not value:
        return jsonify({"status": "error", "message": "Missing key or value"}), 400

    redis_client.set(key, value)
    return jsonify({"status": "success", "data_received": {key: value}}), 200

@app.route("/<key>", methods=["GET"])
def get_key(key):
    """处理 GET 请求，根据键返回对应的值"""
    value = redis_client.get(key)
    if value:
        return jsonify({key: value.decode('utf-8')}), 200
    else:
        return jsonify({"error": "Key not found"}), 404

# 删除指定 key
@app.route('/<key>', methods=['DELETE'])
def delete_key(key):
    """处理 DELETE 请求，删除指定键"""
    result = redis_client.delete(key)
    # 返回 JSON 格式的删除结果，匹配测试脚本的期望响应
    return jsonify({"status": "success", "deleted": 1 if result else 0}), 200

# 启动 Flask 服务
def run_server(port):
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

# 启动多个服务，分别监听5000、9527、9528端口
def start_servers():
    processes = []
    for port in [5000, 9527, 9528]:
        p = Process(target=run_server, args=(port,))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

if __name__ == "__main__":
    start_servers()