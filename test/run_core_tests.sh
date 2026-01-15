#!/bin/bash

# Core 模块测试运行脚本

echo "========================================="
echo "  Core 模块单元测试"
echo "========================================="
echo ""

# 激活虚拟环境
if [ -d "$HOME/Desktop/myenv" ]; then
    source "$HOME/Desktop/myenv/bin/activate"
    echo "已激活虚拟环境"
    echo ""
fi

# 运行测试
echo "运行 Core 模块测试..."
echo ""

python manage.py test test.core --verbosity=2

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✓ 所有测试通过！"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo "  ✗ 测试失败！"
    echo "========================================="
    exit 1
fi