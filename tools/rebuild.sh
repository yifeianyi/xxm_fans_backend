#!/bin/bash
# 用于生产环境：重启后端服务 + 重新加载前端资源

# 1. 重新构建前端资源
cd /home/yifeianyi/Desktop/xxm_fans_home/xxm_fans_frontend
npm run build

# 2、重置静态资源
sudo rm -rf /var/www/xxm_fans_frontend/*
sudo cp -r dist/* /var/www/xxm_fans_frontend/

# 3. 重启 django 后端
sudo systemctl restart gunicorn

# 3. 重载 nginx 以应用新前端资源
sudo systemctl reload nginx

echo "✅ 后端服务已重启，前端资源已重新加载"
