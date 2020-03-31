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

## Running
Download, or copy the contents, of [this file](examples/app.py), and
call the new file ``app.py``.

Then execute in the root project directory ``flask run``

