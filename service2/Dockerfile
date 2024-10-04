FROM node:14-slim
WORKDIR /app
# Install necessary system utilities: procps for ps, coreutils for uptime
RUN apt-get update && apt-get install -y procps coreutils && rm -rf /var/lib/apt/lists/*
COPY service2.js /app
CMD ["node", "service2.js"]