FROM node:18-alpine

WORKDIR /app

# 复制依赖文件并安装
COPY package.json ./
RUN npm install --production

# 复制应用代码
COPY . .

# 构建应用
RUN npm run build

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["npm", "start"]
