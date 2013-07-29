#!/bin/sh


KVDB_PATH="/tmp/sae-pabo-blog.kvdb"
HOST="localhost"
PORT=8888


if [ ! -f $KVDB_PATH ]; then  
    echo "(dp0\n." > $KVDB_PATH
    chmod +rw $KVDB_PATH
fi


echo "tornado servering on http://${HOST}:${PORT}"
dev_server.py --host=$HOST -p $PORT --kvdb-file=$KVDB_PATH
