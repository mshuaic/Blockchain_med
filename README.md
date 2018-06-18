## Menu
* [install docker](#install-docker)
* [config node](#inside-docker-container)
* [remote rpc](#remote-rpc)
* [automation script](#automation-script)

## install docker
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

## inside docker container
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

## Remote rpc

All you need to do is add the RPC port number. Copy the default-rpc-port value from params.dat and add an entry to multichain.conf as follows:

    cd ~/.multichain/chain1/
    grep rpc params.dat
    # Make a note of the default-rpc-port value, let's say it's 1234, and add it to multichain.conf
    echo "rpcport=1234" >> multichain.conf

Allow any ip to connect to node

    echo "rpcallowip=0.0.0.0/0" >> multichain.conf

Re-run docker container with port mapping

    $ docker run -ti --name node0 -v `pwd`/multichain:/root/.multichain -p 2750:2750 -p 1234:1234 mshuaic/blockchainnode

Now you can make JSON-RPC call to node remotely with python wrapper such as [Savoir](https://github.com/DXMarkets/Savoir).

Check your rpc username and password

    $ cat multichain.conf

Assuming your host ip is _1.2.3.4_, username is _user_, password is _pswd_, and chainname is _chain1_

    from Savoir import Savoir
    rpcuser = 'user'
    rpcpasswd = 'pswd'
    rpchost = '1.2.3.4'
    rpcport = '1234'
    chainname = 'chain1'

    api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)
    print(api.getinfo())

## automation script
* [install docker](#install-docker)
* pull blockchainnode

      $ docker pull mshuaic/blockchainnode

* run script. Script will automatically create nodes and run multichain and it
will run multichain-explorer on the first node.

      $ create_node.sh node 4 8570 chain1

  Now, you should be able to view multichain on http://127.0.0.1:2750
* clean.sh cleans up all nodes and container
