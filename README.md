# Django Quick-Deploy

**Django Quick-Deploy** is a tool designed to help developers get a Django project's basic configurations and commonly used modules set up quickly. Originally built to streamline my own development process, I hope it proves useful to others as well.

## Features
- Quickly configure new Django projects
- Uses PostgreSQL - creates a database and migrates for you
- Adjusts settings.py accordingly
- Simple 'index' view
- Base template with Bootstrap 5.3.1, JQuery 3.2.1, & Font Awesome Free 5.15.3
- Index template extending from base so you can get to work on front-end quicker
- Optional installations included: <a href="https://github.com/Bogdanp/django_dramatiq">Django Dramatiq</a> & <a href="https://github.com/jazzband/django-simple-history">Django Simple History</a>
- Works on Windows (32/64-bit)

## Getting Started

1. **Download the Executable**: 
   - Download the latest version from the [Releases](https://github.com/thurstonr18/Django-QuickDeploy/tree/main/releases) section.

2. **Run the Executable**:
   - Simply run the `.exe` file, and follow the on-screen instructions.

3. **Configure Your Project**:
   - The tool will guide you through setting up your Django project with your preferred configurations.

## Installation (from source)
If you prefer to run from source:
```bash
git clone https://github.com/thurstonr18/Django-QuickDeploy.git
cd Django-QuickDeploy.git
pip install -r requirements.txt
python Inquire.py
```

## Compile your own
If you'd like to compile your own <b>.exe</b>, I used <a href="https://github.com/pyinstaller/pyinstaller">PyInstaller</a>.

## Acknowledgments

This project uses the following third-party libraries:

- **<a href="https://github.com/CITGuru/PyInquirer">PyInquirer</a>**: A Python module for common interactive command line user interfaces.
- **<a href="https://github.com/tqdm/tqdm">TQDM</a>**: A Fast, Extensible Progress Bar for Python and CLI.
