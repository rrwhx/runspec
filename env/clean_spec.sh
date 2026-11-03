#!/usr/bin/env bash
# Source: https://github.com/rrwhx/runspec
# Usage: clean_spec.sh [directory ...] [exe]

remove_exe=0
targets=()
for arg in "$@"; do
    if [[ "$arg" == exe ]]; then
        remove_exe=1
    else
        targets+=("$arg")
    fi
done
if [[ ${#targets[@]} -eq 0 ]]; then
    targets=(.)
fi

status=0
for target in "${targets[@]}"; do
    if [[ ! -d "$target" || ! -d "$target/benchspec" || ! -d "$target/config" || ! -f "$target/shrc" ]]; then
        printf 'Error: skipping invalid SPEC directory (requires benchspec/, config/ and shrc file): %s\n' "$target" >&2
        status=1
        continue
    fi

    printf 'Cleaning: %s\n' "$target"
    target_status=0
    rm -rf -- "$target"/result/ "$target"/tmp/ "$target"/config/*cfg.* \
        "$target"/benchspec/*/*/run_*/ \
        "$target"/benchspec/*/*/run/ \
        "$target"/benchspec/*/*/build/ || target_status=1
    if [[ "$remove_exe" -eq 1 ]]; then
        printf 'Removing executables: %s\n' "$target"
        rm -rf -- "$target"/benchspec/*/*/exe/ || target_status=1
    fi
    if [[ "$target_status" -eq 0 ]]; then
        printf 'Cleaned: %s\n' "$target"
    else
        printf 'Error: cleanup failed: %s\n' "$target" >&2
        status=1
    fi
done

exit "$status"
