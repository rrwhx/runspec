#!/bin/bash -x
DIR00=$(realpath .)
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000002    &&  ./gzip_base.${EXT00} input.combined 32  1>input.combined.out 2>input.combined.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000002     &&  ./vpr_base.${EXT00} net.in arch.in place.out dum.out -nodisp -place_only -init_t 5 -exit_t 0.005 -alpha_t 0.9412 -inner_num 2  1>place_log.out 2>place_log.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000002     &&  ./vpr_base.${EXT00} net.in arch.in place.in route.out -nodisp -route_only -route_chan_width 15 -pres_fac_mult 2 -acc_fac 1 -first_iter_pres_fac 4 -initial_pres_fac 8  1>route_log.out 2>route_log.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000002     &&  ./cc1_base.${EXT00} cp-decl.i -o cp-decl.s  1>cp-decl.out 2>cp-decl.err
cd ${DIR00}/benchspec/CINT2000/181.mcf/run/00000002     &&  ./mcf_base.${EXT00} inp.in  1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CINT2000/186.crafty/run/00000002  &&  ./crafty_base.${EXT00} <crafty.in 1>crafty.out 2>crafty.err
cd ${DIR00}/benchspec/CINT2000/197.parser/run/00000002  &&  ./parser_base.${EXT00} 2.1.dict -batch <train.in 1>train.out 2>train.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000002     &&  ./eon_base.${EXT00} chair.control.cook chair.camera chair.surfaces chair.cook.ppm ppm pixels_out.cook  1>cook_log.out 2>cook_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000002     &&  ./eon_base.${EXT00} chair.control.rushmeier chair.camera chair.surfaces chair.rushmeier.ppm ppm pixels_out.rushmeier  1>rushmeier_log.out 2>rushmeier_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000002     &&  ./eon_base.${EXT00} chair.control.kajiya chair.camera chair.surfaces chair.kajiya.ppm ppm pixels_out.kajiya  1>kajiya_log.out 2>kajiya_log.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000002 &&  ./perlbmk_base.${EXT00} -I./lib diffmail.pl 2 350 15 24 23 150  1>2.350.15.24.23.150.out 2>2.350.15.24.23.150.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000002 &&  ./perlbmk_base.${EXT00} -I./lib perfect.pl b 3  1>b.3.out 2>b.3.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000002 &&  ./perlbmk_base.${EXT00} -I. -I./lib scrabbl.pl <scrabbl.in 1>scrabbl.out 2>scrabbl.err
cd ${DIR00}/benchspec/CINT2000/254.gap/run/00000002     &&  ./gap_base.${EXT00} -l ./ -q -m 128M <train.in 1>train.out 2>train.err
cd ${DIR00}/benchspec/CINT2000/255.vortex/run/00000002  &&  ./vortex_base.${EXT00} lendian.raw  1>vortex.out2 2>vortex.err
cd ${DIR00}/benchspec/CINT2000/256.bzip2/run/00000002   &&  ./bzip2_base.${EXT00} input.compressed 8  1>input.compressed.out 2>input.compressed.err
cd ${DIR00}/benchspec/CINT2000/300.twolf/run/00000002   &&  ./twolf_base.${EXT00} train  1>train.stdout 2>train.err
cd ${DIR00}/benchspec/CFP2000/168.wupwise/run/00000002  &&  ./wupwise_base.${EXT00}  1>wupwise.out 2>wupwise.err
cd ${DIR00}/benchspec/CFP2000/171.swim/run/00000002     &&  ./swim_base.${EXT00} <swim.in 1>swim.out 2>swim.err
cd ${DIR00}/benchspec/CFP2000/172.mgrid/run/00000002    &&  ./mgrid_base.${EXT00} <mgrid.in 1>mgrid.out 2>mgrid.err
cd ${DIR00}/benchspec/CFP2000/173.applu/run/00000002    &&  ./applu_base.${EXT00} <applu.in 1>applu.out 2>applu.err
cd ${DIR00}/benchspec/CFP2000/177.mesa/run/00000002     &&  ./mesa_base.${EXT00} -frames 500 -meshfile mesa.in -ppmfile mesa.ppm   
cd ${DIR00}/benchspec/CFP2000/178.galgel/run/00000002   &&  ./galgel_base.${EXT00} <galgel.in 1>galgel.out 2>galgel.err
cd ${DIR00}/benchspec/CFP2000/179.art/run/00000002      &&  ./art_base.${EXT00} -scanfile c756hel.in -trainfile1 a10.img -stride 2 -startx 134 -starty 220 -endx 184 -endy 240 -objects 3  1>train.out 2>train.err
cd ${DIR00}/benchspec/CFP2000/183.equake/run/00000002   &&  ./equake_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/187.facerec/run/00000002  &&  ./facerec_base.${EXT00} <train.in 1>train.out 2>train.err
cd ${DIR00}/benchspec/CFP2000/188.ammp/run/00000002     &&  ./ammp_base.${EXT00} <ammp.in 1>ammp.out 2>ammp.err
cd ${DIR00}/benchspec/CFP2000/189.lucas/run/00000002    &&  ./lucas_base.${EXT00} <lucas2.in 1>lucas2.out 2>lucas2.err
cd ${DIR00}/benchspec/CFP2000/191.fma3d/run/00000002    &&  ./fma3d_base.${EXT00}  1>fma3d.out 2>fma3d.err
cd ${DIR00}/benchspec/CFP2000/200.sixtrack/run/00000002 &&  ./sixtrack_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/301.apsi/run/00000002     &&  ./apsi_base.${EXT00}  1>apsi.out 2>apsi.err
