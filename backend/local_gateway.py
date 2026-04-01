import os
from flask import Flask, request, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for the frontend (Vite on 5173) and allow custom authentication headers
CORS(app, supports_credentials=True, origins=["http://localhost:5173"], allow_headers=["Content-Type", "Authorization", "X-Google-Token", "X-User-Email"])

# Configuration: Path Prefix -> Target URL
SERVICES = {
    "/api/v1/students": "http://localhost:5001/student",
    "/api/v1/tutors": "http://localhost:5002/tutor",
    "/api/v1/sessions": "http://localhost:5003/session",
    "/api/v1/meetings": "http://localhost:5004/meeting",
    "/api/v1/calendar": "http://localhost:5005/calendar",
    "/api/v1/emails": "http://localhost:5006/email",
    "/api/v1/payments": "http://localhost:5007/payment",
    "/api/v1/create-session": "http://localhost:5105/create-session",
    "/api/v1/update-session": "http://localhost:5106/update-session",
    "/api/v1/book-session": "http://localhost:5100/book-session",
    "/api/v1/cancel-session": "http://localhost:5101/cancel-session",
    "/api/v1/rate-tutor": "http://localhost:5102/rate-tutor",
    "/api/v1/getsessions": "http://localhost:5103/getsessions",
}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    # Determine which service to route to
    full_path = "/" + path
    target_service_url = None
    stripped_path = full_path
    
    for prefix, url in SERVICES.items():
        if full_path.startswith(prefix):
            target_service_url = url
            # Kong typically strips the path prefix (e.g., /api/v1/calendar -> /)
            stripped_path = full_path[len(prefix):]
            if not stripped_path.startswith("/"):
                stripped_path = "/" + stripped_path
            break
            
    if not target_service_url:
        return f"Service not found for path: {full_path}", 404

    url = f"{target_service_url}{stripped_path}"
    if request.query_string:
        url += f"?{request.query_string.decode('utf-8')}"

    print(f"Proxying: {request.method} {full_path} -> {url}")

    # Forward the request
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )
        
        # Exclude certain hop-by-hop headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        print(f"Response: {resp.status_code}")
        return response
    except Exception as e:
        print(f"Proxy error for {url}: {str(e)}")
        return f"Proxy error: {str(e)}", 500

if __name__ == "__main__":
    print("Local Gateway starting on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
