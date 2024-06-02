from pathlib import Path

from flask_openapi3 import Info, OpenAPI

from app.register_endpoints import register_endpoints


def run():
    app_info = Info(title="Yuta API", version="1.0.0", description="Especificaçes da API do Yuta")
    app = OpenAPI(__name__, info=app_info)

    app.config.from_pyfile("config.py", silent=True)

    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    register_endpoints(app)

    app.run(host="0.0.0.0", port=3000, debug=True)
