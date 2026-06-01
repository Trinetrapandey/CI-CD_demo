"""
A tiny Flask web application.
This is the "application" that our CI/CD pipeline will test and deploy to EC2.
"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    # This is what people see when they open your EC2 public address.
    return jsonify(
        message="Hello! I was deployed automatically by a CI/CD pipeline.",
        status="running",
        version="1.0.0",
    )


@app.route("/health")
def health():
    # A "health check" endpoint. Pipelines and monitors hit this
    # to confirm the app is alive. It just returns 200 OK.
    return jsonify(status="healthy"), 200


def add(a, b):
    # A plain function with no web stuff, so we have something simple to unit-test.
    return a + b


if __name__ == "__main__":
    # Only used when you run "python app.py" locally for quick testing.
    # In production on EC2, Gunicorn runs the app instead (see README).
    app.run(host="0.0.0.0", port=5000)
