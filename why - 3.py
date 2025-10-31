from flask import Flask, render_template, request, jsonify
import os
import random
import requests
import base64
import json
from datetime import datetime
import hashlib
import time

app = Flask(__name__)

# 模拟用户数据存储
user_data = {
    'total_points': 0,
    'transactions': []
}

# 简单的区块链实现
class SimpleBlockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """创建创世区块"""
        genesis_block = {
            'index': 0,
            'timestamp': str(datetime.now()),
            'transactions': [],
            'previous_hash': '0',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
    
    def add_transaction(self, user_id, garbage_type, points):
        """添加交易到区块链"""
        transaction = {
            'user_id': user_id,
            'garbage_type': garbage_type,
            'points': points,
            'timestamp': str(datetime.now())
        }
        
        self.pending_transactions.append(transaction)
        
        # 每3笔交易生成一个新区块
        if len(self.pending_transactions) >= 3:
            self.mine_block()
        
        return True
    
    def mine_block(self):
        """挖掘新区块"""
        block = {
            'index': len(self.chain),
            'timestamp': str(datetime.now()),
            'transactions': self.pending_transactions.copy(),
            'previous_hash': self.chain[-1]['hash'],
            'nonce': 0
        }
        
        block['hash'] = self.calculate_hash(block)
        self.chain.append(block)
        self.pending_transactions = []
        
        print(f"新区块 #{block['index']} 已生成")
    
    def calculate_hash(self, block):
        """计算区块哈希值"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def get_user_transactions(self, user_id):
        """获取用户的所有交易"""
        user_txs = []
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['user_id'] == user_id:
                    user_txs.append(transaction)
        return user_txs

# 初始化区块链
blockchain = SimpleBlockchain()

# AI识别功能（模拟版本）
def simulate_ai_classification(image_file):
    """
    模拟AI图像分类
    在实际应用中，这里应该调用真实的AI模型
    """
    try:
        # 基于文件名的简单识别（实际应该分析图片内容）
        filename = image_file.filename.lower()
        
        # 关键词匹配
        if any(word in filename for word in ['bottle', 'plastic', 'can', 'paper', 'cardboard', 'glass']):
            return "可回收垃圾", 0.92
        elif any(word in filename for word in ['battery', 'medicine', 'chemical', 'fluorescent']):
            return "有害垃圾", 0.88
        elif any(word in filename for word in ['food', 'fruit', 'vegetable', 'apple', 'banana', 'leftover']):
            return "厨余垃圾", 0.85
        else:
            # 随机分类作为备选
            garbage_types = ['可回收垃圾', '有害垃圾', '厨余垃圾', '其他垃圾']
            weights = [0.4, 0.1, 0.3, 0.2]  # 可回收垃圾概率较高
            garbage_type = random.choices(garbage_types, weights=weights)[0]
            confidence = round(random.uniform(0.7, 0.95), 2)
            return garbage_type, confidence
            
    except Exception as e:
        print(f"AI识别模拟异常: {e}")
        return "其他垃圾", 0.7

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_garbage():
    """处理图片分类请求"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片'})
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        print(f"收到图片上传: {image_file.filename}")
        
        # 使用模拟AI识别
        garbage_type, confidence = simulate_ai_classification(image_file)
        
        # 计算积分
        points_map = {
            '可回收垃圾': 10,
            '有害垃圾': 15, 
            '厨余垃圾': 8,
            '其他垃圾': 5
        }
        points = points_map.get(garbage_type, 5)
        
        print(f"识别结果: {garbage_type}, 积分: {points}, 置信度: {confidence}")
        
        return jsonify({
            'success': True,
            'garbage_type': garbage_type,
            'points': points,
            'confidence': confidence,
            'message': 'AI识别成功！'
        })
        
    except Exception as e:
        print(f"分类过程异常: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_points', methods=['POST'])
def add_points():
    """添加积分到区块链"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        garbage_type = data.get('garbage_type', '未知类型')
        points = data.get('points', 0)
        
        # 更新用户积分
        user_data['total_points'] += points
        
        # 记录交易到区块链
        blockchain.add_transaction(user_id, garbage_type, points)
        
        # 也保存到本地记录
        user_data['transactions'].append({
            'user_id': user_id,
            'garbage_type': garbage_type,
            'points': points,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return jsonify({
            'success': True,
            'total_points': user_data['total_points'],
            'message': f'成功获得 {points} 碳积分！已记录到区块链。'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_points')
def get_points():
    """获取用户总积分"""
    return jsonify({
        'success': True,
        'total_points': user_data['total_points']
    })

@app.route('/get_blockchain_info')
def get_blockchain_info():
    """获取区块链信息"""
    try:
        user_transactions = blockchain.get_user_transactions('default_user')
        
        return jsonify({
            'success': True,
            'block_count': len(blockchain.chain),
            'total_transactions': sum(len(block['transactions']) for block in blockchain.chain),
            'user_transactions': user_transactions,
            'latest_block': blockchain.chain[-1] if blockchain.chain else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test')
def test_page():
    """测试页面"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>功能测试</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            button { padding: 10px; margin: 5px; }
            .result { background: #f0f0f0; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🧪 系统功能测试</h1>
        
        <button onclick="testAI()">测试AI识别</button>
        <button onclick="testBlockchain()">测试区块链</button>
        <button onclick="testPoints()">测试积分系统</button>
        
        <div id="result" class="result"></div>

        <script>
            async function testAI() {
                try {
                    // 模拟图片上传
                    const response = await fetch('/classify', {
                        method: 'POST',
                        body: new FormData()
                    });
                    const result = await response.json();
                    
                    document.getElementById('result').innerHTML = 
                        `<h3>✅ AI识别测试</h3>
                         <p>状态: ${result.success ? '成功' : '失败'}</p>
                         <p>结果: ${result.garbage_type || result.error}</p>`;
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<h3>❌ AI识别测试失败</h3>
                         <p>错误: ${error.message}</p>`;
                }
            }
            
            async function testBlockchain() {
                try {
                    const response = await fetch('/get_blockchain_info');
                    const result = await response.json();
                    
                    document.getElementById('result').innerHTML = 
                        `<h3>⛓️ 区块链测试</h3>
                         <p>区块数量: ${result.block_count}</p>
                         <p>总交易数: ${result.total_transactions}</p>
                         <p>状态: ${result.success ? '正常' : '异常'}</p>`;
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<h3>❌ 区块链测试失败</h3>
                         <p>错误: ${error.message}</p>`;
                }
            }
            
            async function testPoints() {
                try {
                    const response = await fetch('/get_points');
                    const result = await response.json();
                    
                    document.getElementById('result').innerHTML = 
                        `<h3>💰 积分系统测试</h3>
                         <p>当前积分: ${result.total_points}</p>
                         <p>状态: ${result.success ? '正常' : '异常'}</p>`;
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<h3>❌ 积分系统测试失败</h3>
                         <p>错误: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # 创建必要的文件夹
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 60)
    print("🚀 启动智能垃圾分类系统")
    print("📱 主页面: http://localhost:5000")
    print("🧪 测试页面: http://localhost:5000/test")
    print("❤️  健康检查: http://localhost:5000/health")
    print("=" * 60)
    
    # 启动Flask应用
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )