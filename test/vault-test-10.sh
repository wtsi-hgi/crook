#!/usr/bin/env bash


declare ROOT="$(mktemp -d)"
mkdir -p "${ROOT}/.vault/.staged"

function create_file {
    declare FILE="my_test_file_$1"
    touch "${ROOT}/${FILE}"
    declare FILE_INODE
    printf -v FILE_INODE "%x" "$(stat -f %i "${ROOT}/${FILE}")"
    (( ${#FILE_INODE} % 2 )) && FILE_INODE="0${FILE_INODE}"
    declare ENCODED="$(printf "%s" "${FILE}" | base64)"
    declare VAULT_PATH="$(printf "%s" "${FILE_INODE}" | fold -w2 | paste -sd/ - )-${ENCODED}"
    mkdir -p "${ROOT}/.vault/.staged/$(dirname "${VAULT_PATH}")"
    ln "${ROOT}/${FILE}" "${ROOT}/.vault/.staged/${VAULT_PATH}" 
    echo -n "${ROOT}/.vault/.staged/${VAULT_PATH}"
}


for i in {1..10}
do
    result="$(create_file  ${i})\0${result}"
done
echo -ne "$result"