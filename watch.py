#!/usr/bin/env python

import build
import httpwatcher
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def safe_generate():
    try:
        build.generate()
    except Exception as e:
        print("Exception caught while attempting to process project", e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    build.generate()

    output_path = str(Path(build.config['output']).resolve())
    watch_paths = [str(Path(build.config['root']).resolve())]

    httpwatcher.watch(
        output_path,
        watch_paths=watch_paths,
        on_reload=lambda: safe_generate(),
        host='localhost',
        port=8000,
        server_base_path='/',
        watcher_interval=2.0,
        recursive=True,
        open_browser=False
    )
