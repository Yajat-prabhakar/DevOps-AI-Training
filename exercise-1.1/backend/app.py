import logging
import os
import sys
import time

from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("api")

DB_DSN = os.environ.get(
    "DATABASE_URL", "postgresql://app:app@postgres:5432/appdb"
)


def get_conn():
    return psycopg2.connect(DB_DSN, connect_timeout=3)


@app.route("/api/health")
def health():
    """Liveness/readiness probe used by Docker/K8s health checks."""
    status = {"service": "ok", "db": "unknown"}
    try:
        conn = get_conn()
        conn.close()
        status["db"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("DB health check failed: %s", exc)
        status["db"] = "unreachable"
        return jsonify(status), 503
    return jsonify(status), 200


@app.route("/api/hello")
def hello():
    logger.info("Handled /api/hello request")
    return jsonify({"message": "Hello from the Flask API", "ts": time.time()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
