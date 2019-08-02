# mydj
develop_env:python3.6 django2.0.5
pip install django-taggit==0.22.2
pip install Markdown==2.6.11
# install postgresql 
yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
yum install postgresql10
yum install postgresql10-server

/usr/pgsql-10/bin/postgresql-10-setup initdb
systemctl enable postgresql-10
systemctl start postgresql-10

pip install psycopg2==2.7.4


