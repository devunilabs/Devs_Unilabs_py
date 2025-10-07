#!/bin/bash
if [ ! "$(pidof main.py)" ]
then
cd  /home/unilabs/unilabs_csv_to_genesys-main
. /etc/profile.d/informix.sh
python3.12 main.py
fi

