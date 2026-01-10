#!/bin/bash
# SPEC CPU Benchmark Runner
# Enhanced version with colorized output and parameter validation

# Set environment limits
ulimit -s 2000000
ulimit -c unlimited

# Color definitions
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

# Detect SPEC version
detect_spec_version() {
    if [ -d "benchspec/CINT2000/" ]; then
        echo "2000"
    elif [ -d "benchspec/CPU2006/" ]; then
        echo "2006"
    elif [ -d "benchspec/CPU/" ]; then
        echo "2017"
    else
        echo -e "${RED}ERROR: Not a valid SPEC CPU directory${NC}" >&2
        exit 1
    fi
}

# Display help information
show_usage() {
    spec="$1"
    echo -e "\n${CYAN}SPEC CPU $spec Benchmark Runner${NC}"
    echo -e "${GREEN}Usage:${NC}"
    echo -e "  ./run.sh <config_file> <data_size> <runs> <benchmark_type> [options]"
    echo -e "\n${GREEN}Parameters:${NC}"
    echo -e "  ${YELLOW}1. Config file${NC} (Available: ${CYAN}$(ls config/*.cfg | xargs -n1 basename)${NC})"
    echo -e "  ${YELLOW}2. Data size${NC}:   ${CYAN}test${NC}, ${CYAN}train${NC}, or ${CYAN}ref${NC}"
    echo -e "  ${YELLOW}3. Run count${NC}:   Positive integer"
    
    case "$spec" in
        "2000"|"2006")
            echo -e "  ${YELLOW}4. Benchmark type${NC}: ${CYAN}int${NC}, ${CYAN}fp${NC}, or ${CYAN}all${NC}"
            ;;
        "2017")
            echo -e "  ${YELLOW}4. Benchmark type${NC}: ${CYAN}intrate${NC}, ${CYAN}fprate${NC}, or ${CYAN}specrate${NC}"
            ;;
    esac
    
    echo -e "  ${YELLOW}Options${NC}:       e.g., ${CYAN}--rate 4${NC}, ${CYAN}--copies 4${NC}"
    
    print_benchmark_list "$spec"
}

print_benchmark_list() {
    spec="$1"
    echo -e "\n${GREEN}Available Benchmarks:${NC}"
    case "$spec" in
        "2000")
            echo -e "${YELLOW}Integer Suite:${NC}"
            echo "  164.gzip 175.vpr 176.gcc 181.mcf 186.crafty 197.parser"
            echo "  252.eon 253.perlbmk 254.gap 255.vortex 256.bzip2 300.twolf"
            echo -e "\n${YELLOW}Floating Point Suite:${NC}"
            echo "  168.wupwise 171.swim 172.mgrid 173.applu 177.mesa"
            echo "  178.galgel 179.art 183.equake 187.facerec 188.ammp"
            echo "  189.lucas 191.fma3d 200.sixtrack 301.apsi"
            ;;
        "2006")
            echo -e "${YELLOW}Integer Suite:${NC}"
            echo "  400.perlbench 401.bzip2 403.gcc 429.mcf 445.gobmk"
            echo "  456.hmmer 458.sjeng 462.libquantum 464.h264ref 471.omnetpp"
            echo "  473.astar 483.xalancbmk"
            echo -e "\n${YELLOW}Floating Point Suite:${NC}"
            echo "  410.bwaves 416.gamess 433.milc 434.zeusmp 435.gromacs"
            echo "  436.cactusADM 437.leslie3d 444.namd 447.dealII 450.soplex"
            echo "  453.povray 454.calculix 459.GemsFDTD 465.tonto 470.lbm"
            echo "  481.wrf 482.sphinx3"
            ;;
        "2017")
            echo -e "${YELLOW}SPECrate Integer Suite:${NC}"
            echo "  500.perlbench_r 502.gcc_r 505.mcf_r 520.omnetpp_r"
            echo "  523.xalancbmk_r 525.x264_r 531.deepsjeng_r 541.leela_r"
            echo "  548.exchange2_r 557.xz_r"
            echo -e "\n${YELLOW}SPECrate Floating Point Suite:${NC}"
            echo "  503.bwaves_r 507.cactuBSSN_r 508.namd_r 510.parest_r"
            echo "  511.povray_r 519.lbm_r 521.wrf_r 526.blender_r 527.cam4_r"
            echo "  538.imagick_r 544.nab_r 549.fotonik3d_r 554.roms_r"
            ;;
    esac
}

# Main script flow
SPEC_VERSION=$(detect_spec_version)

# Show help if no parameters
# Check parameter existence
if [ $# -eq 0 ]; then
    show_usage "$SPEC_VERSION"
    exit 0
elif [ $# -lt 4 ]; then
    echo -e "${RED}ERROR: Missing required parameters!${NC}"
    show_usage "$SPEC_VERSION"
    exit 1
fi

# Parameter validation
CONFIG_FILE="config/$(basename $1)"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}ERROR: Config file not found!${NC}"
    echo -e "Available configs: ${CYAN}$(ls config/*.cfg | xargs -n1 basename)${NC}"
    exit 1
fi

# Initialize SPEC environment
echo -e "\n${GREEN}Initializing SPEC environment...${NC}"
source shrc > /dev/null 2>&1

# Configure run command
if [ ! -d "${SPEC}/benchspec/CPU/" ]; then
    echo -e "${YELLOW}Performing directory relocation...${NC}"
    relocate
    RUN_CMD="runspec"
else
    RUN_CMD="runcpu"
fi

# Build command arguments
BASE_CMD="$RUN_CMD -c $(basename $1) -i $2 -n $3 ${@:4} -T base"
echo -e "\n${CYAN}Execution Command:${NC}"
echo -e "${YELLOW}$BASE_CMD${NC}"

# Run benchmarks
echo -e "\n${GREEN}Starting benchmark run at${NC} ${CYAN}$(date)${NC}"
eval $BASE_CMD
echo -e "\n${GREEN}Completed benchmark run at${NC} ${CYAN}$(date)${NC}"

