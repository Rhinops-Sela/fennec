#!/bin/bash

sed -i "s|http://localhost:3000|$BACKEND_URL|g" "/usr/share/nginx/html/assets/config.json"
sed -i "s|http://localhost:9090|$SOCKET_URL|g" "/usr/share/nginx/html/assets/config.json"

echo "cat config.json"
cat /usr/share/nginx/html/assets/config.json

pm2 start /app/backend/dist/src/index.js && nginx -g 'daemon off;'
