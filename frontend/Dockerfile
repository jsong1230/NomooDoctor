# syntax=docker/dockerfile:1

FROM node:22-alpine AS base

# Install dependencies
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN --mount=type=cache,target=/root/.npm npm ci --prefer-offline

# Copy application code
COPY . .

# Development mode - no build, run with dev server
CMD ["npm", "run", "dev"]
