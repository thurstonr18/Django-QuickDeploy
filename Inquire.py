import os, sys, re, time
import subprocess
import winreg
from subprocess import Popen as pop
from PyInquirer import prompt
from Deploy import Deployer


class PostgreSQLNotInstalledError(Exception):
    def __init__(self, message="PostgreSQL is not installed. Please install PostgreSQL to proceed."):
        self.message = message
        super().__init__(self.message)


class Questionnaire:
    def __init__(self):
        dirs = pop(['powershell', '(Get-PSDrive -PSProvider FileSystem).Name'],
                   stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = dirs.communicate()
        output = out.decode('utf8')
        self.sql_path = None
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

        print(intro_message)
        time.sleep(2)

    def find_psql(self):
        common_paths = [
            r'C:\Program Files\PostgreSQL',
            r'C:\Program Files (x86)\PostgreSQL'
        ]

        for path in common_paths:
            if os.path.exists(path):
                try:
                    # List all directories in the base path
                    for version_dir in sorted(os.listdir(path)):
                        version_path = os.path.join(path, version_dir, 'bin', 'psql.exe')
                        if os.path.isfile(version_path):
                            return version_path
                except PermissionError:
                    return None
        return None

    def is_postgres(self):
        #print('\nPlease wait..')
        time.sleep(2)
        self.find_psql()
        if self.sql_path:
            #print(f"\nPostgreSQL is installed. Found psql at: {psql_path}")
            return True
        else:
            #print("\nPostgreSQL is not installed.")
            return False

    def ask_it(self):
        while True:
            answers = prompt(self.questions)
            fpath = f"{answers['path']}:/"
            ppath = os.path.join(fpath, answers['name'])
            if os.path.isdir(ppath):
                print(f"Error: The directory '{ppath}' already exists. Please choose a different project name or drive.")
                continue  # Restart the questions if the directory exists
            if not self.is_postgres():
                raise PostgreSQLNotInstalledError(f"Error: PostgreSQL is not installed.\n\nIt appears that the required PostgreSQL database server is missing from your system. Please install PostgreSQL to proceed.")
            answers.update(
                {
                    'psql': str(self.sql_path)
                }
            )
            return answers




if __name__ == "__main__":
    ppath = None

    q = Questionnaire()
    while True:
        try:
            qa = q.ask_it()

        except:
            exit()

        # Check if the user confirms the deployment
        if qa['confirm']:
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
                exit()  # Exit the program if the user doesn't want to restart

    try:
        #dep = Deployer(qa)
        #dep.deploy()
        print('Done')
    except Exception as e:
        print(f"An error occurred while deploying the project, please see below.\n\n{str(e)}")
        exit()
