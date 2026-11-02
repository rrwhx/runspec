#!/bin/bash
# Source: https://github.com/rrwhx/runspec

set -euo pipefail
shopt -s nullglob

usage() {
    cat <<EOF
Usage: $0 [all|suffix-pattern ...]

Run from the SPEC root directory. No arguments means all base/peak builds.
Patterns match suffixes beginning with _base or _peak, not benchmark names.
Literal suffixes and shell wildcards (*, ?, [...]) are supported.
Quote patterns to prevent expansion by your shell.

Examples:
  $0
  $0 '_base*'
  $0 '*gcc*' '*clang*'
  $0 '_base.my_config'

Output: ./<current-directory>_exe/<actual-suffix-without-leading-underscore>/
EOF
}

if [[ ${1-} == -h || ${1-} == --help ]]; then
    usage
    exit 0
fi
if [[ ${1-} == -- ]]; then
    shift
fi
if [[ $# -eq 0 ]]; then
    set -- all
fi

patterns=("$@")
matched=()
for pattern in "${patterns[@]}"; do
    if [[ -z "$pattern" ]]; then
        printf 'Error: suffix patterns must not be empty.\n' >&2
        exit 1
    fi
    matched+=(0)
done

# Discover actual suffixes from filenames; do not parse ls output.
# Collect the selection before writing, so a typo does not produce partial output.
selected_files=()
selected_suffixes=()
for file in benchspec/*/*/exe/*; do
    [[ -f "$file" ]] || continue
    filename=${file##*/}
    [[ "$filename" =~ (_(base|peak).*)$ ]] || continue
    suffix=${BASH_REMATCH[1]}
    selected=0
    for ((i = 0; i < ${#patterns[@]}; i++)); do
        pattern=${patterns[i]}
        # The unquoted RHS enables glob matching; the leading * preserves
        # the original behavior of accepting a literal trailing suffix.
        if [[ "$pattern" == all || "$suffix" == *$pattern ]]; then
            matched[i]=1
            selected=1
        fi
    done
    if [[ "$selected" -eq 1 ]]; then
        selected_files+=("$file")
        selected_suffixes+=("$suffix")
    fi
done

for ((i = 0; i < ${#patterns[@]}; i++)); do
    if [[ "${matched[i]}" -eq 0 ]]; then
        printf 'Error: no base/peak executables match suffix pattern %q under benchspec/*/*/exe/. Run from the SPEC root directory.\n' "${patterns[i]}" >&2
        exit 1
    fi
done

output_root="./$(basename "$PWD")_exe"
for ((i = 0; i < ${#selected_files[@]}; i++)); do
    file=${selected_files[i]}
    suffix=${selected_suffixes[i]}
    target_dir="${output_root}/${suffix#_}"
    if [[ ! -d "$target_dir" ]]; then
        mkdir -p "$target_dir"
    fi
    printf 'Copying %s -> %s/\n' "$file" "$target_dir"
    cp "$file" "${target_dir}/"
done

printf 'Copied %s executables to %s\n' "${#selected_files[@]}" "$output_root"
