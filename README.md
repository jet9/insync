Insync notifier
===============

Install requirements:
	
- `docopt` python module

Run:

```
Autosync local files with remote host

Usage:
    insync [-c <config>] [-l <log_file>]

Options:
	-c <config>     path to config file. [default: ./insync.yaml]
	-l <log_file>   path to log file. [default: ./insync.log]
```

TODO:

- daemonizing
- sighup config reload
