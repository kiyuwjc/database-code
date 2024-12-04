import random
from flask import Flask, request, jsonify
from redis import Redis
import sys

# 初始化 Flask 应用
app = Flask(__name__)

# 默认的 Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MAX_ITER = 500

# 创建 Redis 连接池
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# 获取一个随机的缓存服务器地址
def get_cs(cs_num):
    port = 9527 + cs_num
    return f"http://127.0.0.1:{port}"

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
    result = redis_client.delete(key)
    if result:
        return '1', 200
    else:
        return '0', 200

# 启动 Flask 服务
def run_server(port):
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

if __name__ == "__main__":
    # 从命令行读取端口号
    if len(sys.argv) != 2:
        print("Usage: python cache_server.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    run_server(port)
