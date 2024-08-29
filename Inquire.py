import os
import re
import time
import subprocess
from subprocess import Popen as pop
from PyInquirer import prompt
from Deploy import Deployer
from tqdm import tqdm

class PostgreSQLNotInstalledError(Exception):
    def __init__(self, message="PostgreSQL is not installed. Please install PostgreSQL to proceed."):
        self.message = message
        super().__init__(self.message)

class ErlangNotInstalledError(Exception):
    def __init__(self, message="Erlang is not installed. Please install Erlang to proceed."):
        self.message = message
        super().__init__(self.message)

class RabbitMQNotInstalledError(Exception):
    def __init__(self, message="RabbitMQ is not installed. Please install RabbitMQ to proceed."):
        self.message = message
        super().__init__(self.message)

class PostgreSQLDatabaseExistsError(Exception):
    def __init__(self, message="CREATE DATABASE FAILURE. Database already exists."):
        self.message = message
        super().__init__(self.message)

class Questionnaire:
    def __init__(self):
        dirs = pop(['powershell', '(Get-PSDrive -PSProvider FileSystem).Name'],
                   stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = dirs.communicate()
        output = out.decode('utf8')
        self.sql_path = None
        self.rabbitmq_path = None
        self.drives = output.splitlines()
        self.questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': 'What is your project\'s name?'
            },
            {
                'type': 'list',
                'name': 'path',
                'message': 'Which drive do you want to deploy this project to?',
                'choices': self.drives
            },
            {
                'type': 'checkbox',
                'name': 'features',
                'message': 'Select optional features.',
                'choices': [
                    {'name': 'Dramatiq'},
                    {'name': 'Simple History'},
                ]
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Enter the PostgreSQL password for user postgres.'
            },
            {
                'type': 'confirm',
                'name': 'confirm',
                'message': 'Do you want to deploy with these settings?',
                'default': False
            }
        ]
        intro_message = """
            Welcome to Django QuickDeploy!
            This command-line tool helps you quickly deploy your Django project with ease. To get started, please ensure the following prerequisites are met:

            1. **PostgreSQL Installation:** This tool relies on PostgreSQL for database management. Ensure PostgreSQL is installed and properly configured on your system.

            Follow the prompts to set up your Django project and streamline your deployment process.
            Let’s get started!
            """
        self.responses = {}
        print(intro_message)
        time.sleep(0.3)

    def is_database(self, name=None, pwd=None, sqlpath=None):
        env = os.environ.copy()
        env['PGPASSWORD'] = pwd
        cmd = [
            sqlpath,
            '-U' 'postgres',
            '-c', f"SELECT datname FROM pg_database;"
        ]
        p = pop(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out, err = p.communicate()
        output = out.decode('utf8')
        r0 = re.search(rf'{name}', output, re.IGNORECASE)
        if r0 is not None:
            return False
        print(f"\nDatabase {name} is ready")
        time.sleep(1)
        return True

    def is_postgres(self):
        common_paths = [
            r'C:\Program Files\PostgreSQL',
            r'C:\Program Files (x86)\PostgreSQL'
        ]
        for path in common_paths:
            if os.path.exists(path):
                try:
                    for version_dir in sorted(os.listdir(path)):
                        version_path = os.path.join(path, str(version_dir), 'bin', 'psql.exe')
                        if os.path.isfile(version_path):
                            self.sql_path = str(version_path)
                            print(f"\nPostgreSQL is installed. Found psql at: {self.sql_path}")
                            time.sleep(1)
                            return True
                except PermissionError:
                    print('\nNo access allowed')
                    continue
        print("\nPostgreSQL is not installed.")
        return False

    def find_rabbitmqctl(self):
        common_paths = [
            r'C:\Program Files\RabbitMQ',
            r'C:\Program Files\RabbitMQ Server',
            r'C:\Program Files (x86)\RabbitMQ',
            r'C:\Program Files (x86)\RabbitMQ Server'
        ]
        for path in common_paths:
            if os.path.exists(path):
                try:
                    for version_dir in sorted(os.listdir(path)):
                        bin_path = os.path.join(path, str(version_dir), 'sbin', 'rabbitmqctl.bat')
                        if os.path.isfile(bin_path):
                            self.rabbitmq_path = str(bin_path)
                            return
                except PermissionError:
                    print('\nNo access allowed')
                    return None
        return None

    def check_erlang(self):
        try:
            result = subprocess.run(["erl", "-eval", "erlang:display(erlang:system_info(otp_release)), halt()"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            otp_release = result.stdout.decode().strip()
            print(f"\nErlang is installed. Found Erlang OTP release: {otp_release}")
            time.sleep(.5)
            return True
        except subprocess.CalledProcessError:
            return False

    def check_rabbitmq(self):
        self.find_rabbitmqctl()
        if self.rabbitmq_path:
            try:
                subprocess.run([self.rabbitmq_path, "status"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"\nRabbitMQ is installed. Found rabbitmqctl at: {self.rabbitmq_path}")
                time.sleep(1)
                return True
            except subprocess.CalledProcessError:
                return False
        return False

    def ask_it(self):
        while True:
            try:
                answers = prompt(self.questions)
                fpath = f"{answers['path']}:/"
                ppath = os.path.join(fpath, answers['name'])
                if os.path.isdir(ppath):
                    print(f"\nError: The directory '{ppath}' already exists. Please choose a different project name or drive.")
                    continue
                if not self.is_postgres():
                    raise PostgreSQLNotInstalledError()
                if not self.is_database(name=answers['name'], pwd=answers['password'], sqlpath=str(self.sql_path)):
                    raise PostgreSQLDatabaseExistsError()
                self.responses.update(
                    {
                        'project_name': answers['name'],
                        'project_drive': ppath,
                        'project_features': answers['features'],
                        'sql_pw': answers['password'],
                        'sql_path': str(self.sql_path),
                        'confirm': answers['confirm']
                    }
                )
                if "Dramatiq" in answers['features']:
                    if not self.check_erlang():
                        raise ErlangNotInstalledError()
                    if not self.check_rabbitmq():
                        raise RabbitMQNotInstalledError()
                return self.responses
            except Exception as e:
                return 'HELP'

if __name__ == "__main__":
    ppath = None
    q = Questionnaire()
    while True:
        try:
            qa = q.ask_it()
        except Exception as e:
            print(e)
            exit()
        try:
            confirm = qa['confirm']
        except:
            exit()
        if confirm:
            break
        else:
            restart_prompt = {
                'type': 'confirm',
                'name': 'restart',
                'message': 'Do you want to restart the questionnaire?',
                'default': True,
            }
            restart = prompt(restart_prompt)
            if not restart['restart']:
                exit()
    try:
        dep = Deployer(qa)
        progress_bar = tqdm(dep.deploy(), desc='Deploying...', total=13)
        for proc in progress_bar:
            progress_bar.set_description(proc)
            progress_bar.update()
        print('Done')
    except Exception as e:
        print(f"An error occurred while deploying the project, please see below.\n\n{str(e)}")
        exit()
