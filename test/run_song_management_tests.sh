#!/bin/bash
# Song Management 应用测试运行脚本

echo "========================================="
echo "Song Management 应用测试"
echo "========================================="

# 激活虚拟环境
source ~/Desktop/myenv/bin/activate

# 运行测试
echo ""
echo "运行测试..."
echo ""
python manage.py test test.song_management --verbosity=2

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ 所有测试通过！"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo "✗ 测试失败，请检查错误信息"
    echo "========================================="
    exit 1
fi