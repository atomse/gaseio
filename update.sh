#!/bin/bash

name=$(cd `dirname $0`; pwd) 
project=$(basename $name)
username=gase


HOSTS="work bwg"
echo $project
for i in dist/${project}*.whl;
do
	fname=`basename $i`
	for host in `echo $HOSTS`; 
	do
		scp -P 5522 $i ${host}.atomse.net:/tmp/$fname
		ssh -p 5522 ${host}.atomse.net \
        bash -c "\"\
            source /app/${project}/bin/activate; \
            export HOME=/home/${username}; \
            sudo -u ${username} /app/${project}/bin/pip uninstall -yy ${project}; \
            ping -c 1 -W 1 free.atomse.xyz && sudo -u ${username} /app/${project}/bin/pip install http://free.atomse.xyz/qcdata-1.1.0-py2.py3-none-any.whl|| sudo -u ${username} /app/${project}/bin/pip install http://bwg.atomse.net/qcdata-1.1.0-py2.py3-none-any.whl;
            sudo -u ${username} /app/${project}/bin/pip install /tmp/${fname}; \
            rm -f /tmp/$fname;  \
            sudo supervisorctl restart ${project}; \""
	done
done


