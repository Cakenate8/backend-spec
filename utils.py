from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError
import os


SECRET_KEY = os.getenv("SECRET_KEY", "super-test")
ALGORITHM = "HS256"


def encode_token(customer_id):
    now = datetime.now(timezone.utc)
    payload = {
        "customer_id": customer_id,
        "exp": now + timedelta(hours=1),
        "iat": now
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token missing"}), 401
        
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id = data.get("customer_id")
            if not customer_id:
                return jsonify({"error": "Invalid token"}), 401
        except JWTError:
            return jsonify({"error": "Token is invalid or expired"}), 401
        
        return f(customer_id, *args, **kwargs)
    return decorated