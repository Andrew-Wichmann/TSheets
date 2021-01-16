FROM python:3.6-slim-buster

# Install deps
# gcc, python3.7-dev, and libpq-dev are for the psycopg2 python library.
# cron is for, well, the cron. The cron runs the python script every 5 minutes.
RUN apt-get update && apt-get -y install cron gcc python3.7-dev libpq-dev

# Copy in the requirements file and install them
COPY requirements.txt /app/requirements.txt
RUN cd /app && pip install -r requirements.txt

# Copy in application code
# Note: this image can probably be made smaller by ignoring some files in this COPY
COPY . /app
WORKDIR /app

## provided by: https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container
# Copy crontab file to the cron.d directory and the start script into the working dir
COPY crontab /etc/cron.d/crontab
COPY docker/start.sh /app/start.sh

# Give execution rights on the cron job and the start script
RUN chmod 0644 /etc/cron.d/crontab
RUN chmod 0777 /app/start.sh

# Apply cron job
RUN crontab /etc/cron.d/crontab

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the start script on container startup
CMD ["/app/start.sh"]