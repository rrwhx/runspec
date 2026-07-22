#!/bin/bash
# Source: https://github.com/rrwhx/runspec

# 检查是否提供了参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <目录或文件> [目录或文件...]"
    exit 1
fi

# 定义关键字数组
int_keywords=("164.gzip" "175.vpr" "176.gcc" "181.mcf" "186.crafty" "197.parser" "252.eon" "253.perlbmk" "254.gap" "255.vortex" "256.bzip2" "300.twolf" "400.perlbench" "401.bzip2" "403.gcc" "429.mcf" "445.gobmk" "456.hmmer" "458.sjeng" "462.libquantum" "464.h264ref" "471.omnetpp" "473.astar" "483.xalancbmk" "500.perlbench_r" "502.gcc_r" "505.mcf_r" "520.omnetpp_r" "523.xalancbmk_r" "525.x264_r" "531.deepsjeng_r" "541.leela_r" "548.exchange2_r" "557.xz_r" "706.stockfish_r" "707.ntest_r" "708.sqlite_r" "710.omnetpp_r" "714.cpython_r" "721.gcc_r" "723.llvm_r" "727.cppcheck_r" "729.abc_r" "734.vpr_r" "735.gem5_r" "750.sealcrypto_r" "753.ns3_r" "777.zstd_r" )
fp_keywords=("168.wupwise" "171.swim" "172.mgrid" "173.applu" "177.mesa" "178.galgel" "179.art" "183.equake" "187.facerec" "188.ammp" "189.lucas" "191.fma3d" "200.sixtrack" "301.apsi" "410.bwaves" "416.gamess" "433.milc" "434.zeusmp" "435.gromacs" "436.cactusADM" "437.leslie3d" "444.namd" "447.dealII" "450.soplex" "453.povray" "454.calculix" "459.GemsFDTD" "465.tonto" "470.lbm" "481.wrf" "482.sphinx3" "503.bwaves_r" "507.cactuBSSN_r" "508.namd_r" "510.parest_r" "511.povray_r" "519.lbm_r" "521.wrf_r" "526.blender_r" "527.cam4_r" "538.imagick_r" "544.nab_r" "549.fotonik3d_r" "554.roms_r" "709.cactus_r" "722.palm_r" "731.astcenc_r" "736.ocio_r" "737.gmsh_r" "748.flightdm_r" "749.fotonik3d_r" "765.roms_r" "766.femflow_r" "767.nest_r" "772.marian_r" "782.lbm_r")


# 对单个文件进行重命名处理
process_file() {
    local file="$1"
    local filename dirpath keyword new_filename
    filename=$(basename "$file")
    dirpath=$(dirname "$file")

    # 检查文件名是否包含int关键字
    for keyword in "${int_keywords[@]}"; do
        if [[ "$filename" == *"$keyword"* ]]; then
            # 避免重复添加前缀
            if [[ "$filename" != int_* ]]; then
                new_filename="int_$filename"
                mv -- "$file" "$dirpath/$new_filename"
                echo "重命名: $file -> $dirpath/$new_filename"
            fi
            return
        fi
    done

    # 检查文件名是否包含fp关键字
    for keyword in "${fp_keywords[@]}"; do
        if [[ "$filename" == *"$keyword"* ]]; then
            if [[ "$filename" != xfp_* ]]; then
                new_filename="xfp_$filename"
                mv -- "$file" "$dirpath/$new_filename"
                echo "重命名: $file -> $dirpath/$new_filename"
            fi
            return
        fi
    done
}

# 遍历所有参数：目录则处理其下的文件，文件则直接处理
for target in "$@"; do
    if [ -d "$target" ]; then
        while IFS= read -r -d '' file; do
            process_file "$file"
        done < <(find "$target" -maxdepth 1 -type f -print0)
    elif [ -f "$target" ]; then
        process_file "$target"
    else
        echo "警告: '$target' 不是目录或文件，跳过" >&2
    fi
done
