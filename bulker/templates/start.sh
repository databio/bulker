source "${BULKERSHELLRC}"
echo $BULKERPROMPT
if [ -z ${BULKERPROMPT+x} ]; then echo "No prompt change"; else PS1="${BULKERPROMPT}"; fi
export PATH="${BULKERPATH}:${PATH}"
