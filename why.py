import numpy as np

# 设置随机种子以确保结果可重现
np.random.seed(85)

# 创建一个空列表来保存结果
result = []

# 生成3次乐透号码并保存
for _ in range(3):
    # 创建从1到45的整数数组
    a = np.arange(1, 46)
    
    # 随机打乱数组
    np.random.shuffle(a)
    
    # 选择前6个数字作为乐透号码
    lotto = a[:6]
    
    # 将本次乐透号码添加到结果列表中
    result.append(lotto)

# 将结果列表转换为形状为 (3, 6) 的二维NumPy数组
result_array = np.array(result)

# 打印结果
print('3次乐透号码结果 (列表):\n', result)
print('\n二维数组 (shape (3, 6)):\n', result_array)
print('数组的 shape:', result_array.shape)