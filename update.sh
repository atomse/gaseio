#!/bin/bash

name=$(cd `dirname $0`; pwd) 
project=$(basename $name)



HOSTS="work bwg"
echo $project
for i in dist/${project}*.whl;
do
	fname=`basename $i`
	for host in `echo $HOSTS`; 
	do
		# scp -P 5522 $i ${host}.atomse.net:/tmp/$fname
		ssh -p 5522 ${host}.atomse.net \
        "bash -c \"\
            source /app/${project}/bin/activate; \
            pip uninstall -yy ${project}; \
            sudo -u gase /app/gaseio/bin/pip install /tmp/${fname}; \
            # rm -f /tmp/$fname; \" \
            sudo supervisorctl restart gaseio; \
        "
	done
done


