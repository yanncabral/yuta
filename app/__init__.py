from pathlib import Path
from typing import Any, Dict, Optional

from flask_openapi3 import Info, OpenAPI

from app.register_blueprints import register_blueprints


def run(test_config: Optional[Dict[str, Any]] = None):
    app_info = Info(title="Yuta API", version="1.0.0", description="Especificaçes da API do Yuta")
    app = OpenAPI(__name__, info=app_info)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=str(Path(app.instance_path) / "yuta.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    register_blueprints(app)

    app.run(host="0.0.0.0", port=3000, debug=True)
