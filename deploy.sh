#!/bin/bash

name=$(cd `dirname $0`; pwd) 
project=$(basename $name)
echo $project
for i in dist/${project}*.whl;
do
	fname=`basename $i`
	for host in `echo "work bwg"`; 
	do
		scp -P 5522 $i ${host}.atomse.net:/tmp/$fname
		ssh -p 5522 ${host}.atomse.net "bash -c \"pip3 uninstall gaseio -yy; pip3 install /tmp/$fname || pip3 install /tmp/$fname --user ; rm -f /tmp/$fname\""
	done
done



