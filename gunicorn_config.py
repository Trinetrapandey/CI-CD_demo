# Gunicorn is the "production web server" that runs your Flask app on EC2.
# Flask's built-in server (app.run) is only for local testing, never for production.

bind = "0.0.0.0:5000"   # Listen on port 5000 on all network interfaces
workers = 2             # Number of worker processes (2 is fine for a free t2.micro)
timeout = 30
