#!/bin/bash

sed -i "/backendUrl/c\  \"backendUrl\": \"$BACKEND_URL\"," /usr/share/nginx/html/assets/config.json
sed -i "/socketUrl/c\  \"socketUrl\": \"$SOCKET_URL\"," /usr/share/nginx/html/assets/config.json

echo "cat config.json"
cat /usr/share/nginx/html/assets/config.json

nginx stop
nginx start

pm2 start /app/backend/dist/src/index.js && nginx -g 'daemon off;'
