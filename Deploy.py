
import os, sys, re
import subprocess
import zipfile
from subprocess import Popen as pop
import shutil
import time

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
rrico = os.path.join(bundle_dir, 'rr.ico')
model_file = os.path.join(bundle_dir, 'models.py')
view_file = os.path.join(bundle_dir, 'views.py')
urls_file = os.path.join(bundle_dir, 'urls.py')
tasks_file = os.path.join(bundle_dir, 'tasks.py')
settingsurls_file = os.path.join(bundle_dir, 'baseurls.py')
static_files = os.path.join(bundle_dir, 'static.zip')
template_files = os.path.join(bundle_dir, 'templates.zip')
avit_logo = os.path.join(bundle_dir, 'ribbon.png')

time_settings = '''
LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = False

'''

static_settings = '''
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
'''


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

        self.model_dest = None
        self.view_dest = None
        self.task_dest = None
        self.url_dest = None
        self.settingsurls_dest = None
        self.static_dest = None
        self.template_dest = None


        self.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'CONN_MAX_AGE': 30,
                'NAME': '',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            }
        }

        self.settings_data = None


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
            '-c', f"CREATE DATABASE {self.project_name.lower()};"
        ]
        p = pop(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out, err = p.communicate()
        output = out.decode('utf8')
        if p.returncode != 0:
            raise SubprocessErrorDetected(message=err.decode('utf8'))
        self.DATABASES['default']['NAME'] = self.project_name.lower()
        self.DATABASES['default']['PASSWORD'] = self.password

        return True


    def edit_settings(self):
        settings_file = os.path.join(self.django_path, f"{self.project_name}", "settings.py")
        with open(settings_file) as file:
            lines = file.read()

        re0 = re.sub(r'from pathlib import Path', r'import os\nfrom pathlib import Path', lines)
        re1 = re.sub(r'ALLOWED_HOSTS = \[\]', r"ALLOWED_HOSTS = ['*']\nLOGIN_REDIRECT_URL = '/'", re0)
        if "Dramatiq" in self.features and "Simple History" in self.features:
            re2 = re.sub(r"\'django\.contrib\.staticfiles\',",
                         r"'django.contrib.staticfiles',\n    'django_dramatiq',\n    'simple_history',\n    'main'\n",
                         re1)
        elif "Dramatiq" in self.features:
            re2 = re.sub(r"\'django\.contrib\.staticfiles\',",
                         r"'django.contrib.staticfiles',\n    'django_dramatiq',\n    'main'\n",
                         re1)
        elif "Simple History" in self.features:
            re2 = re.sub(r"\'django\.contrib\.staticfiles\',",
                         r"'django.contrib.staticfiles',\n    'simple_history',\n    'main'\n",
                         re1)
        else:
            re2 = re.sub(r"\'django\.contrib\.staticfiles\',",
                         r"'django.contrib.staticfiles',\n    'main'\n",
                         re1)

        re3 = re.search(r'(DATABASES = \{.*}\n\n)', re2, re.DOTALL)
        re4 = re.sub(rf'{re3.group(1)}', str(self.DATABASES), re2)
        re5 = re.search(r'(LANGUAGE_CODE.*USE_TZ = True\n\n)', re4, re.DOTALL)
        re6 = re.sub(rf'{re5.group(1)}', time_settings, re4)
        re7 = re.search(r'(STATIC_URL = \'\w+/\')', re6)
        settings_data = re.sub(rf'{re7.group(1)}', static_settings, re6)
        with open(settings_file, 'w+') as file:
            file.write(settings_data)

        return

    def copy_files(self):
        # Ensure self.django_path is set to a valid directory
        if not self.django_path:
            raise ValueError("self.django_path must be set to the directory where manage.py is located")

        # Declare the app directory's location
        main_dest = os.path.join(self.django_path, 'main')

        # Path to copy urls.py into
        main_urls_dest = os.path.join(main_dest, 'urls.py')

        # Path to copy views.py into
        views_dest = os.path.join(main_dest, 'views.py')

        # Path to copy models.py into
        models_dest = os.path.join(main_dest, 'models.py')

        # Path to copy baseurls.py into, renaming it to urls.py
        project_urls_dest = os.path.join(self.django_path, f"{self.project_name}", "urls.py")

        # Set media destination (for AVIT logo)
        media_dest = os.path.join(self.django_path, 'media', 'ribbon.png')

        # Ensure the target directories exist
        #os.makedirs(os.path.dirname(main_urls_dest), exist_ok=True)
        #os.makedirs(os.path.dirname(project_urls_dest), exist_ok=True)
        os.makedirs(os.path.dirname(media_dest), exist_ok=True)


        # Copy urls.py
        shutil.copy(urls_file, main_urls_dest)

        # Copy views.py
        shutil.copy(view_file, views_dest)

        # Copy models.py
        shutil.copy(model_file, models_dest)

        # Copy and rename baseurls.py to urls.py
        shutil.copy(settingsurls_file, project_urls_dest)

        # Copy logo over to media/
        shutil.copy(avit_logo, media_dest)

        # Unzip static.zip into both self.django_path and self.django_path/main
        with zipfile.ZipFile(static_files) as zip_ref:
            zip_ref.extractall(self.django_path)
            zip_ref.extractall(main_dest)

        # Unzip templates.zip into self.django_path/main
        with zipfile.ZipFile(template_files, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(self.django_path, 'main'))

        if "Dramatiq" in self.features:
            shutil.copy(tasks_file, os.path.join(main_dest, "tasks.py"))

        return

    def deploy(self):
        self.django_path = os.path.join(self.project_path, self.project_name)

        # Create the project directory
        yield "Make dir"
        os.mkdir(self.project_path)
        time.sleep(1)

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

        yield "Upgrade pip"
        cmd = f"{activate_cmd}; python -m pip install --upgrade pip"
        self.process(cmd, 'Powershell', wdir=self.project_path)
        time.sleep(1)

        yield "Install deps"
        cmd = f"{activate_cmd}; python -m pip install Django==5.1 requests psycopg2"
        self.process(cmd, 'Powershell', wdir=self.project_path)
        time.sleep(1)

        # Run the Django commands within the virtual environment
        yield "Run startproject"
        cmd = f"{activate_cmd}; python -m django startproject {self.project_name}"
        self.process(cmd, 'Powershell', wdir=self.project_path)
        time.sleep(1)

        yield "Run startapp"
        cmd = f"{activate_cmd}; python -m django startapp main"
        self.process(cmd, 'Powershell', wdir=self.django_path)
        time.sleep(1)

        if "Dramatiq" in self.features:
            yield "Install Dramatiq"
            cmd = f"{activate_cmd}; python -m pip install django-dramatiq[rabbitmq]"
            self.process(cmd, 'Powershell', wdir=self.django_path)
            cmd = f"{activate_cmd}; python -m pip install pika"
            self.process(cmd, 'Powershell', wdir=self.django_path)
            time.sleep(1)
        else:
            yield "Skip Dramatiq"
            time.sleep(1)

        if "Simple History" in self.features:
            yield "Install Simple History"
            cmd = f"{activate_cmd}; python -m pip install django-simple-history"
            self.process(cmd, 'Powershell', wdir=self.django_path)
            time.sleep(1)
        else:
            yield "Skip Simple History"
            time.sleep(1)

        yield "Copy files"
        self.copy_files()
        time.sleep(1)

        yield "Edit settings"
        self.edit_settings()
        time.sleep(1)

        yield "makemigrations"
        cmd = f"{activate_cmd}; python manage.py makemigrations"
        self.process(cmd, 'Powershell', wdir=self.django_path)
        time.sleep(1)

        yield "migrate"
        cmd = f"{activate_cmd}; python manage.py migrate"
        self.process(cmd, 'Powershell', wdir=self.django_path)
        time.sleep(1)

        return