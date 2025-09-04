FROM node:18-alpine

# Set working directory
WORKDIR /app

# Set environment variables for build
ENV VITE_BACKEND_URL=http://backend:8000

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application with correct port
CMD ["npm", "run", "preview", "--", "--port", "3000", "--host", "0.0.0.0"]
