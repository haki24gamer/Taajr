#!/bin/bash

# Set your ngrok subdomain and Flask app details
FLASK_APP="/home/haki/Documents/VScode/Projets/Taajr/app.py"        # Change this to your Flask app filename
FLASK_PORT=5000           # Change this if your app runs on a different port
NGROK_SUBDOMAIN="mighty-endlessly-oarfish.ngrok-free.app" # Replace with your ngrok subdomain

# Run Flask app in the background
echo "Starting Flask app..."
python3 $FLASK_APP &
FLASK_PID=$!  # Save the Flask process ID to terminate later

# Wait for Flask to start
sleep 2

# Run ngrok with the specified subdomain
echo "Starting ngrok..."
ngrok http --url=$NGROK_SUBDOMAIN $FLASK_PORT &

# Save the ngrok process ID
NGROK_PID=$!

# Trap Ctrl+C to terminate both processes
trap "echo 'Stopping Flask and ngrok...'; kill $FLASK_PID $NGROK_PID; exit" SIGINT

# Keep the script running
wait
