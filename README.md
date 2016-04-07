# JIRA RethinkDB

This project contains scripts and instructions to generate reports from JIRA, using its RESTful
API in Python, alongside RethinkDB, also in Python.

RethinkDB can be started with the following command.

    docker run --name some-rethink -v "$PWD:/data" -d rethinkdb

And then you can get the IP address with:

    docker inspect --format '{{ .NetworkSettings.IPAddress }}' some-rethink

## Configuration file

You must create a dotEnv file in your project local directory, with the following contents:

JIRA=${JIRAURL}
USERNAME=${JIRAUSER}
PASSWORD=${ITSPASS}
RETHINKDB=${RETHINKDBIP}

## Dependencies

You can install the projects dependencies with pip install -r requirements.txt (you may have
to use sudo). You can also use Anaconda and conda instead.