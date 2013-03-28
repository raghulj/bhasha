Bhasha - A localization tool
======

Bhasha is a simple localization tool. It uses the simplepo ui and the backend is built with the power of Django. 

Installation
--------------
It is always better to try new tools with a virtual env  in python. If you don't have a virtual env, install it from  [virtual env site] . Once the installation is complete, create a virtual environment for the bhasha application. Let's name it as `bhasha_env`.

`python virtual_env bhasha_env`

To activate the virtual environment,

`source /path/to/bhasha_env/bin/activate`

**Installing Bhasha packages**

`pip install -r bhasha/requirements.txt`

All our package dependencies are installed. To create a database, configure it in `local_settings.py` file. A sample `local_settings_sample.py` is added in `bhasha/bhasha` folder. Copy and rename the file to `local_settings.py` file. Change to your configuration.

`python manage.py syncdb` 

Yup, We have our database. The default username and password for the admin is added. Start the server. 

[virtual env site]: https://pypi.python.org/pypi/virtualenv