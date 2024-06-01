from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask


def run(test_config: Optional[Dict[str, Any]] = None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=str(Path(app.instance_path) / 'yuta.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello() -> str:
        return 'Hello, World!'

    app.run(host='0.0.0.0', port=3000, debug=True)
