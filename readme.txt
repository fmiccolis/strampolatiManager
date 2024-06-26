# Connect to server, check the version of python and install required packages (and python if required)
ssh ubuntu@[ip_address] -i [private key]

# ----------- INSTALL DJANGO

# install virtual environment
# if you are on AMD you may need also two additional commands:
# https://stackoverflow.com/questions/63591163/python3-pip-has-no-installation-candidate
# sudo add-apt-repository universe
# sudo apt update
# sudo apt install python3.10-venv
#
# sudo apt-get update
# sudo apt-get install python3-pip -y
# sudo -H pip3 install --upgrade pip
# sudo -H pip3 install virtualenv
#
# sudo apt install python3.8-venv
#
# sudo -H pip3 install --upgrade pip
# sudo -H pip3 install virtualenv

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-venv


# Download the exist Django App from git
# you can use your own project here
git clone https://github.com/Stefanotuv/AssessmentOI.git

# if you do any mistake
sudo rm -rf /home/ubuntu/strampolati


# you can alternatevely create a project frm scratch see here:
# https://docs.djangoproject.com/en/4.2/intro/tutorial01/
# or you can transfer content from your local machine using scp with using a string like:
# scp-i [path/key] -r [path_local/file or path_local/folder] user@IP:[path_remote/file or path_remote/folder]

# the app requires a set of environment varialble saved on an hidden file that i call .env
# the file can also be creted locally on the same folder using sudo nano /home/ubuntu/AssessmentOI/AssessmentOI/.env
# once the file has been transferred we will make some changes to work in production
scp -i /Users/stefano/.ssh/id_oci_test -r /Users/stefano/Dropbox/NewDev/AssessmentOI/AssessmentOI/.env ubuntu@141.147.113.192:/home/ubuntu/AssessmentOI/AssessmentOI/.env
scp -i /Users/stefano/.ssh/id_oci_test -r /Users/stefano/Dropbox/NewDev/AssessmentOI/AssessmentOI/.env ubuntu@144.21.58.252:/home/ubuntu/AssessmentOI/AssessmentOI/.env

# change parameters in the env file
sudo nano /home/ubuntu/strampolati/.env
set: DEPLOYMENT='remote'
set: all the parameters for the various DB or the DB you want your app to connect to

# create a virtual environment and activate it
# take a note of where you put your virtual environment
source /home/ubuntu/strampolati/.venv/bin/activate
python3 -m venv /home/ubuntu/strampolati/.venv


# If you have download the app form git we need to install the various libraries for the project
# to do that we use pip and the requirements.txt that contained the various libraries
# NOTE: The application has one more folder on the path. it doesnt not start with the project folder directly
# so consider the correct paths when you change the settings for your project
ls
cd strampolati
pip install -r requirements.txt
# after this step all the libraries for the project should be installed a ready
# you can exit the venv
exit


# OPTIONAL
# if you make any change to the files than you may need to pull the changes
# Enter the correct folder and use the git pull command
cd AssessmentOI/AssessmentOI
ls -a
git pull https://github.com/Stefanotuv/AssessmentOI.git



# open the door ubuntu
# this is required to have the webserver exposed to the web.
# we open the 8000
sudo apt-get install iptables-persistent
sudo iptables -I INPUT 5 -p tcp --dport 8000 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo netfilter-persistent save

# open the door on OCI from the OCI console
# to do this add ingress rule to the correct security list for the subnet on OCI

# Reactivate the virtual environment and Test Django
source /home/ubuntu/strampolati/.venv/bin/activate
python /home/ubuntu/strampolati/manage.py runserver 0.0.0.0:8000
# check the address and the app should respond. To use it you have to start the migration and create a super user
# quit the server and deactivate

# ----- ----- ----- ----- INSTALL GUNICORN ----- ----- ----- ----- ----- ----- -----
# test that gunicorn can connect to the django app
# gunicorn is used to enter the application through the wsgi file
# NOTE: check the path for the file
# sudo apt install gunicorn # not required gunicorn is install from the requirements file
# you have to activate the venv to launch gunicorn
source /home/ubuntu/strampolati/.venv/bin/activate

cd /home/ubuntu/strampolati/
gunicorn --bind 0.0.0.0:8000 strampolati.wsgi
# note: it does not work using the absolute path.
# you need to be in the right directory

sudo mkdir /var/log/gunicorn

sudo nano /etc/systemd/system/gunicorn.socket
# ---------------------------------------------------------------------------
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
# ---------------------------------------------------------------------------
sudo nano /etc/systemd/system/gunicorn.service
# ---------------------------------------------------------------------------
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/strampolati
ExecStart=/home/ubuntu/strampolati/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock strampolati.wsgi:application

[Install]
WantedBy=multi-user.target
# ---------------------------------------------------------------------------

# start the service
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# check status
sudo systemctl status gunicorn.socket
sudo systemctl status gunicorn

# restart if you change any python file
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

# ----- ----- ----- ----- INSTALL NGINX ----- ----- ----- ----- ----- ----- -----
# install the server
sudo apt-get install nginx

# make changes to the setting file. if you make changes directly in production be concious that the may get lost
# if you need to run a pull request or actually the change can prevent the git pull
# DEBUG = False
# ALLOWED_HOSTS = ['*']
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Prepare the static files. This step is necessary to put all files on the folder static
# without this steps the CSS and JS files cannot be served to the server
source /home/ubuntu/strampolati/.venv/bin/activate
python /home/ubuntu/strampolati/manage.py collectstatic
deactivate

# create the files and link for NGINIX
sudo nano /etc/nginx/sites-available/strampolati
server {
    listen 80;
    server_name 141.147.113.192;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/strampolati;
    }
    location /media/ {
        root /home/ubuntu/strampolati;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

sudo gpasswd -a www-data ubuntu
sudo -u www-data stat /home/ubuntu/strampolati/static


# enable the file by linking it to the sites-enabled directory
sudo ln -s /etc/nginx/sites-available/strampolati /etc/nginx/sites-enabled

# test nginx
sudo nginx -t

# restart if you change any python file
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
# restart server.
sudo nginx -s reload
sudo systemctl restart nginx
sudo systemctl status nginx

# test the ip address
# if the default port is not open, add an ingress rule and in ubuntu add the below
ssh ubuntu@141.147.115.202 -i /Users/stefano/.ssh/id_oci_test
sudo iptables -I INPUT 5 -p tcp --dport 80 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo netfilter-persistent save

# https
# https://pylessons.com/django-deployment
sudo apt-get install python3-certbot-nginx

sudo nano /etc/nginx/sites-available/strampolati

IP-webserver:

sudo certbot --nginx -d IP-webserver -d IP-webserver