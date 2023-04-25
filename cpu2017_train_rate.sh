#!/bin/bash -x
DIR17=$(realpath .)
cd ${DIR17}/benchspec/CPU/500.perlbench_r/run/run_base_train_${EXT17}.0000 &&  ./perlbench_r_base.${EXT17} -I./lib diffmail.pl 2 550 15 24 23 100   1>diffmail.2.550.15.24.23.100.out 2>diffmail.2.550.15.24.23.100.err
cd ${DIR17}/benchspec/CPU/500.perlbench_r/run/run_base_train_${EXT17}.0000 &&  ./perlbench_r_base.${EXT17} -I./lib perfect.pl b 3   1>perfect.b.3.out 2>perfect.b.3.err
cd ${DIR17}/benchspec/CPU/500.perlbench_r/run/run_base_train_${EXT17}.0000 &&  ./perlbench_r_base.${EXT17} -I. -I./lib scrabbl.pl  <scrabbl.in 1>scrabbl.out 2>scrabbl.err
cd ${DIR17}/benchspec/CPU/500.perlbench_r/run/run_base_train_${EXT17}.0000 &&  ./perlbench_r_base.${EXT17} -I./lib splitmail.pl 535 13 25 24 1091 1   1>splitmail.535.13.25.24.1091.1.out 2>splitmail.535.13.25.24.1091.1.err
cd ${DIR17}/benchspec/CPU/500.perlbench_r/run/run_base_train_${EXT17}.0000 &&  ./perlbench_r_base.${EXT17} -I. -I./lib suns.pl   1>suns.out 2>suns.err
cd ${DIR17}/benchspec/CPU/502.gcc_r/run/run_base_train_${EXT17}.0000       &&  ./cpugcc_r_base.${EXT17} 200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s   1>200.opts-O3_-finline-limit_50000.out 2>200.opts-O3_-finline-limit_50000.err
cd ${DIR17}/benchspec/CPU/502.gcc_r/run/run_base_train_${EXT17}.0000       &&  ./cpugcc_r_base.${EXT17} scilab.c -O3 -finline-limit=50000 -o scilab.opts-O3_-finline-limit_50000.s   1>scilab.opts-O3_-finline-limit_50000.out 2>scilab.opts-O3_-finline-limit_50000.err
cd ${DIR17}/benchspec/CPU/502.gcc_r/run/run_base_train_${EXT17}.0000       &&  ./cpugcc_r_base.${EXT17} train01.c -O3 -finline-limit=50000 -o train01.opts-O3_-finline-limit_50000.s   1>train01.opts-O3_-finline-limit_50000.out 2>train01.opts-O3_-finline-limit_50000.err
cd ${DIR17}/benchspec/CPU/505.mcf_r/run/run_base_train_${EXT17}.0000       &&  ./mcf_r_base.${EXT17} inp.in    1>inp.out 2>inp.err
cd ${DIR17}/benchspec/CPU/520.omnetpp_r/run/run_base_train_${EXT17}.0000   &&  ./omnetpp_r_base.${EXT17} -c General -r 0   1>omnetpp.General-0.out 2>omnetpp.General-0.err
cd ${DIR17}/benchspec/CPU/523.xalancbmk_r/run/run_base_train_${EXT17}.0000 &&  ./cpuxalan_r_base.${EXT17} -v allbooks.xml xalanc.xsl   1>train-allbooks.out 2>train-allbooks.err
cd ${DIR17}/benchspec/CPU/525.x264_r/run/run_base_train_${EXT17}.0000      &&  ./x264_r_base.${EXT17} --dumpyuv 50 --frames 142 -o BuckBunny_New.264 BuckBunny.yuv 1280x720   1>run_000-142_x264_r_base.mytest-m64_x264.out 2>run_000-142_x264_r_base.mytest-m64_x264.err
cd ${DIR17}/benchspec/CPU/531.deepsjeng_r/run/run_base_train_${EXT17}.0000 &&  ./deepsjeng_r_base.${EXT17} train.txt   1>train.out 2>train.err
cd ${DIR17}/benchspec/CPU/541.leela_r/run/run_base_train_${EXT17}.0000     &&  ./leela_r_base.${EXT17} train.sgf   1>train.out 2>train.err
cd ${DIR17}/benchspec/CPU/548.exchange2_r/run/run_base_train_${EXT17}.0000 &&  ./exchange2_r_base.${EXT17} 1   1>exchange2.txt 2>exchange2.err
cd ${DIR17}/benchspec/CPU/557.xz_r/run/run_base_train_${EXT17}.0000        &&  ./xz_r_base.${EXT17} input.combined.xz 40 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 6356684 -1 8   1>input.combined-40-8.out 2>input.combined-40-8.err
cd ${DIR17}/benchspec/CPU/557.xz_r/run/run_base_train_${EXT17}.0000        &&  ./xz_r_base.${EXT17} IMG_2560.cr2.xz 40 ec03e53b02deae89b6650f1de4bed76a012366fb3d4bdc791e8633d1a5964e03004523752ab008eff0d9e693689c53056533a05fc4b277f0086544c6c3cbbbf6 40822692 40824404 4   1>IMG_2560.cr2-40-4.out 2>IMG_2560.cr2-40-4.err
cd ${DIR17}/benchspec/CPU/503.bwaves_r/run/run_base_train_${EXT17}.0000    &&  ./bwaves_r_base.${EXT17} bwaves_1  <bwaves_1.in 1>bwaves_1.out 2>bwaves_1.err
cd ${DIR17}/benchspec/CPU/503.bwaves_r/run/run_base_train_${EXT17}.0000    &&  ./bwaves_r_base.${EXT17} bwaves_2  <bwaves_2.in 1>bwaves_2.out 2>bwaves_2.err
cd ${DIR17}/benchspec/CPU/507.cactuBSSN_r/run/run_base_train_${EXT17}.0000 &&  ./cactusBSSN_r_base.${EXT17} spec_train.par     1>spec_train.out 2>spec_train.err
cd ${DIR17}/benchspec/CPU/508.namd_r/run/run_base_train_${EXT17}.0000      &&  ./namd_r_base.${EXT17} --input apoa1.input --iterations 7 --output apoa1.train.output   1>namd.out 2>namd.err
cd ${DIR17}/benchspec/CPU/510.parest_r/run/run_base_train_${EXT17}.0000    &&  ./parest_r_base.${EXT17} train.prm   1>train.out 2>train.err
cd ${DIR17}/benchspec/CPU/511.povray_r/run/run_base_train_${EXT17}.0000    &&  ./povray_r_base.${EXT17} SPEC-benchmark-train.ini   1>SPEC-benchmark-train.stdout 2>SPEC-benchmark-train.stderr
cd ${DIR17}/benchspec/CPU/519.lbm_r/run/run_base_train_${EXT17}.0000       &&  ./lbm_r_base.${EXT17} 300 reference.dat 0 1 100_100_130_cf_b.of   1>lbm.out 2>lbm.err
cd ${DIR17}/benchspec/CPU/521.wrf_r/run/run_base_train_${EXT17}.0000       &&  ./wrf_r_base.${EXT17}   1>rsl.out.0000 2>wrf.err
cd ${DIR17}/benchspec/CPU/526.blender_r/run/run_base_train_${EXT17}.0000   &&  ./blender_r_base.${EXT17} sh5_reduced.blend --render-output sh5_reduced_ --threads 1 -b -F RAWTGA -s 234 -e 234 -a   1>sh5_reduced.234.spec.out 2>sh5_reduced.234.spec.err
cd ${DIR17}/benchspec/CPU/527.cam4_r/run/run_base_train_${EXT17}.0000      &&  ./cam4_r_base.${EXT17}   1>cam4_r_base.mytest-m64.txt 2>cam4_r_base.mytest-m64.err
cd ${DIR17}/benchspec/CPU/538.imagick_r/run/run_base_train_${EXT17}.0000   &&  ./imagick_r_base.${EXT17} -limit disk 0 train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga   1>train_convert.out 2>train_convert.err
cd ${DIR17}/benchspec/CPU/544.nab_r/run/run_base_train_${EXT17}.0000       &&  ./nab_r_base.${EXT17} aminos 391519156 1000   1>aminos.out 2>aminos.err
cd ${DIR17}/benchspec/CPU/544.nab_r/run/run_base_train_${EXT17}.0000       &&  ./nab_r_base.${EXT17} gcn4dna 1850041461 300   1>gcn4dna.out 2>gcn4dna.err
cd ${DIR17}/benchspec/CPU/549.fotonik3d_r/run/run_base_train_${EXT17}.0000 &&  ./fotonik3d_r_base.${EXT17}   1>fotonik3d_r.log 2>fotonik3d_r.err
cd ${DIR17}/benchspec/CPU/554.roms_r/run/run_base_train_${EXT17}.0000      &&  ./roms_r_base.${EXT17}  <ocean_benchmark1.in.x 1>ocean_benchmark1.log 2>ocean_benchmark1.err