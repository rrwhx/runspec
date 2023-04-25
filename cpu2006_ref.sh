#!/bin/bash -x
DIR06=$(realpath .)
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_ref_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1  1>checkspam.2500.5.25.11.150.1.1.1.1.out 2>checkspam.2500.5.25.11.150.1.1.1.1.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_ref_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I./lib diffmail.pl 4 800 10 17 19 300  1>diffmail.4.800.10.17.19.300.out 2>diffmail.4.800.10.17.19.300.err
cd ${DIR06}/benchspec/CPU2006/400.perlbench/run/run_base_ref_${EXT06}.0000  &&  ./perlbench_base.${EXT06} -I./lib splitmail.pl 1600 12 26 16 4500  1>splitmail.1600.12.26.16.4500.out 2>splitmail.1600.12.26.16.4500.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} input.source 280  1>input.source.out 2>input.source.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} chicken.jpg 30  1>chicken.jpg.out 2>chicken.jpg.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} liberty.jpg 30  1>liberty.jpg.out 2>liberty.jpg.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} input.program 280  1>input.program.out 2>input.program.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} text.html 280  1>text.html.out 2>text.html.err
cd ${DIR06}/benchspec/CPU2006/401.bzip2/run/run_base_ref_${EXT06}.0000      &&  ./bzip2_base.${EXT06} input.combined 200  1>input.combined.out 2>input.combined.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} 166.i -o 166.s  1>166.out 2>166.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} 200.i -o 200.s  1>200.out 2>200.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} c-typeck.i -o c-typeck.s  1>c-typeck.out 2>c-typeck.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} cp-decl.i -o cp-decl.s  1>cp-decl.out 2>cp-decl.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} expr.i -o expr.s  1>expr.out 2>expr.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} expr2.i -o expr2.s  1>expr2.out 2>expr2.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} g23.i -o g23.s  1>g23.out 2>g23.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} s04.i -o s04.s  1>s04.out 2>s04.err
cd ${DIR06}/benchspec/CPU2006/403.gcc/run/run_base_ref_${EXT06}.0000        &&  ./gcc_base.${EXT06} scilab.i -o scilab.s  1>scilab.out 2>scilab.err
cd ${DIR06}/benchspec/CPU2006/429.mcf/run/run_base_ref_${EXT06}.0000        &&  ./mcf_base.${EXT06} inp.in  1>inp.out 2>inp.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_ref_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <13x13.tst 1>13x13.out 2>13x13.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_ref_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <nngs.tst 1>nngs.out 2>nngs.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_ref_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <score2.tst 1>score2.out 2>score2.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_ref_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <trevorc.tst 1>trevorc.out 2>trevorc.err
cd ${DIR06}/benchspec/CPU2006/445.gobmk/run/run_base_ref_${EXT06}.0000      &&  ./gobmk_base.${EXT06} --quiet --mode gtp <trevord.tst 1>trevord.out 2>trevord.err
cd ${DIR06}/benchspec/CPU2006/456.hmmer/run/run_base_ref_${EXT06}.0000      &&  ./hmmer_base.${EXT06} nph3.hmm swiss41  1>nph3.out 2>nph3.err
cd ${DIR06}/benchspec/CPU2006/456.hmmer/run/run_base_ref_${EXT06}.0000      &&  ./hmmer_base.${EXT06} --fixed 0 --mean 500 --num 500000 --sd 350 --seed 0 retro.hmm  1>retro.out 2>retro.err
cd ${DIR06}/benchspec/CPU2006/458.sjeng/run/run_base_ref_${EXT06}.0000      &&  ./sjeng_base.${EXT06} ref.txt  1>ref.out 2>ref.err
cd ${DIR06}/benchspec/CPU2006/462.libquantum/run/run_base_ref_${EXT06}.0000 &&  ./libquantum_base.${EXT06} 1397 8  1>ref.out 2>ref.err
cd ${DIR06}/benchspec/CPU2006/464.h264ref/run/run_base_ref_${EXT06}.0000    &&  ./h264ref_base.${EXT06} -d foreman_ref_encoder_baseline.cfg  1>foreman_ref_baseline_encodelog.out 2>foreman_ref_baseline_encodelog.err
cd ${DIR06}/benchspec/CPU2006/464.h264ref/run/run_base_ref_${EXT06}.0000    &&  ./h264ref_base.${EXT06} -d foreman_ref_encoder_main.cfg  1>foreman_ref_main_encodelog.out 2>foreman_ref_main_encodelog.err
cd ${DIR06}/benchspec/CPU2006/464.h264ref/run/run_base_ref_${EXT06}.0000    &&  ./h264ref_base.${EXT06} -d sss_encoder_main.cfg  1>sss_main_encodelog.out 2>sss_main_encodelog.err
cd ${DIR06}/benchspec/CPU2006/471.omnetpp/run/run_base_ref_${EXT06}.0000    &&  ./omnetpp_base.${EXT06} omnetpp.ini  1>omnetpp.log 2>omnetpp.err
cd ${DIR06}/benchspec/CPU2006/473.astar/run/run_base_ref_${EXT06}.0000      &&  ./astar_base.${EXT06} BigLakes2048.cfg  1>BigLakes2048.out 2>BigLakes2048.err
cd ${DIR06}/benchspec/CPU2006/473.astar/run/run_base_ref_${EXT06}.0000      &&  ./astar_base.${EXT06} rivers.cfg  1>rivers.out 2>rivers.err
cd ${DIR06}/benchspec/CPU2006/483.xalancbmk/run/run_base_ref_${EXT06}.0000  &&  ./Xalan_base.${EXT06} -v t5.xml xalanc.xsl  1>ref.out 2>ref.err
cd ${DIR06}/benchspec/CPU2006/410.bwaves/run/run_base_ref_${EXT06}.0000     &&  ./bwaves_base.${EXT06}   2>bwaves.err
cd ${DIR06}/benchspec/CPU2006/416.gamess/run/run_base_ref_${EXT06}.0000     &&  ./gamess_base.${EXT06} <cytosine.2.config 1>cytosine.2.out 2>cytosine.2.err
cd ${DIR06}/benchspec/CPU2006/416.gamess/run/run_base_ref_${EXT06}.0000     &&  ./gamess_base.${EXT06} <h2ocu2+.gradient.config 1>h2ocu2+.gradient.out 2>h2ocu2+.gradient.err
cd ${DIR06}/benchspec/CPU2006/416.gamess/run/run_base_ref_${EXT06}.0000     &&  ./gamess_base.${EXT06} <triazolium.config 1>triazolium.out 2>triazolium.err
cd ${DIR06}/benchspec/CPU2006/433.milc/run/run_base_ref_${EXT06}.0000       &&  ./milc_base.${EXT06} <su3imp.in 1>su3imp.out 2>su3imp.err
cd ${DIR06}/benchspec/CPU2006/434.zeusmp/run/run_base_ref_${EXT06}.0000     &&  ./zeusmp_base.${EXT06}  1>zeusmp.stdout 2>zeusmp.err
cd ${DIR06}/benchspec/CPU2006/435.gromacs/run/run_base_ref_${EXT06}.0000    &&  ./gromacs_base.${EXT06} -silent -deffnm gromacs -nice 0   2>gromacs.err
cd ${DIR06}/benchspec/CPU2006/436.cactusADM/run/run_base_ref_${EXT06}.0000  &&  ./cactusADM_base.${EXT06} benchADM.par  1>benchADM.out 2>benchADM.err
cd ${DIR06}/benchspec/CPU2006/437.leslie3d/run/run_base_ref_${EXT06}.0000   &&  ./leslie3d_base.${EXT06} <leslie3d.in 1>leslie3d.stdout 2>leslie3d.err
cd ${DIR06}/benchspec/CPU2006/444.namd/run/run_base_ref_${EXT06}.0000       &&  ./namd_base.${EXT06} --input namd.input --iterations 38 --output namd.out   1>namd.stdout 2>namd.err
cd ${DIR06}/benchspec/CPU2006/447.dealII/run/run_base_ref_${EXT06}.0000     &&  ./dealII_base.${EXT06} 23  1>log 2>dealII.err
cd ${DIR06}/benchspec/CPU2006/450.soplex/run/run_base_ref_${EXT06}.0000     &&  ./soplex_base.${EXT06} -s1 -e -m45000 pds-50.mps  1>pds-50.mps.out 2>pds-50.mps.stderr
cd ${DIR06}/benchspec/CPU2006/450.soplex/run/run_base_ref_${EXT06}.0000     &&  ./soplex_base.${EXT06} -m3500 ref.mps  1>ref.out 2>ref.stderr
cd ${DIR06}/benchspec/CPU2006/453.povray/run/run_base_ref_${EXT06}.0000     &&  ./povray_base.${EXT06} SPEC-benchmark-ref.ini  1>SPEC-benchmark-ref.stdout 2>SPEC-benchmark-ref.stderr
cd ${DIR06}/benchspec/CPU2006/454.calculix/run/run_base_ref_${EXT06}.0000   &&  ./calculix_base.${EXT06} -i  hyperviscoplastic  1>hyperviscoplastic.log 2>hyperviscoplastic.err
cd ${DIR06}/benchspec/CPU2006/459.GemsFDTD/run/run_base_ref_${EXT06}.0000   &&  ./GemsFDTD_base.${EXT06}  1>ref.log 2>ref.err
cd ${DIR06}/benchspec/CPU2006/465.tonto/run/run_base_ref_${EXT06}.0000      &&  ./tonto_base.${EXT06}  1>tonto.out 2>tonto.err
cd ${DIR06}/benchspec/CPU2006/470.lbm/run/run_base_ref_${EXT06}.0000        &&  ./lbm_base.${EXT06} 3000 reference.dat 0 0 100_100_130_ldc.of  1>lbm.out 2>lbm.err
cd ${DIR06}/benchspec/CPU2006/481.wrf/run/run_base_ref_${EXT06}.0000        &&  ./wrf_base.${EXT06}  1>rsl.out.0000 2>wrf.err
cd ${DIR06}/benchspec/CPU2006/482.sphinx3/run/run_base_ref_${EXT06}.0000    &&  ./sphinx_livepretend_base.${EXT06} ctlfile . args.an4  1>an4.log 2>an4.err
