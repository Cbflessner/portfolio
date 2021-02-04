# portfolio


## Getting Started
To run this appliction you will need to fork and clone this repo then install both Docker and Docker-Compose. 

- Intrusctions on forking a repo
    - https://docs.github.com/en/github/getting-started-with-github/fork-a-repo

- Instruction on cloning a repo
    - https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository

- Instructions for installing Docker can be found here:
  - https://docs.docker.com/get-docker/

- Instructions for docker-compose here (you must install docker first):
  - https://docs.docker.com/compose/install/
  - This comes with Docker Desktop for Mac and Windows in the previous step

Once those two components are installed you should be good to go.  The compose file 
will spin up 7 different docker containers on your local machine.  At the end of 
its execution each container will have all the necessary files and dependencies loaded
so you do not need to install Python, Kafka, or Redis to run this app even though
it uses all three.

After installation, navigate to the portfolio 
directory in your preferred shell and type `docker-compose up -d` (depending on how
docker was set up you might need to run this command as an admin)

After all of the docker containers are up, navigate to `localhost:8000` in a web browser.  You'll need to register
an account and sign in to get to the main page.

## Debugging

### Bind Mounts
For your convience while editing you can enable the bind mounts on the 4 python containers
(these are the producer, consumer, client, and tests containers).  By default the 
mounts are commented out as they cause the circleCI pipeline to fail, however if 
you uncomment the lines starting with the line that begins "volumes" and ending 
with the line that begins "target" you will be able to make changes to the code 
on your local machine and have those immediately reflected in the corresponding 
code on the container.  

### Reload
If you further set the reload variable in ~/portfolio/ui/gunicorn_config.py to 
True the code you change on your local computer will be immediately reflected in
the UI.

### Loglevel
In the same `gunicorn_config.py` file you can set the granularity of log output as
well as where those logs go.  The default setting of "-" sends the log to the standard
output which allows you to access it with the `docker-compose logs -f -t [container name]`
command.  See more details about this command below.

## Useful Docker Commands
### docker-compose
`docker-compose up -d` is the easiest way to launch the application however there
are some other userful commands you should be aware of.  

To view the logs of a given container you launched with docker-compose use: 
`docker-compose logs [-f] [-t] [container name]`
    i.e. `docker-compose logs -f -t client` will show you the same output you see
    on your terminal when you run flask run
    `-f` means follow, it will show you all the current log messages and continue
    to display new messages as they come in until you hit ctrl c
    `-t` adds a timestamp to your messages

To take down all of your containers use:
`docker-compose down`
    this will both stop and remove all of your containers so you will not be able
    to view the log files after doing this

To rebuild one of the images in the docker-compose file
`docker-compose build [service name]`

### Docker
When you only want to do something to one of your containers you use the docker 
command

`docker stop [container name]` for instance will stop (and not remove) just one container
    i.e. docker stop client would stop the client container

`docker ps` shows you all your currently running containers

`docker run [container name]` will start up just one container
    be aware that this command usually take a log of arguments which are set in 
    the docker-compose file for your (and my) convience.  To mimick the client 
    docker container that gets setup in the compose file for instance you would 
    run the command:
        `docker run --name client -d -p 8000:5000 --rm client:latest`
            `--name` designates the name of your container in the above example the
            name was client
            `-d` runs the container in the background after it is up, if you do not
            add this argument the terminal will not return control to you
                this is also true for the docker-compose command
            `-p` designates the ports for the container in the above container 8000
            is the external port and 5000 is the port for other docker containers
            on this network
            `--rm` will remove your docker container after you stop it
            client:latest is the name of the docker image you are going to use to 
            run this container.  This is the only manditory argument in this command
            client:latest is the name of the docker image that must of been previously 
            built.  See below command.  This is the only mandatory argument.

`docker build -t [image name]` will build your docker image from a dockerfile. To 
    build the same image used in the client container of docker-compose we would 
    use this command:
        `docker build -t client:latest . --file ui/Dockerfile_client`
        `-t` stands for tag, it names the image you are going to build this must 
        match the name used in the docker run command.
        `.` declares the base directory where the container is to be build
        `--file docker` natually looks for a file called Dockerfile in the base directory
        if this is not the name and or location of your file you need to specify it

`docker network ls` will list all of the docker networks on your machine.
    When you use docker compose all your containers are attached to the same network
    by default.  If you do not name this network in your docker-compose file the 
    name becomes the name of the directory docker-compose.yml is in with "_default" 
    appended.
        i.e. the network of this docker-compose file will be portfolio_default


`docker network inspect [network name]`
    gives you more information about your network including which containers are 
    a part of it.

`docker exec -it [container name] bash`
    will ssh you into a bash shell of your chosen container.  The bash command can 
    be almost any command line command
        i.e. docker exec -it client python will open the python intepreter on the 
        client container.