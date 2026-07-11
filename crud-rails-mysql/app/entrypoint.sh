#!/bin/sh
set -e

# MySQL may still be starting when this container boots — retry the migration
# instead of crashing, mirroring the connection retry the Flask Templates use.
attempts=0
until bundle exec rake db:migrate; do
  attempts=$((attempts + 1))
  if [ "$attempts" -ge 15 ]; then
    echo "Could not connect to MySQL after 15 attempts" >&2
    exit 1
  fi
  echo "MySQL not ready yet — retrying in 2s ($attempts/15)"
  sleep 2
done

exec bundle exec puma -b tcp://0.0.0.0:3000
