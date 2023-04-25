#!/bin/bash -x
DIR06=$(realpath .)
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_train_${EXT06}.0000   &&  ./perlbench_base.${EXT06} -I./lib diffmail.pl 2 550 15 24 23 100  1>diffmail.2.550.15.24.23.100.out 2>diffmail.2.550.15.24.23.100.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_train_${EXT06}.0000   &&  ./perlbench_base.${EXT06} -I./lib perfect.pl b 3  1>perfect.b.3.out 2>perfect.b.3.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_train_${EXT06}.0000   &&  ./perlbench_base.${EXT06} -I. -I./lib scrabbl.pl <scrabbl.in 1>scrabbl.out 2>scrabbl.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_train_${EXT06}.0000   &&  ./perlbench_base.${EXT06} -I./lib splitmail.pl 535 13 25 24 1091  1>splitmail.535.13.25.24.1091.out 2>splitmail.535.13.25.24.1091.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_train_${EXT06}.0000   &&  ./perlbench_base.${EXT06} -I. -I./lib suns.pl  1>suns.out 2>suns.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_train_${EXT06}.0000       &&  ./bzip2_base.${EXT06} input.program 10  1>input.program.out 2>input.program.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_train_${EXT06}.0000       &&  ./bzip2_base.${EXT06} byoudoin.jpg 5  1>byoudoin.jpg.out 2>byoudoin.jpg.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_train_${EXT06}.0000       &&  ./bzip2_base.${EXT06} input.combined 80  1>input.combined.out 2>input.combined.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_train_${EXT06}.0000         &&  ./gcc_base.${EXT06} integrate.i -o integrate.s  1>integrate.out 2>integrate.err
cd ${DIR06}/benchspec/CPU2006/429.mcf/run/run_base_train_${EXT06}.0000         &&  ./mcf_base.${EXT06} inp.in  1>inp.out 2>inp.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <arb.tst 1>arb.out 2>arb.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <arend.tst 1>arend.out 2>arend.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <arion.tst 1>arion.out 2>arion.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <atari_atari.tst 1>atari_atari.out 2>atari_atari.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <blunder.tst 1>blunder.out 2>blunder.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <buzco.tst 1>buzco.out 2>buzco.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <nicklas2.tst 1>nicklas2.out 2>nicklas2.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_train_${EXT06}.0000       &&  ./gobmk_base.${EXT06} --quiet --mode gtp <nicklas4.tst 1>nicklas4.out 2>nicklas4.err
cd ${DIR06}/benchspec/CPU2006/456.hmmer/run/run_base_train_${EXT06}.0000       &&  ./hmmer_base.${EXT06} --fixed 0 --mean 425 --num 85000 --sd 300 --seed 0 leng100.hmm  1>leng100.out 2>leng100.err
cd ${DIR06}/benchspec/CPU2006/458.sjeng/run/run_base_train_${EXT06}.0000       &&  ./sjeng_base.${EXT06} train.txt  1>train.out 2>train.err
cd ${DIR06}/benchspec/CPU2006/462.libquantum/run/run_base_train_${EXT06}.0000  &&  ./libquantum_base.${EXT06} 143 25  1>train.out 2>train.err
cd ${DIR06}/benchspec/CPU2006/464.h264ref/run/run_base_train_${EXT06}.0000     &&  ./h264ref_base.${EXT06} -d foreman_train_encoder_baseline.cfg  1>foreman_train_baseline_encodelog.out 2>foreman_train_baseline_encodelog.err
cd ${DIR06}/benchspec/CPU2006/471.omnetpp/run/run_base_train_${EXT06}.0000     &&  ./omnetpp_base.${EXT06} omnetpp.ini  1>omnetpp.log 2>omnetpp.err
cd ${DIR06}/benchspec/CPU2006/473.astar/run/run_base_train_${EXT06}.0000       &&  ./astar_base.${EXT06} BigLakes1024.cfg  1>BigLakes1024.out 2>BigLakes1024.err
cd ${DIR06}/benchspec/CPU2006/473.astar/run/run_base_train_${EXT06}.0000       &&  ./astar_base.${EXT06} rivers1.cfg  1>rivers1.out 2>rivers1.err
cd ${DIR06}/benchspec/CPU2006/483.xalancbmk/run/run_base_train_${EXT06}.0000   &&  ./Xalan_base.${EXT06} -v allbooks.xml xalanc.xsl  1>train.out 2>train.err
cd ${DIR06}/benchspec/CPU2006/410.bwaves/run/run_base_train_${EXT06}.0000      &&  ./bwaves_base.${EXT06}   2>bwaves.err
cd ${DIR06}/benchspec/CPU2006/416.gamess/run/run_base_train_${EXT06}.0000      &&  ./gamess_base.${EXT06} <h2ocu2+.energy.config 1>h2ocu2+.energy.out 2>h2ocu2+.energy.err
cd ${DIR06}/benchspec/CPU2006/433.milc/run/run_base_train_${EXT06}.0000        &&  ./milc_base.${EXT06} <su3imp.in 1>su3imp.out 2>su3imp.err
cd ${DIR06}/benchspec/CPU2006/434.zeusmp/run/run_base_train_${EXT06}.0000      &&  ./zeusmp_base.${EXT06}  1>zeusmp.stdout 2>zeusmp.err
cd ${DIR06}/benchspec/CPU2006/435.gromacs/run/run_base_train_${EXT06}.0000     &&  ./gromacs_base.${EXT06} -silent -deffnm gromacs -nice 0   2>gromacs.err
cd ${DIR06}/benchspec/CPU2006/436.cactusADM/run/run_base_train_${EXT06}.0000   &&  ./cactusADM_base.${EXT06} benchADM.par  1>benchADM.out 2>benchADM.err
cd ${DIR06}/benchspec/CPU2006/437.leslie3d/run/run_base_train_${EXT06}.0000    &&  ./leslie3d_base.${EXT06} <leslie3d.in 1>leslie3d.stdout 2>leslie3d.err
cd ${DIR06}/benchspec/CPU2006/444.namd/run/run_base_train_${EXT06}.0000        &&  ./namd_base.${EXT06} --input namd.input --iterations 1 --output namd.out   1>namd.stdout 2>namd.err
cd ${DIR06}/benchspec/CPU2006/447.dealII/run/run_base_train_${EXT06}.0000      &&  ./dealII_base.${EXT06} 10  1>log 2>dealII.err
cd ${DIR06}/benchspec/CPU2006/450.soplex/run/run_base_train_${EXT06}.0000      &&  ./soplex_base.${EXT06} -s1 -e -m5000 pds-20.mps  1>pds-20.mps.out 2>pds-20.mps.stderr
cd ${DIR06}/benchspec/CPU2006/450.soplex/run/run_base_train_${EXT06}.0000      &&  ./soplex_base.${EXT06} -m1200 train.mps  1>train.out 2>train.stderr
cd ${DIR06}/benchspec/CPU2006/453.povray/run/run_base_train_${EXT06}.0000      &&  ./povray_base.${EXT06} SPEC-benchmark-train.ini  1>SPEC-benchmark-train.stdout 2>SPEC-benchmark-train.stderr
cd ${DIR06}/benchspec/CPU2006/454.calculix/run/run_base_train_${EXT06}.0000    &&  ./calculix_base.${EXT06} -i  stairs  1>stairs.log 2>stairs.err
cd ${DIR06}/benchspec/CPU2006/459.GemsFDTD/run/run_base_train_${EXT06}.0000    &&  ./GemsFDTD_base.${EXT06}  1>train.log 2>train.err
cd ${DIR06}/benchspec/CPU2006/465.tonto/run/run_base_train_${EXT06}.0000       &&  ./tonto_base.${EXT06}  1>tonto.out 2>tonto.err
cd ${DIR06}/benchspec/CPU2006/470.lbm/run/run_base_train_${EXT06}.0000         &&  ./lbm_base.${EXT06} 300 reference.dat 0 1 100_100_130_cf_b.of  1>lbm.out 2>lbm.err
cd ${DIR06}/benchspec/CPU2006/481.wrf/run/run_base_train_${EXT06}.0000         &&  ./wrf_base.${EXT06}  1>rsl.out.0000 2>wrf.err
cd ${DIR06}/benchspec/CPU2006/482.sphinx3/run/run_base_train_${EXT06}.0000     &&  ./sphinx_livepretend_base.${EXT06} ctlfile . args.an4  1>an4.log 2>an4.err
