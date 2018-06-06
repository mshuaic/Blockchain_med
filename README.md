#### install docker
* [install docker](https://docs.docker.com/install/)

* pull containter

  `$ docker pull mshuaic/blockchainnode`
* create a folder in your local machine

  `$ mkdir multichain`
* run master node

  ``$ docker run -ti --name node0 -v `pwd`/multichain:/root/.multichain mshuaic/blockchainnode``

* run other node

  `$ docker run -ti --name node1 mshuaic/blockchainnode`
* exit container

  `$ exit`
* re-start cotainter

  `$ docker start -i node0`

* show all running containers

  `$ docker ps -a`

* kill all running containers

  `$ docker kill $(docker ps -aq)`

* remove all containers

  `$ docker rm $(docker ps -aq)`

After you exit, Docker **DOES NOT** save any change you made in your system.
If you want to save your change in docker container, check this [docker commit](https://docs.docker.com/engine/reference/commandline/commit/#examples)

#### inside docker container
* [Download and Install Multichain](https://www.multichain.com/download-install/)

* [Multichain Tutorial](https://www.multichain.com/getting-started/)

* [Multichain Explorer](https://github.com/MultiChain/multichain-explorer)

  After you installed MultiChain Explorer in the docker container, you need to
  forward web port(default: 2750) to the host.
    * commit your current container

       [docker commit](https://docs.docker.com/engine/reference/commandline/commit/#examples)
    * re-run

        ``$ docker run -ti --name node0 -v `pwd`/multichain:/root/.multichain -p 2750:2750 mshuaic/blockchainnode``

        more detail:
        [docker networking](https://docs.docker.com/config/containers/container-networking/)
