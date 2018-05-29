#!/usr/bin/env python3

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

def clean():
    output = Path(config['output'])

    depth = 0
    parents = []
    for file in output.glob('**/*'):
        if '.git' in str(file):
            continue

        if file.is_file():
            print("Deleting {0}".format(file))
            file.unlink()
        else:
            parents.append(file)

        # print([p.name for p in file.relative_to(output).parents][:-1])
        # unlink()

    parents.reverse()
    for dir in parents:
        print("Deleting {0}".format(dir))
        dir.rmdir()

    # for dir in output.
    #     rmdir()

def generate():
    # Generate css files using pyScss
    root = Path(config['root'])
    output = Path(config['output'])

    # Copy CNAME
    cname = 'CNAME'
    (output / cname).write_text((root / cname).read_text())


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
