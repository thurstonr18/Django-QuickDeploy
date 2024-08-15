import os, sys, re
import subprocess
from subprocess import Popen as pop

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
rrico = os.path.join(bundle_dir, 'rr.ico')

class Deployer:
    def __init__(self, answers):
        self.password = answers['password']
        self.features = answers['features']
        self.project_name = answers['name']
        self.path = f"{answers['path']}:/"
        self.psql_path = answers['psql']
        self.project_path = os.path.join(self.path, self.project_name) #Top directory (e.g. Z:/Avit-internal-apps); does not include Django root
        self.django_path = None


    def process(self, cmd, shell, wdir=None):
        if wdir is None:
            p = pop([shell, '/c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            try:
                p = pop([shell, '/c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=wdir)
            except Exception as e:
                print(f'\nERROR: An exception occurred when processing command "{cmd}"')

        out, err = p.communicate()
        output = out.decode('utf8')
        error = err.decode('utf8')
        if output:
            query = output
        else:
            query = error

        return query

    def setup_db(self):
        cmd = [
            self.psql_path,
            '-U postgres',
            '-c', f"CREATE DATABASE [IF NOT EXISTS] {self.project_name}"
        ]
        self.process(cmd, 'Powershell')

        return

    def deploy(self):
        self.setup_db()

        os.mkdir(self.project_path)
        cmd = f"django-admin startproject {self.project_name}"
        self.process(cmd, 'Powershell', wdir=self.project_path)
        self.django_path = os.path.join(self.project_path, self.project_name)
        cmd = "django-admin startapp main"
        self.process(cmd, 'Powershell', wdir=self.django_path)



        return
