#### install docker
* [install docker](https://docs.docker.com/install/)

* pull containter

  `$ docker pull mshuaic/blockchainnode`
* create a folder in your local machine

  `$ mkdir multichain`
* run master node

  ``$ docker run -ti --name node0 -v `pwd`/multichain:/root/.multichain mshuaic/blockchainnode``

* run other node0

  `$ docker run -ti --name node1 mshuaic/blockchainnode`
* exit container

  `$ exit`
* re-start cotainter

  `$ docker start -i node0`

After you exit, Docker **DOES NOT** save your any change you made in your system.
If you want to save your change in docker container, check this [docker commit](https://docs.docker.com/engine/reference/commandline/commit/#examples)

#### inside docker container
* [Download and Install Multichain](https://www.multichain.com/download-install/)

* [Multichain Tutorial](https://www.multichain.com/getting-started/)

* [Multichain Explorer](https://github.com/MultiChain/multichain-explorer)
