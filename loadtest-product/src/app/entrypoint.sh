#!/bin/bash

set | grep LOCUST_

LOCUST=( "locust" )

LOCUST+=( -f ${LOCUST_SCRIPT:-/locust-tasks/tasks.py} )
LOCUST+=( --headless )

if [[ ! -v $LOCUST_USERS ]]; then
    LOCUST+=( -u  $LOCUST_USERS )
else
    LOCUST+=( -u  500 )
fi

if [[ ! -v $LOCUST_HATCH_RATE ]]; then
    LOCUST+=( -r  $LOCUST_HATCH_RATE )
else
    LOCUST+=( -r  10 )
fi

if [[ ! -v $LOCUST_RUN_TIME ]]; then
    LOCUST+=( -t  $LOCUST_RUN_TIME )
else
    LOCUST+=( -t  10m )
fi

LOCUST+=( --host=$LOCUST_TARGET_HOST )

if [[ ! -v $LOCUST_STEP_LOAD ]]; then
    LOCUST+=( --step-load )
fi

if [[ ! -v $LOCUST_STEP_USERS ]]; then
    LOCUST+=( --step-users  $LOCUST_STEP_USERS )
fi

if [[ ! -v $LOCUST_STEP_TIME ]]; then
    LOCUST+=( --step-time  $LOCUST_STEP_TIME )
fi

echo "${LOCUST[@]}"

#replace bash, let locust handle signals
# shellcheck disable=SC2068
exec ${LOCUST[@]}