
import os, sys, re
import subprocess
from random import random
from subprocess import Popen as pop
import time

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
rrico = os.path.join(bundle_dir, 'rr.ico')


class SubprocessErrorDetected(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class Deployer:
    def __init__(self, answers):

        self.features = answers['project_features']
        self.project_name = answers['project_name']
        self.project_path = answers['project_drive']
        self.psql_path = answers['sql_path']
        self.password = answers['sql_pw']
        self.django_path = None
        self.venv_path = os.path.join(self.project_path, 'venv')


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
    def create_venv(self):
        # Command to create a virtual environment
        cmd = f"py -3.11 -m venv {self.venv_path}"
        #print(f"Creating virtual environment at {self.venv_path}...")
        self.process(cmd, 'Powershell')

    def activate_venv(self):
        # Activation script depends on the OS
        if sys.platform == "win32":
            activate_script = os.path.join(self.venv_path, 'Scripts', 'Activate.ps1')
        else:
            activate_script = os.path.join(self.venv_path, 'bin', 'activate')

        # Ensure the activation command is used for the subsequent commands
        return activate_script

    def setup_db(self):
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        cmd = [
            self.psql_path,
            '-U' 'postgres',
            '-c', f"CREATE DATABASE {self.project_name};"
        ]
        p = pop(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out, err = p.communicate()
        output = out.decode('utf8')
        if p.returncode != 0:
            raise SubprocessErrorDetected(message=err.decode('utf8'))

        return True


    def pee_pee(self):
        for i in range(100):
            yield "pee pee {}".format(str(i))
            time.sleep(0.05)

    def deploy(self):
        # Set up the database
        yield "Creating DB..."
        self.setup_db()
        time.sleep(1)


        # Create the virtual environment
        yield "Creating venv"
        self.create_venv()
        time.sleep(1)

        # Activate the virtual environment
        activate_script = self.activate_venv()
        activate_cmd = f"& {activate_script}"

        # Create the project directory
        yield "Make dir"
        os.mkdir(os.path.join(self.project_path, self.project_name))
        time.sleep(1)

        # Run the Django commands within the virtual environment
        yield "Run startproject"
        cmd = f"{activate_cmd}; django-admin startproject {self.project_name}"
        self.process(cmd, 'Powershell', wdir=self.project_path)
        time.sleep(1)

        self.django_path = os.path.join(self.project_path, self.project_name)

        yield "Run startapp"
        cmd = f"{activate_cmd}; django-admin startapp main"
        self.process(cmd, 'Powershell', wdir=self.django_path)

        if "Dramatiq" in self.features:
            yield "Install Dramatiq"
            cmd = f"{activate_cmd}; python -m pip install django-dramatiq[rabbitmq]"
            self.process(cmd, 'Powershell', wdir=self.django_path)
            time.sleep(1)
        if "Simple History" in self.features:
            yield "Install Simple History"
            cmd = f"{activate_cmd}; python -m pip install django-simple-history"
            self.process(cmd, 'Powershell', wdir=self.django_path)
            time.sleep(1)



        return