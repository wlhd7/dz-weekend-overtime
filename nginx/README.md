# 域名配置说明

## 1. 修改 Nginx 配置

编辑 `nginx/nginx.conf` 文件，将 `your-domain.com` 替换为你的实际域名：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改这里
    ...
}
```

## 2. DNS 解析设置

在你的域名提供商处添加 A 记录：
- 类型：A
- 主机记录：@ (或你的域名前缀，如 www)
- 记录值：你的服务器 IP 地址
- TTL：默认即可

## 3. 启动服务

```bash
# 停止现有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

## 4. HTTPS 配置（可选）

如果需要 HTTPS，可以使用 Let's Encrypt：

```bash
# 安装 certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 证书会自动配置到 nginx
```

## 5. 访问测试

配置完成后，通过以下方式访问：
- HTTP: http://your-domain.com
- HTTPS: https://your-domain.com (如果配置了 SSL)

## 6. 故障排除

查看日志：
```bash
# 查看 nginx 日志
docker-compose logs nginx

# 查看所有服务状态
docker-compose ps
```
