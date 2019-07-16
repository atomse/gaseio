#!/bin/bash


# create user 
adduser gase

mkdir -p /home/gase/chemio


name=$(cd `dirname $0`; pwd) 
project=$(basename $name)
username=gase

# Install virtualenv

virtualenv > /dev/null

[ $? ] && pip3 install virtualenv


# Create ${project} virtualenv

[ -e /app/${project} ] || $(mkdir -p /app/log; \
chown $username:$username /app/*  -R ; \
cd /app ;\
sudo -u ${username} virtualenv ${project} -p python3.6; )


supervisorctl -h > /dev/null 

[ $? ] && $(yum install supervisor || apt install supervisor)



[ -d /etc/supervisor/conf.d ] && dirname=/etc/supervisor/conf.d && conf_file=/etc/supervisor/supervisord.conf
[ -d /etc/supervisord.d/ ] && dirname=/etc/supervisord.d/ && conf_file=/etc/supervisord.conf
[ ! $dirname -o ! $conf_file ] && exit 1
[ "$(grep 'files = ' $conf_file | grep '\*\.conf')" != "" ] && filename=supervisor_${project}.conf
[ "$(grep 'files = ' $conf_file | grep '\*\.ini')" != "" ] && filename=supervisor_${project}.ini



cat > ${dirname}/${filename} << EOF
[program:${project}]
directory=/tmp ; 程序的启动目录
command=/app/${project}/bin/python -m ${project}.server # --port=5000 ; 启动命令，与手动在命令行启动的命令是一样的，注意这里home不可用~代替
autostart=true     ; 在 supervisord 启动的时候也自动启动
startsecs=5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart=true   ; 程序异常退出后自动重启
startretries=3     ; 启动失败自动重试次数，默认是 3
user=gase          ; 用哪个用户启动
redirect_stderr=true  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 20MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 20     ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /app/log/${project}.log
loglevel=info
EOF

