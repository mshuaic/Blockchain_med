# Overview

This project is for [iDash Blockchain Competition](http://www.humangenomeprivacy.org/2018/competition-tasks.html):
Blockchain-based immutable logging and querying for cross-site genomic dataset access audit trial.

# Environment
- tested in MacOS 10.13 and Ubuntu 16.0.4
- Python 3
- [install fq](https://stedolan.github.io/jq/). 
- [install docker](https://docs.docker.com/install/)

# Scripts

#### configuration
- `create_node.sh` genrating nodes... ??
- `clean.sh` cleaning the temporary nodes ... ??

#### data storage and query implementation 
- `baseline.py`
- `baseline1.py`
- `baseline2.py`

see [our solution](#our-solution)

#### Addition file
* `config.py`: rpc credentials, data directory
* `util.py`: provides utility function
* `Savoir.py`: python Json-RPC wrapper
* `benchmark.py`: benchmark test suite

# our solution
Data Storage (Insertion) and Query Implementation.

- `baseline1.py`

Insert a record:  
For the i-th attribute in the record, we store key = i-th attribute and value = plaintext of record.
Hence, the plaintext of the record is duplicated k times where k is the amount of attributes.

Query:  
For a query with timestamp-range, we transform it into the _union_ of multiple single-time-point query.  
For a query with multiple attributes combined by AND, we transform it into the _intersection_ of multiple single-attribute queries.  
For a single-attribute (or single-time-point) query, we return the value(s) w.r.t. the key (i.e, the given attribute).  

- `baseline2.py`

Insert a record:  
First, we store the record as key = `SHA1` hash of record, value = plaintext of record.  
Then, we store its k attributes info as key =  hash of i-th attributes, value = `SHA1` hash of the record; hence, the hash of this record (instead of the plaintext) is duplicated k times. 

Query:  
similar to `baseline1`.


# Run Benchmark
#### Step 1
Download git repo and docker file

    $ git clone https://github.com/mshuaic/Blockchain_med
    $ docker pull mshuaic/blockchainnode

The docker file has already been configured with Multichain 1.0.4. 

#### Step 2

Automatically create nodes and run multichain and it will run multichain-explorer on the first node.

    $ bash create_node.sh

Now, you should be able to view multichain on http://127.0.0.1:2750

You can also create nodes with parameters. The following is an example creating 4 nodes and rpcports are 8570, 8571, 8572, 8573.
The name of blockchain is _chain1_.
  
    $ bash create_node.sh node 4 8570 chain1

`clean.sh` cleans up all nodes and container. If you are already running nodes, you can clean up using *clean.sh*

    bash clean.sh

#### Step 3
Run benchmark. You can specify which baseline program you want to test.

    python main.py baseline1
    python main.py baseline2



# Appendix: Manually Configure Docker
* [config node](#inside-docker-container)
* [remote rpc](#remote-rpc)
* [automation script](#automation-script)

### install docker
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

### inside docker container
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

### Remote rpc

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

### automation script
* [install docker](#install-docker)
* pull blockchainnode

      $ docker pull mshuaic/blockchainnode

* run script. Script will automatically create nodes and run multichain and it
will run multichain-explorer on the first node.

      $ bash create_node.sh node 4 8570 chain1

  This example creates 4 nodes and rpcports are 8570, 8571, 8572, 8573. The name
  of blockchain is _chain1_.

  Now, you should be able to view multichain on http://127.0.0.1:2750
* clean.sh cleans up all nodes and container
