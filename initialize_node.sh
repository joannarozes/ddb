#!/usr/bin/env bash

# Available script params:
# -d : will delete current database

while getopts ":d" opt; do
    case $opt in
    d)
        rm db/station.db
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

python db/create_db.py
