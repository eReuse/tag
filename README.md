# ereuse-tag
Tag management for eReuse.org tag providers.

Allows tag providers to create tags, send them to several Devicehubs and
track them through their lifecycle.

eReuse.org Tag can create Tag IT Smart (TIS) eTags, generating files that
the user can submit to TIS manufacturers to create and print tags.

## Installing
The requirements are:

- Python 3. In debian is `# apt install python3-pip`.
- [PostgreSQL 11 or higher](https://www.postgresql.org/download/).

Install Tags with *pip*:

1. git clone
3. `pip3 install -e . -r requirements.txt`.

Create a PostgreSQL database called *tags* by running
[create-db](examples/create-db.sh):

1. `sudo su - postgres`
2. `bash {absolute-path}/examples/create-db.sh tags dtag`

Configure project using environment file (you can use provided example as quickstart):                    
.. code:: bash 
   
   $ cp examples/env.example .env

## Running
Download, or copy the contents, of [this file](examples/app.py), and
call the new file ``app.py``.

Setup the appropriate token and URL for the connected `devicehub` instance by changing
the value of variable `DEVICEHUBS` in `app.py`.
The token to be specified resides in the devicehub database in table `common.inventory` and column
`tag_token`.

Execute in the root project directory ``flask init-db`` to initialize the database.

Then run the application with `flask run -p <port>`

