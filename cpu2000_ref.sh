#!/bin/bash -x
DIR00=$(realpath .)
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000003    &&  ./gzip_base.${EXT00} input.source 60  1>input.source.out 2>input.source.err
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000003    &&  ./gzip_base.${EXT00} input.log 60  1>input.log.out 2>input.log.err
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000003    &&  ./gzip_base.${EXT00} input.graphic 60  1>input.graphic.out 2>input.graphic.err
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000003    &&  ./gzip_base.${EXT00} input.random 60  1>input.random.out 2>input.random.err
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000003    &&  ./gzip_base.${EXT00} input.program 60  1>input.program.out 2>input.program.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000003     &&  ./vpr_base.${EXT00} net.in arch.in place.out dum.out -nodisp -place_only -init_t 5 -exit_t 0.005 -alpha_t 0.9412 -inner_num 2  1>place_log.out 2>place_log.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000003     &&  ./vpr_base.${EXT00} net.in arch.in place.in route.out -nodisp -route_only -route_chan_width 15 -pres_fac_mult 2 -acc_fac 1 -first_iter_pres_fac 4 -initial_pres_fac 8  1>route_log.out 2>route_log.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000003     &&  ./cc1_base.${EXT00} 166.i -o 166.s  1>166.out 2>166.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000003     &&  ./cc1_base.${EXT00} 200.i -o 200.s  1>200.out 2>200.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000003     &&  ./cc1_base.${EXT00} expr.i -o expr.s  1>expr.out 2>expr.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000003     &&  ./cc1_base.${EXT00} integrate.i -o integrate.s  1>integrate.out 2>integrate.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000003     &&  ./cc1_base.${EXT00} scilab.i -o scilab.s  1>scilab.out 2>scilab.err
cd ${DIR00}/benchspec/CINT2000/181.mcf/run/00000003     &&  ./mcf_base.${EXT00} inp.in  1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CINT2000/186.crafty/run/00000003  &&  ./crafty_base.${EXT00} <crafty.in 1>crafty.out 2>crafty.err
cd ${DIR00}/benchspec/CINT2000/197.parser/run/00000003  &&  ./parser_base.${EXT00} 2.1.dict -batch <ref.in 1>ref.out 2>ref.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000003     &&  ./eon_base.${EXT00} chair.control.cook chair.camera chair.surfaces chair.cook.ppm ppm pixels_out.cook  1>cook_log.out 2>cook_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000003     &&  ./eon_base.${EXT00} chair.control.rushmeier chair.camera chair.surfaces chair.rushmeier.ppm ppm pixels_out.rushmeier  1>rushmeier_log.out 2>rushmeier_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000003     &&  ./eon_base.${EXT00} chair.control.kajiya chair.camera chair.surfaces chair.kajiya.ppm ppm pixels_out.kajiya  1>kajiya_log.out 2>kajiya_log.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib diffmail.pl 2 550 15 24 23 100  1>2.550.15.24.23.100.out 2>2.550.15.24.23.100.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I. -I./lib makerand.pl  1>makerand.out 2>makerand.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib perfect.pl b 3 m 4  1>b.3.m.4.out 2>b.3.m.4.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib splitmail.pl 850 5 19 18 1500  1>850.5.19.18.1500.out 2>850.5.19.18.1500.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib splitmail.pl 704 12 26 16 836  1>704.12.26.16.836.out 2>704.12.26.16.836.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib splitmail.pl 535 13 25 24 1091  1>535.13.25.24.1091.out 2>535.13.25.24.1091.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000003 &&  ./perlbmk_base.${EXT00} -I./lib splitmail.pl 957 12 23 26 1014  1>957.12.23.26.1014.out 2>957.12.23.26.1014.err
cd ${DIR00}/benchspec/CINT2000/254.gap/run/00000003     &&  ./gap_base.${EXT00} -l ./ -q -m 192M <ref.in 1>ref.out 2>ref.err
cd ${DIR00}/benchspec/CINT2000/255.vortex/run/00000003  &&  ./vortex_base.${EXT00} lendian1.raw  1>vortex1.out2 2>vortex1.err
cd ${DIR00}/benchspec/CINT2000/255.vortex/run/00000003  &&  ./vortex_base.${EXT00} lendian2.raw  1>vortex2.out2 2>vortex2.err
cd ${DIR00}/benchspec/CINT2000/255.vortex/run/00000003  &&  ./vortex_base.${EXT00} lendian3.raw  1>vortex3.out2 2>vortex3.err
cd ${DIR00}/benchspec/CINT2000/256.bzip2/run/00000003   &&  ./bzip2_base.${EXT00} input.source 58  1>input.source.out 2>input.source.err
cd ${DIR00}/benchspec/CINT2000/256.bzip2/run/00000003   &&  ./bzip2_base.${EXT00} input.graphic 58  1>input.graphic.out 2>input.graphic.err
cd ${DIR00}/benchspec/CINT2000/256.bzip2/run/00000003   &&  ./bzip2_base.${EXT00} input.program 58  1>input.program.out 2>input.program.err
cd ${DIR00}/benchspec/CINT2000/300.twolf/run/00000003   &&  ./twolf_base.${EXT00} ref  1>ref.stdout 2>ref.err
cd ${DIR00}/benchspec/CFP2000/168.wupwise/run/00000003  &&  ./wupwise_base.${EXT00}  1>wupwise.out 2>wupwise.err
cd ${DIR00}/benchspec/CFP2000/171.swim/run/00000003     &&  ./swim_base.${EXT00} <swim.in 1>swim.out 2>swim.err
cd ${DIR00}/benchspec/CFP2000/172.mgrid/run/00000003    &&  ./mgrid_base.${EXT00} <mgrid.in 1>mgrid.out 2>mgrid.err
cd ${DIR00}/benchspec/CFP2000/173.applu/run/00000003    &&  ./applu_base.${EXT00} <applu.in 1>applu.out 2>applu.err
cd ${DIR00}/benchspec/CFP2000/177.mesa/run/00000003     &&  ./mesa_base.${EXT00} -frames 1000 -meshfile mesa.in -ppmfile mesa.ppm   
cd ${DIR00}/benchspec/CFP2000/178.galgel/run/00000003   &&  ./galgel_base.${EXT00} <galgel.in 1>galgel.out 2>galgel.err
cd ${DIR00}/benchspec/CFP2000/179.art/run/00000003      &&  ./art_base.${EXT00} -scanfile c756hel.in -trainfile1 a10.img -trainfile2 hc.img -stride 2 -startx 110 -starty 200 -endx 160 -endy 240 -objects 10  1>ref.1.out 2>ref.1.err
cd ${DIR00}/benchspec/CFP2000/179.art/run/00000003      &&  ./art_base.${EXT00} -scanfile c756hel.in -trainfile1 a10.img -trainfile2 hc.img -stride 2 -startx 470 -starty 140 -endx 520 -endy 180 -objects 10  1>ref.2.out 2>ref.2.err
cd ${DIR00}/benchspec/CFP2000/183.equake/run/00000003   &&  ./equake_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/187.facerec/run/00000003  &&  ./facerec_base.${EXT00} <ref.in 1>ref.out 2>ref.err
cd ${DIR00}/benchspec/CFP2000/188.ammp/run/00000003     &&  ./ammp_base.${EXT00} <ammp.in 1>ammp.out 2>ammp.err
cd ${DIR00}/benchspec/CFP2000/189.lucas/run/00000003    &&  ./lucas_base.${EXT00} <lucas2.in 1>lucas2.out 2>lucas2.err
cd ${DIR00}/benchspec/CFP2000/191.fma3d/run/00000003    &&  ./fma3d_base.${EXT00}  1>fma3d.out 2>fma3d.err
cd ${DIR00}/benchspec/CFP2000/200.sixtrack/run/00000003 &&  ./sixtrack_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/301.apsi/run/00000003     &&  ./apsi_base.${EXT00}  1>apsi.out 2>apsi.err
