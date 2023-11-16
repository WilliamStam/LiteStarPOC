# Supervisor

This assumes its all setup and requirements installed and that you can run the service with `python main.py` if not see
the setup guides.

To setup a supervisor service create a file `/etc/supervisor/conf.d/api.conf` (name it whatever you want with a .conf
extension )

```conf
[program:api]
directory=/opt/api/src
command=/opt/api/venv/bin/python main.py
redirect_stderr=true
stdout_logfile=/var/log/api.log
stdout_logfile_backups=10
autostart=true
autorestart=true
```

Notice the "command" it executes. it uses the python executable inside your venv (fix paths accordingly).

you will need to reload the supervisor config to load your new service file. do so with:

```shell
sudo supervisorctl reread
sudo supervisorctl update
```

to start/stop the service

```shell
sudo supervisorctl start api
sudo supervisorctl stop api
```

to get the status

```
sudo supervisorctl status api
```

to watch the output

```
sudo supervisorctl tail -f api
```

Start the service if its not started. make sure its running. check the output to make sure there aren't any errors. and
if all that went according to plan your litestar application should be accessible on
http://yyy.yyy.yyy.yyy:80