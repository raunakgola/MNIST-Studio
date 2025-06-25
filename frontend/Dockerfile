# Multi-stage build for optimized production image
# Stage 1: Build stage - Install dependencies and build the application
FROM node:18-alpine AS builder

# Set working directory in the container
WORKDIR /app

# Copy package files first to leverage Docker layer caching
# This allows Docker to cache the npm install step if package.json hasn't changed
COPY package*.json ./

# Accept build arguments for environment variables
ARG VITE_PREDICTION_SERVER_URL
# Set as environment variable so Vite can access it during build
ENV VITE_PREDICTION_SERVER_URL=$VITE_PREDICTION_SERVER_URL

# Install all dependencies (including devDependencies needed for building)
# Using npm ci for faster, reliable, reproducible builds in production
RUN npm ci --only=production=false

# Copy the rest of the application source code
COPY . .

# Build the application for production
# This creates an optimized build with minified assets in the dist/ directory
RUN npm run build

# Stage 2: Production stage - Serve the built application
FROM nginx:alpine AS production

# Install dumb-init for proper signal handling in containers
RUN apk add --no-cache dumb-init

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy the built application from the builder stage
# The Vite build output goes to /dist by default
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration for SPA routing
COPY --chown=nextjs:nodejs nginx.conf /etc/nginx/nginx.conf

# Change ownership of nginx directories to our non-root user
RUN chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nextjs:nodejs /var/run/nginx.pid && \
    chown -R nextjs:nodejs /usr/share/nginx/html

# Switch to non-root user
USER nextjs

# Expose port 80 for the web server
EXPOSE 80

# Use dumb-init to handle signals properly and start nginx
ENTRYPOINT ["dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]