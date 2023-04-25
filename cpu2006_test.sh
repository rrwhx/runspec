#!/bin/bash -x
DIR06=$(realpath .)
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib attrs.pl  1>attrs.out 2>attrs.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib gv.pl  1>gv.out 2>gv.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib makerand.pl  1>makerand.out 2>makerand.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib pack.pl  1>pack.out 2>pack.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib redef.pl  1>redef.out 2>redef.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib ref.pl  1>ref.out 2>ref.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib regmesg.pl  1>regmesg.out 2>regmesg.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_test_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I. -I./lib test.pl  1>test.out 2>test.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_test_${EXT06}.0000      &&  ./bzip2_base.${EXT06} input.program 5  1>input.program.out 2>input.program.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_test_${EXT06}.0000      &&  ./bzip2_base.${EXT06} dryer.jpg 2  1>dryer.jpg.out 2>dryer.jpg.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_test_${EXT06}.0000        &&  ./gcc_base.${EXT06} cccp.i -o cccp.s  1>cccp.out 2>cccp.err
cd ${DIR06}/benchspec/CPU2006/429.mcf/run/run_base_test_${EXT06}.0000        &&  ./mcf_base.${EXT06} inp.in  1>inp.out 2>inp.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <capture.tst 1>capture.out 2>capture.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <connect.tst 1>connect.out 2>connect.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <connect_rot.tst 1>connect_rot.out 2>connect_rot.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <connection.tst 1>connection.out 2>connection.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <connection_rot.tst 1>connection_rot.out 2>connection_rot.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <cutstone.tst 1>cutstone.out 2>cutstone.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_test_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <dniwog.tst 1>dniwog.out 2>dniwog.err
cd ${DIR06}/benchspec/CPU2006/456.hmmer/run/run_base_test_${EXT06}.0000      &&  ./hmmer_base.${EXT06} --fixed 0 --mean 325 --num 45000 --sd 200 --seed 0 bombesin.hmm  1>bombesin.out 2>bombesin.err
cd ${DIR06}/benchspec/CPU2006/458.sjeng/run/run_base_test_${EXT06}.0000      &&  ./sjeng_base.${EXT06} test.txt  1>test.out 2>test.err
cd ${DIR06}/benchspec/CPU2006/462.libquantum/run/run_base_test_${EXT06}.0000 &&  ./libquantum_base.${EXT06} 33 5  1>test.out 2>test.err
cd ${DIR06}/benchspec/CPU2006/464.h264ref/run/run_base_test_${EXT06}.0000    &&  ./h264ref_base.${EXT06} -d foreman_test_encoder_baseline.cfg  1>foreman_test_baseline_encodelog.out 2>foreman_test_baseline_encodelog.err
cd ${DIR06}/benchspec/CPU2006/471.omnetpp/run/run_base_test_${EXT06}.0000    &&  ./omnetpp_base.${EXT06} omnetpp.ini  1>omnetpp.log 2>omnetpp.err
cd ${DIR06}/benchspec/CPU2006/473.astar/run/run_base_test_${EXT06}.0000      &&  ./astar_base.${EXT06} lake.cfg  1>lake.out 2>lake.err
cd ${DIR06}/benchspec/CPU2006/483.xalancbmk/run/run_base_test_${EXT06}.0000  &&  ./Xalan_base.${EXT06} -v test.xml xalanc.xsl  1>test.out 2>test.err
cd ${DIR06}/benchspec/CPU2006/410.bwaves/run/run_base_test_${EXT06}.0000     &&  ./bwaves_base.${EXT06}   2>bwaves.err
cd ${DIR06}/benchspec/CPU2006/416.gamess/run/run_base_test_${EXT06}.0000     &&  ./gamess_base.${EXT06} <exam29.config 1>exam29.out 2>exam29.err
cd ${DIR06}/benchspec/CPU2006/433.milc/run/run_base_test_${EXT06}.0000       &&  ./milc_base.${EXT06} <su3imp.in 1>su3imp.out 2>su3imp.err
cd ${DIR06}/benchspec/CPU2006/434.zeusmp/run/run_base_test_${EXT06}.0000     &&  ./zeusmp_base.${EXT06}  1>zeusmp.stdout 2>zeusmp.err
cd ${DIR06}/benchspec/CPU2006/435.gromacs/run/run_base_test_${EXT06}.0000    &&  ./gromacs_base.${EXT06} -silent -deffnm gromacs -nice 0   2>gromacs.err
cd ${DIR06}/benchspec/CPU2006/436.cactusADM/run/run_base_test_${EXT06}.0000  &&  ./cactusADM_base.${EXT06} benchADM.par  1>benchADM.out 2>benchADM.err
cd ${DIR06}/benchspec/CPU2006/437.leslie3d/run/run_base_test_${EXT06}.0000   &&  ./leslie3d_base.${EXT06} <leslie3d.in 1>leslie3d.stdout 2>leslie3d.err
cd ${DIR06}/benchspec/CPU2006/444.namd/run/run_base_test_${EXT06}.0000       &&  ./namd_base.${EXT06} --input namd.input --iterations 1 --output namd.out   1>namd.stdout 2>namd.err
cd ${DIR06}/benchspec/CPU2006/447.dealII/run/run_base_test_${EXT06}.0000     &&  ./dealII_base.${EXT06} 8  1>log 2>dealII.err
cd ${DIR06}/benchspec/CPU2006/450.soplex/run/run_base_test_${EXT06}.0000     &&  ./soplex_base.${EXT06} -m10000 test.mps  1>test.out 2>test.stderr
cd ${DIR06}/benchspec/CPU2006/453.povray/run/run_base_test_${EXT06}.0000     &&  ./povray_base.${EXT06} SPEC-benchmark-test.ini  1>SPEC-benchmark-test.stdout 2>SPEC-benchmark-test.stderr
cd ${DIR06}/benchspec/CPU2006/454.calculix/run/run_base_test_${EXT06}.0000   &&  ./calculix_base.${EXT06} -i  beampic  1>beampic.log 2>beampic.err
cd ${DIR06}/benchspec/CPU2006/459.GemsFDTD/run/run_base_test_${EXT06}.0000   &&  ./GemsFDTD_base.${EXT06}  1>test.log 2>test.err
cd ${DIR06}/benchspec/CPU2006/465.tonto/run/run_base_test_${EXT06}.0000      &&  ./tonto_base.${EXT06}  1>tonto.out 2>tonto.err
cd ${DIR06}/benchspec/CPU2006/470.lbm/run/run_base_test_${EXT06}.0000        &&  ./lbm_base.${EXT06} 20 reference.dat 0 1 100_100_130_cf_a.of  1>lbm.out 2>lbm.err
cd ${DIR06}/benchspec/CPU2006/481.wrf/run/run_base_test_${EXT06}.0000        &&  ./wrf_base.${EXT06}  1>rsl.out.0000 2>wrf.err
cd ${DIR06}/benchspec/CPU2006/482.sphinx3/run/run_base_test_${EXT06}.0000    &&  ./sphinx_livepretend_base.${EXT06} ctlfile . args.an4  1>an4.log 2>an4.err
