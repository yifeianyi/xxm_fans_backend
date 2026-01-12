#!/bin/bash
# FansDIY 应用测试脚本

echo "开始运行 FansDIY 应用测试..."
echo "======================================"

# 激活虚拟环境
source ~/Desktop/myenv/bin/activate

# 运行测试
python3 manage.py test test.fansDIY --verbosity=2

echo "======================================"
echo "FansDIY 应用测试完成！"
