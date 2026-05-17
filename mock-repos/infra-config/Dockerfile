FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run as root (security issue - should use non-root user)
USER root

# Start application
CMD ["node", "server.js"]

# Made with Bob
