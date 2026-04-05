#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 9 ]; then
  echo "Usage:"
  echo "  $0 <host> <port> <user> <pass> <db> <warehouses> <vu> <rampup_min> <duration_min> [log_file]"
  exit 1
fi

HOST="$1"
PORT="$2"
DBUSER="$3"
DBPASS="$4"
DBNAME="$5"
WAREHOUSES="$6"
VU="$7"
RAMPUP="$8"
DURATION="$9"
LOG_FILE="${10:-hammerdb_${HOST}_$(date +%Y%m%d_%H%M%S).log}"

WORKDIR="$(mktemp -d)"
BUILD_TCL="$WORKDIR/build_tpcc.tcl"
RUN_TCL="$WORKDIR/run_tpcc.tcl"

cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

# Для build число build VU не должно превышать warehouses
BUILD_VU="$WAREHOUSES"

cat > "$BUILD_TCL" <<EOF
dbset db pg
dbset bm TPROC-C

diset connection pg_host $HOST
diset connection pg_port $PORT

diset tpcc pg_superuser $DBUSER
diset tpcc pg_superuserpass $DBPASS
diset tpcc pg_defaultdbase $DBNAME

diset tpcc pg_user $DBUSER
diset tpcc pg_pass $DBPASS
diset tpcc pg_dbase $DBNAME

diset tpcc pg_storedprocs true
diset tpcc pg_count_ware $WAREHOUSES
diset tpcc pg_num_vu $BUILD_VU

buildschema
EOF

cat > "$RUN_TCL" <<EOF
dbset db pg
dbset bm TPROC-C

diset connection pg_host $HOST
diset connection pg_port $PORT

diset tpcc pg_superuser $DBUSER
diset tpcc pg_superuserpass $DBPASS
diset tpcc pg_defaultdbase $DBNAME

diset tpcc pg_user $DBUSER
diset tpcc pg_pass $DBPASS
diset tpcc pg_dbase $DBNAME

diset tpcc pg_storedprocs true
diset tpcc pg_count_ware $WAREHOUSES
diset tpcc pg_num_vu $VU
diset tpcc pg_driver timed
diset tpcc pg_rampup $RAMPUP
diset tpcc pg_duration $DURATION

loadscript
vuset vu $VU
vucreate
vurun
EOF

{
  echo "===== BUILD SCHEMA ====="
  docker run --platform linux/amd64 --rm \
    -v "$WORKDIR:/work" \
    tpcorg/hammerdb:postgres \
    bash -lc "cd /home/hammerdb && ./hammerdbcli auto /work/$(basename "$BUILD_TCL")"

  echo
  echo "===== RUN TEST ====="
  docker run --platform linux/amd64 --rm \
    -v "$WORKDIR:/work" \
    tpcorg/hammerdb:postgres \
    bash -lc "cd /home/hammerdb && ./hammerdbcli auto /work/$(basename "$RUN_TCL")"
} | tee "$LOG_FILE"

echo "HammerDB log saved to: $LOG_FILE"