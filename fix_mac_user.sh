#!/bin/sh                                                                                                                    

BULKERDIR=`dirname $BULKERCFG`
cd $BULKERDIR/templates
echo "$USER:x:$(id -u):$(id -g):ns,,,:$HOME:/bin/bash" > mac_passwd
sed "s|/etc/passwd|$BULKERDIR/templates/mac_passwd|" docker_executable.jinja2 > docker_executable_mac.jinja2
sed -i .bak "s|docker_executable.jinja2|docker_executable_mac.jinja2|" $BULKERCFG
sed "s|/etc/passwd|$BULKERDIR/templates/mac_passwd|" docker_shell.jinja2 > docker_shell_mac.jinja2
sed -i .bak "s|docker_shell.jinja2|docker_shell_mac.jinja2|" $BULKERCFG
