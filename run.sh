#!/bin/bash
ulimit -s unlimited
ulimit -c unlimited

if [ -d "benchspec/CINT2000/" ]
then
    spec="2000"
elif [ -d "benchspec/CPU2006/" ]
then
    spec="2006"
elif [ -d "benchspec/CPU/" ]
then
    spec="2017"
else
    echo "not an SPEC CPU diectory"
    exit 1
fi

if test -z $1 ; then
    echo -e "************************************************"
    echo -e "* @1 cfg filename in config directory: ${RED}`echo config/*.cfg`${NC}"
    echo -e "* @2 input data to run: ${RED}test${NC}, ${RED}train${NC}, or ${RED}ref${NC}"
    echo -e "* @3 number of times to run: integer, such as ${RED}1${NC}"
    if [[ "$spec" == "2000" ]]
    then
        echo -e "* @4 benchmarks: ${RED}int${NC}, ${RED}fp${NC} or ${RED}all${NC}"
    elif [[ "$spec" == "2006" ]]
    then
        echo -e "* @4 benchmarks: ${RED}int${NC}, ${RED}fp${NC} or ${RED}all${NC}"
    elif [[ "$spec" == "2017" ]]
    then
        echo -e "* @4 ${RED}intrate${NC} ${RED}fprate${NC} ${RED}specrate${NC}"
    fi
    echo -e "* @others options, default none, such as --rate --users 4/--rate 4/--copies 4"
    echo -e "* "
    if [[ "$spec" == "2000" ]]
    then
        echo -e "* benchmarks 2000"
        echo -e "* 1. one or more individual benchmarks, such as ${RED}175 176${NC}"
        echo -e "* 2. ${RED}int${NC} for the integer suite"
        echo -e "* 2. ${RED}fp${NC} for the floating point suite"
        echo -e "* 3. ${RED}all${NC} to run both the integer and the floating point suites."
        echo -e "*"
        echo -e "* SPEC CPU 2000"
        echo -e "*"
        echo -e "* ./run.sh <config_file> test 1 all"
        echo -e "* 2000 int:"
        echo -e "* "164.gzip", "175.vpr", "176.gcc", "181.mcf", "186.crafty", "197.parser", "252.eon", "253.perlbmk", "254.gap", "255.vortex", "256.bzip2", "300.twolf""
        echo -e "* 2000 fp:"
        echo -e "* "168.wupwise", "171.swim", "172.mgrid", "173.applu", "177.mesa", "178.galgel", "179.art", "183.equake", "187.facerec", "188.ammp", "189.lucas", "191.fma3d", "200.sixtrack", "301.apsi""
    elif [[ "$spec" == "2006" ]]
    then
        echo -e "* benchmarks 2006"
        echo -e "* 1. one or more individual benchmarks, such as ${RED}459 465${NC}"
        echo -e "* 2. ${RED}int${NC} for the integer suite"
        echo -e "* 2. ${RED}fp${NC} for the floating point suite"
        echo -e "* 3. ${RED}all${NC} to run both the integer and the floating point suites."
        echo -e "*"
        echo -e "* SPEC CPU 2006"
        echo -e "* ./run.sh <config_file> test 1 all"
        echo -e "*"
        echo -e "* 2006 int:"
        echo -e "* "400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk""
        echo -e "* 2006 fp:"
        echo -e "* "410.bwaves", "416.gamess", "433.milc", "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII", "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD", "465.tonto", "470.lbm", "481.wrf", "482.sphinx3""
    elif [[ "$spec" == "2017" ]]
    then
        echo -e "* benchmarks 2017"
        echo -e "* 1. one or more individual benchmarks, such as ${RED}500 502${NC}"
        echo -e "* 2. ${RED}intrate${NC} for the specrate integer suite"
        echo -e "* 2. ${RED}fprate${NC} for the specrate floating point suite"
        echo -e "* 3. ${RED}specrate${NC} to run both the specrate integer and the floating point suites."
        echo -e "*"
        echo -e "* SPEC CPU 2017"
        echo -e "*"
        echo -e "* ./run.sh <config_file> test 1 specrate"
        echo -e "* 2017 intrate:"
        echo -e "* "500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r", "523.xalancbmk_r", "525.x264_r", "531.deepsjeng_r", "541.leela_r", "548.exchange2_r", "557.xz_r""
        echo -e "* 2017 fprate:"
        echo -e "* "503.bwaves_r", "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r", "519.lbm_r", "521.wrf_r", "526.blender_r", "527.cam4_r", "538.imagick_r", "544.nab_r", "549.fotonik3d_r", "554.roms_r""
    fi
    echo -e "************************************************"

    exit
fi

config=`basename $1`

if [ ! -f "config/$config" ]
then
    echo "config/$config" not existed
    exit 1
fi

RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}source shrc${NC}"
source shrc

run=runcpu
if [ ! -d "${SPEC}/benchspec/CPU/" ]
then
    echo -e "${RED}relocate${NC}"
    relocate
    run=runspec
fi
CMD="$run -c $config -i $2 -n $3 "${@:4}" -T base"
echo -e "${RED}"$CMD"${NC}"

echo ""
echo -e "${RED}`date`${NC}"
eval $CMD
echo -e "${RED}`date`${NC}"

