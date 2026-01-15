#!/bin/bash

# site_settings 应用测试运行脚本

echo "========================================="
echo "运行 site_settings 应用测试"
echo "========================================="
echo ""

# 激活虚拟环境
source ~/Desktop/myenv/bin/activate

# 运行测试
python3 manage.py test test.site_settings --verbosity=2

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ site_settings 应用测试通过"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo "✗ site_settings 应用测试失败"
    echo "========================================="
    exit 1
fi