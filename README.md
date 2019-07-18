# PredictConn

- Project to predict internet connectivity.

### CAIDA datasets:
- The CAIDA dataset for As to Org mapping can be downloaded from [here](http://data.caida.org/datasets/as-organizations/)
- The as2org_parser script flattens out the data present in the CAIDA dataset. Useful for grouping and ordering organizations (and thereby ASNs bound to orgs). Can be used for validation.  


### Setting up PeeringDB with a MySQL driver:

In addition to the steps listed [here](http://peeringdb.github.io/peeringdb-py/#how-to-install), some notes on configuring MySQL for PeeringDB are listed below:

- Install Mysql - select the second option: not-so-secure encryption method when prompted. 
- Create a new 'peeringdb' database and set the UTF-8 character set.
```
MySQL [(none)]> CREATE DATABASE peeringdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

- Create a new user 'peeringdb' and some password (e.g. '123'):
```
MySQL [(none)]> select host, user from mysql.user;
+-----------+------------------+
| host      | user             |
+-----------+------------------+
| localhost | mysql.infoschema |
| localhost | mysql.session    |
| localhost | mysql.sys        |
| localhost | root             |
+-----------+------------------+
4 rows in set (0.00 sec)

MySQL [(none)]> CREATE USER 'peeringdb' IDENTIFIED BY '123';
Query OK, 0 rows affected (0.02 sec)

MySQL [(none)]> select host, user from mysql.user;
+-----------+------------------+
| host      | user             |
+-----------+------------------+
| %         | peeringdb        |
| localhost | mysql.infoschema |
| localhost | mysql.session    |
| localhost | mysql.sys        |
| localhost | root             |
```

- Grant priveleges to the newly created user 'peeringdb' for all databases, or optionally just restrict to the 'peeringdb' database.
```
MySQL [(none)]> GRANT ALL PRIVILEGES ON *.* TO 'peeringdb'@'%';
```
- Update the peeringdb config with `peeringdb conf-write`  or directly update
`~/.peeringdb/config.yaml` with the above database, user and password credentials created.
```
database:
  engine: mysql
  name: peeringdb
  host: localhost
  password: 123
  user: peeringdb
peeringdb:
  password: ''
  timeout: 0
  url: https://www.peeringdb.com/api
  user: ''

```
- Now, sync the remote PeeringDB to the MySQL database
```
peeringdb sync
```
 

#### Other miscellaneous useful resources:
- Python binding for PeeringDB: https://github.com/peeringdb/peeringdb-py
- API docs: https://www.peeringdb.com/apidocs/#/
- UW NSDI'19 inferences: https://homes.cs.washington.edu/~yuchenj/problink-as-relationships/ 



