#!/usr/bin/env python

from scss import Compiler as ScssCompiler
from pathlib import Path

from statik.project import StatikProject
from statik.generator import generate as StatikGenerate

import logging
logger = logging.getLogger(__name__)

config = {
    'root': 'src/',
    'output': 'public/'
}

def generate():
    # Generate css files using pyScss
    root = Path(config['root'])
    output = Path(config['output'])

    scss = ScssCompiler(root)

    for file in root.glob('css/**/*.*css'):
        if file.name[0] == '_':
            continue # skip files like _common.scss

        file = file.relative_to(root)
        out = (output / file).with_suffix('.css')


        # ensure output dir exists
        out.parent.mkdir(parents=True, exist_ok=True)
        
        # write file
        if file.suffix == ".scss":
            with out.open('w') as f:
                f.write(scss.compile(file))
        else:
            out.write_text((root/ file).read_text())

    # Generate HTML files using Statik
    StatikGenerate(config['root'], output_path=config['output'], in_memory=False, safe_mode=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate()
