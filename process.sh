#!/usr/bin/env bash

###################################
function inf  { >&2 printf "\033[34m[+]\033[0m %b\n" "$@" ; }
function warn { >&2 printf "\033[33m[!]\033[0m %b\n" "$@" ; }
function err  { >&2 printf "\033[31m[!]\033[0m %b\n" "$@" ; }
function err! { err "$@" && exit 1; }

unset EXIT_RES
ON_EXIT=("${ON_EXIT[@]}")

function on_exit_fn {
  EXIT_RES=$?
  for cb in "${ON_EXIT[@]}"; do $cb || true; done
  # read might hang on ctrl-c, this is a hack to finish the script for real
  clear_exit
  exit $EXIT_RES
}

function on_exit {
  ON_EXIT+=("$@")
}

function clear_exit {
  trap - EXIT SIGINT
}

trap on_exit_fn EXIT SIGINT

ACTION=${ACTION}

PROCESS=$(basename $0)
L_PATH=$(dirname $(realpath $0))
P_CHANNEL_ID=${P_CHANNEL_ID}
P_SURVEY_ID=${P_SURVEY_ID}


function usage {
  cat << EOF
           $PROCESS: USACE to WWW

Usage: $PROCESS action [options...]

Options:
  -V, --verbose     echo every command that gets executed
  --channel-id      filter by channel id (ex: CENAN_JI_01_INL)
  --survey-id       filter by survey id (ex: JI_01_INL_20250501_CS_5560_60)
  --                stop reading arguments
  -h, --help        display this help

Commands:
  help                            Show usage
  download                        Download surveys (based on filters)
  extract                         Extract survey data
  preview                         Generate a preview of survey data
  crs                             Get CRS used in survey as EPSG

  Example:
    $ ./$PROCESS download --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./$PROCESS extract --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./$PROCESS preview --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./$PROCESS do --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./$PROCESS preview --survey-id JI_01_INL_20250501_CS_5560_60 -- --help
    $ ./$PROCESS preview --survey-id JI_01_INL_20250501_CS_5560_60 -- \\
            --grid-res 50 --distance-filter 100
    $ ./$PROCESS do --survey-id JI_01_INL_20250501_CS_5560_60 -- \\
            --grid-res 50 --distance-filter 100 \\
            -o foo.tif
    $ ./$PROCESS crs --survey-id JI_01_INL_20250501_CS_5560_60

EOF
}


function parse_args {
  _ARGS=()
  _NP_ARGS=()

  ! [[ $1 =~ ^- ]] && ACTION=$1 && shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -V|--verbose)
        set -x
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --channel-id)
        P_CHANNEL_ID=$2
        shift
        ;;
      --survey-id)
        P_SURVEY_ID=$2
        shift
        ;;
       -)
        _ARGS+=("$(cat "$2")")
        shift
        ;;
      --)
        shift
        _NP_ARGS+=("$@")
        break
        ;;
      *)
        _ARGS+=("$1")
        ;;
    esac
    shift
  done
}


function process_q {
  duckdb -noheader -list << EOF
    SELECT ${1:-"*"} FROM read_csv('surveys.csv')
    WHERE true
      ${P_CHANNEL_ID:+"AND channelareaidfk = '$P_CHANNEL_ID'"}
      ${P_SURVEY_ID:+"AND surveyjobidpk = '$P_SURVEY_ID'"}
EOF
}

function crs {
  while read -r line; do
          IN_CRS=$(python << EOF
from pyproj import CRS
crs = CRS.from_user_input("$line")
print(crs.to_epsg())
EOF
)
    break
  done < <(process_q "sourceprojection")
  echo EPSG:$IN_CRS
}

function main {
  parse_args "$@"

  # re-set action arguments after parsing.
  # access action arguments as $1, $2, ... in order
  set -- "${_ARGS[@]}"

  case $ACTION in
      populate)
        [[ -f surveys.csv ]] || python surveys.py > surveys.csv
        ;;
      download)
        # downlads data to surveys folder.
        # Extracted data is in surveys/data
        # Does not download if filename exists
        mkdir -p $L_PATH/surveys/data
        process_q "sourcedatalocation" | parallel --bar -j 10 'curl -s -L --create-dirs -o surveys/{/} {}'
        ;;
      extract)
        pushd $L_PATH/surveys
          unzip -j '*.ZIP' "*.XYZ" -x "*FULL.XYZ" -d data
        popd
        ;;
      preview)
        files=()
        while read -r line; do
          files+=("surveys/data/$line.XYZ")
        done < <(process_q "surveyjobidpk")
        python totiff.py ${files[@]} $@ ${_NP_ARGS[@]} --preview
        ;;
      do)
        files=()
        while read -r line; do
          files+=("surveys/data/$line.XYZ")
        done < <(process_q "surveyjobidpk")
        python totiff.py ${files[@]} $@ ${_NP_ARGS[@]}
        ;;

      crs)
        crs
        ;;
      help)
        usage
        ;;
      *)
        usage
        exit 1
        ;;
  esac
}

main "$@"
