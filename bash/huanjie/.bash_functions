#.bash_functions

BACK_CD_HISTORY=""
FORWARD_CD_HISTORY=""
KEEP_CD_HISTORY=100

# override the builtin cd function so it can trace back history
# use cd n to move forwards
# use cd -n to move backwards
# use lcd to list stored history
function cd {
    local DIR="."
    local BACK_HISTORY=$BACK_CD_HISTORY
    local FORWARD_HISTORY=$FORWARD_CD_HISTORY
    if [[ $# -eq 1 ]] && [[ $1 =~ ^[0-9-]+$ ]]; then
        local FORWARD_HISTORY_LENGTH=$(echo $FORWARD_CD_HISTORY | grep -o ":" | wc -l)
        local BACK_HISTORY_LENGTH=$(echo $BACK_CD_HISTORY | grep -o ":" | wc -l)
        if [[ $1 -gt 0 ]]; then
            # go forward
            if [[ $FORWARD_CD_HISTORY == "" ]]; then
                echo "You are at the frontier! Cannot move forward. Try 'lcd' to see the cache."
            else
                if [[ $1 -ge $FORWARD_HISTORY_LENGTH ]]; then
                    echo "Not enough forward history in the cache. Try 'lcd' to see the cache."
                else
                    for iDir in $( seq 1 $1 ); do
                        DIR=${FORWARD_HISTORY%%:*}
                        FORWARD_HISTORY=${FORWARD_HISTORY#*:}
                        BACK_HISTORY=$DIR:$BACK_HISTORY
                    done
                    DIR=${FORWARD_HISTORY%%:*}
                    if [[ -d "$DIR" ]]; then
                        FORWARD_CD_HISTORY=$FORWARD_HISTORY
                        BACK_CD_HISTORY=$BACK_HISTORY
                        builtin cd "$DIR"
                    fi
                fi
            fi
        elif [[ $1 -lt 0 ]]; then
            if [[ $(( -$1 )) -gt $BACK_HISTORY_LENGTH ]]; then
                echo "Not enough backward history in the cache. Try 'lcd' to see the cache."
            else
                if [[ $FORWARD_HISTORY_LENGTH -eq 0 ]]; then
                    DIR=$PWD
                    FORWARD_HISTORY=$DIR:$FORWARD_HISTORY
                fi
                for iDir in $(seq 1 $(( -$1 ))); do
                    DIR=${BACK_HISTORY%%:*}
                    BACK_HISTORY=${BACK_HISTORY#*:}
                    FORWARD_HISTORY=$DIR:$FORWARD_HISTORY
                done
                if [[ -d "$DIR" ]]; then
                    BACK_CD_HISTORY=$BACK_HISTORY
                    FORWARD_CD_HISTORY=$FORWARD_HISTORY
                    builtin cd "$DIR"
                fi
            fi
        else
            echo "Stay right here."
        fi
    else
        if [[ $KEEP_CD_HISTORY -gt 0 ]]; then
            BACK_CD_HISTORY=$PWD:$BACK_CD_HISTORY
            KEEP_CD_HISTORY=$(( $KEEP_CD_HISTORY - 1 ))
        else
            BACK_CD_HISTORY=$PWD:${BACK_CD_HISTORY%:*}
        fi
        FORWARD_CD_HISTORY=""
        builtin cd "$@"
    fi
}

# check the history in the stack
# only used for debugging
function checkcd
{
    echo "[BACK_CD_HISTORY]"
    echo $BACK_CD_HISTORY | tr ":" "\n"
    echo "[FORWARD_CD_HISTORY]"
    echo $FORWARD_CD_HISTORY | tr ":" "\n"
}

# list stored history
# calling cd after moving backwards will clear the future history
function lcd
{
    local CD_HISTORY_LENGTH=100
    if [[ $# -ge 1 ]]; then
        CD_HISTORY_LENGTH=$1
    fi
    local FORWARD_HISTORY_LENGTH=$(echo $FORWARD_CD_HISTORY | grep -o ":" | wc -l)
    local BACK_HISTORY_LENGTH=$(echo $BACK_CD_HISTORY | grep -o ":" | wc -l)
    local BACK_HISTORY=${BACK_CD_HISTORY%:*}
    local FORWARD_HISTORY=${FORWARD_CD_HISTORY%:*}
    local history=""
    if [[ $FORWARD_HISTORY_LENGTH -eq 0 ]]; then
        history=$(echo ${BACK_HISTORY} | tr ":" "\n" | tac | tr "\n" ":")
    else
        if [[ $BACK_HISTORY_LENGTH -gt 0 ]]; then
            history=$history$(echo ${BACK_HISTORY} | tr ":" "\n" | tac | tr "\n" ":")
        fi
        history=$history$(echo "${FORWARD_HISTORY%%:*} ")
        if [[ $FORWARD_HISTORY_LENGTH -gt 1 ]]; then
            history=$history:$(echo "${FORWARD_HISTORY#*:}")
        fi
    fi
    local line_numbers=$(echo -e "$(seq -$BACK_HISTORY_LENGTH -1)\n$(seq 0 $(($FORWARD_HISTORY_LENGTH-1)))")
    line_numbers=$(echo $line_numbers | sed '/^$/d' | tr " " "\n")
    local filenames=$(echo ${history} | tr ":" "\n")
    if [[ $FORWARD_HISTORY_LENGTH -le 1 ]]; then
        filenames=$filenames" "
    fi
    if [[ $FORWARD_HISTORY_LENGTH -eq 0 ]]; then
        (paste <(echo "$line_numbers")  <(echo "$filenames") --delimiters '\t')
    else
        (paste <(echo "$line_numbers")  <(echo "$filenames") --delimiters '\t') | grep "^.*\s$" -A $CD_HISTORY_LENGTH -B $CD_HISTORY_LENGTH
    fi
}

# fast advance to a directory containing a pattern
# not very fast in reality
function fcd
{
    if [[ $# -ge 1 ]]; then
        if [[ $1 == */* ]]; then
            cd "$(find . -path '*$1' -print -quit)"
        else
            cd "$(find . -type d -name $1 -print -quit)"
        fi
    fi
}

# up n levels
function up
{
    for i in $(seq 1 $1)
    do
        cd ..
    done
}

# cat the most recent file in a folder
function clast
{
    local dir="./"
    if [[ $# -ge 1 ]]; then
        dir=$1
    fi
    find $dir -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" " | xargs cat
}

# cat the most recent file in log folder
function clog
{
    clast ~/log
}

# data frame manipulation

# print csv file in tidy format
function dcsv
{
    cat $1 | perl -pe 's/((?<=,)|(?<=^)),/ ,/g;' | column -t -s, | less -S
    #perl -pe 's/((?<=,)|(?<=^)),/ ,/g;' "$@" | column -t -s, | exec less  -F -S -X -K
}

# print tsv file in tidy format
function dtsv
{
    perl -pe 's/((?<=\t)|(?<=^))\t/ \t/g;' "$@" | column -t -s $'\t' | exec less  -F -S -X -K
}

# transpose a matrix
function transpose
{
    if [[ $# -eq 1 && -f $1 ]]; then
        awk '
        {
            for (i=1; i<=NF; i++)  {
                        a[NR,i] = $i
            }
        }
        NF>p { p = NF }
        END {
           for(j=1; j<=p; j++) {
                str=a[1,j]
                for(i=2; i<=NR; i++){
                    str=str"\t"a[i,j];
                }
                print str
            }
        }' $1
    fi
}

# sort a data table by the given column
# inputs: $1: filename, $2: column index to sort (start from 1)
function dsort
{
    local column=1
    if [[ $# -ge 1 ]]; then
        if [[ $# -eq 1 ]]; then
            column=1
        else
            column=$2
        fi
        (head -n 1 $1 && (tail -n +2 $1 | sort -k${column}g)) | cat
    fi
}

# transfer the file to google shared drive
# you have to setup rclone first
# go to lab wiki to check how to do that
function tfdrive
{
    local drive="sudmantlab"
    OPTIND=1
    while getopts ":d:" opt; do
        case "$opt" in
            d) drive="${OPTARG}";;
            *) ;;
        esac
    done
    shift $((OPTIND-1))
    if [[ $# -ge 1 ]]; then
        local file=$1
        shift
        if [[ -f $file ]]; then
            rclone copy $@ $file ${drive}:projects/agingGeneRegulation/savio/$(date +'%Y%m%d')
        elif [[ -d $file ]]; then
            rclone copy $@ $file ${drive}:projects/agingGeneRegulation/savio/$(date +'%Y%m%d')/$(basename $file)
        else
            echo "$file: File/Folder not Found"
        fi
    else
        echo "No file/folder to be transferred"
    fi
}

# transfer files (obsolete but still in use)
function tfsudmant
{
    if [[ $# -eq 1 ]]; then
        rclone copy $1 sudmantlab:projects/agingGeneRegulation/savio/$(date +'%Y%m%d')
    fi
}
function tfberkeley
{
    if [[ $# -eq 1 ]]; then
        rclone copy $1 berkeley:sudmant/agingGeneRegulation/savio/$(date +'%Y%m%d')
    fi
}
