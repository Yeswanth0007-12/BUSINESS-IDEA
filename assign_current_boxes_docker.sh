#!/bin/bash

# Run the assign_current_boxes.py script inside the backend Docker container

echo "🚀 Running auto-assign script inside Docker container..."
echo ""

docker exec -it packoptima-backend python /app/assign_current_boxes_in_container.py
