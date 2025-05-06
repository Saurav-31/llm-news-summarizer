FROM node:16-alpine

# Create app directory and set permissions
WORKDIR /app

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set ownership of the app directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Install dependencies
COPY --chown=appuser:appgroup package*.json ./
RUN npm install

# Copy the rest of the application
COPY --chown=appuser:appgroup . .

EXPOSE 3000

CMD ["npm", "start"] 