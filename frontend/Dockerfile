# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/tailwind.config.js ./
COPY frontend/tsconfig.json ./

# Build arguments
ARG REACT_APP_API_URL=http://localhost:8000

# Set environment variables
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf

# Copy built application from build stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx entrypoint script
COPY nginx/docker-entrypoint.sh /docker-entrypoint.d/40-frontend-config.sh
RUN chmod +x /docker-entrypoint.d/40-frontend-config.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 