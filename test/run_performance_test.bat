@echo off
REM 性能测试一键执行脚本 (Windows版本)

echo 🚀 开始性能测试...

REM 检查是否在test目录下
if not exist "locust.conf" (
    echo 请在test目录下运行此脚本
    pause
    exit /b 1
)

REM 运行Locust性能测试
echo 📊 正在运行性能测试...
locust -f Locustfile.py --config locust.conf

REM 检查测试是否成功完成
if %ERRORLEVEL% EQU 0 (
    echo ✅ 性能测试完成
    
    REM 生成可视化图表
    echo 📈 正在生成可视化图表...
    python visualize_locust.py
    
    REM 生成详细报告
    echo 📝 正在生成详细报告...
    python generate_report.py
    
    echo 🎉 所有测试和报告生成完成！
    echo 查看生成的文件：
    echo   - qps.png (QPS图表)
    echo   - response_time.png (响应时间图表)
    echo   - failures.png (失败数图表)
    echo   - load_test_results_*.csv (原始数据)
    echo   - charts/ (详细图表目录)
) else (
    echo ❌ 性能测试失败
    pause
    exit /b 1
)

pause