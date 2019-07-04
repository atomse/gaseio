#!/bin/bash

name=$(cd `dirname $0`; pwd) 
project=$(basename $name)
echo $project
for i in dist/${project}*.whl;
do
	fname=`basename $i`
	for host in `echo "work bwg"`; 
	do
		scp -P 5522 $i ${host}.atomse.net:
		ssh -p 5522 ${host}.atomse.net "bash -c \"sudo /usr/bin/python3 -m pip uninstall gaseio -yy; sudo /usr/bin/python3 -m pip install $fname; # rm -f $fname\""
	done
done



