[![Gitter](https://badges.gitter.im/watchit-app/community.svg)](https://gitter.im/watchit-app/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# Getting started
* If you don’t have Go, [install it](https://golang.org/doc/install).
* If you don’t have IPFS , [install it](https://github.com/ipfs/go-ipfs#install).
* [How to spawn an IPFS node in Node.js and in the Browser](https://mrh.io/2018-01-24-pushing-limits-ipfs-orbitdb/) 
* [How to spawn an IPFS private node and generate swarm key](https://mrh.io/ipfs-private-networks/) 



# watchit-gateway
Gateway Watchit Seeder

## How

*Start docker containers and starts movies migration.*
> Init and start bootstrap ipfs node. 
> (Please wait until movies get ready migrated).

`docker-compose up`

# watchit-app

*After run migration and expose our node in gateway*

Please copy entry hash in `clients` file located in your root directory and the `private key` as well. This keys will be requested on app login. 

*To configure your app please*

> Get ipfs "node id" using `docker-compose exec watchit_ipfs ipfs id -f=<id>`.
* `BOOTSTRAP_IP = {GATEWAY_IP} `
* `BOOTSTRAP_HASH = {IPFS_NODE_ID}`
> In [this file](https://github.com/ZorrillosDev/watchit-desktop/blob/master/public/lib/settings/orbit.js) set your ENV variables. 




