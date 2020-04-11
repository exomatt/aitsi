import os
import shutil
import subprocess

if __name__ == '__main__':
    dirname, filename = os.path.split(os.path.abspath(__file__))
    path: str = os.path.join(dirname, "generate")
    print(path)
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    subprocess.call(
        'pipenv run pyinstaller -D -c --hidden-import="pkg_resources.py2_warn" --distpath ./generate/dist --workpath ./generate/build --specpath ./generate/ spa.py')
    source = "logging.conf"
    destination = path + "/dist/spa/logging.conf"
    shutil.copy(source, destination)
