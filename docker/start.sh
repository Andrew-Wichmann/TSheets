#!/bin/bash

# It might be possible to do this with #!/bin/bash -l
# but that would require loading the env into that file.
# I'm not sure how to do that at run time when the secrets will
# be available.
# https://stackoverflow.com/a/51591762
env >> /etc/environment
cd /app/TSheetsAutomation && python /app/TSheetsAutomation/manage.py migrate
cron -f