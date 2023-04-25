#!/bin/bash -x
DIR00=$(realpath .)
cd ${DIR00}/benchspec/CINT2000/164.gzip/run/00000001    && ./gzip_base.${EXT00} input.compressed 2  1>input.compressed.out 2>input.compressed.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000001     && ./vpr_base.${EXT00} net.in arch.in place.out dum.out -nodisp -place_only -init_t 5 -exit_t 0.005 -alpha_t 0.9412 -inner_num 2  1>place_log.out 2>place_log.err
cd ${DIR00}/benchspec/CINT2000/175.vpr/run/00000001     && ./vpr_base.${EXT00} net.in arch.in place.in route.out -nodisp -route_only -route_chan_width 15 -pres_fac_mult 2 -acc_fac 1 -first_iter_pres_fac 4 -initial_pres_fac 8  1>route_log.out 2>route_log.err
cd ${DIR00}/benchspec/CINT2000/176.gcc/run/00000001     && ./cc1_base.${EXT00} cccp.i -o cccp.s  1>cccp.out 2>cccp.err
cd ${DIR00}/benchspec/CINT2000/181.mcf/run/00000001     && ./mcf_base.${EXT00} inp.in  1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CINT2000/186.crafty/run/00000001  && ./crafty_base.${EXT00} <crafty.in 1>crafty.out 2>crafty.err
cd ${DIR00}/benchspec/CINT2000/197.parser/run/00000001  && ./parser_base.${EXT00} 2.1.dict -batch <test.in 1>test.out 2>test.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000001     && ./eon_base.${EXT00} chair.control.cook chair.camera chair.surfaces chair.cook.ppm ppm pixels_out.cook  1>cook_log.out 2>cook_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000001     && ./eon_base.${EXT00} chair.control.rushmeier chair.camera chair.surfaces chair.rushmeier.ppm ppm pixels_out.rushmeier  1>rushmeier_log.out 2>rushmeier_log.err
cd ${DIR00}/benchspec/CINT2000/252.eon/run/00000001     && ./eon_base.${EXT00} chair.control.kajiya chair.camera chair.surfaces chair.kajiya.ppm ppm pixels_out.kajiya  1>kajiya_log.out 2>kajiya_log.err
cd ${DIR00}/benchspec/CINT2000/253.perlbmk/run/00000001 && ./perlbmk_base.${EXT00} -I. -I./lib test.pl <test.in 1>test.out 2>test.err
cd ${DIR00}/benchspec/CINT2000/254.gap/run/00000001     && ./gap_base.${EXT00} -l ./ -q -m 64M <test.in 1>test.out 2>test.err
cd ${DIR00}/benchspec/CINT2000/255.vortex/run/00000001  && ./vortex_base.${EXT00} lendian.raw  1>vortex.out2 2>vortex.err
cd ${DIR00}/benchspec/CINT2000/256.bzip2/run/00000001   && ./bzip2_base.${EXT00} input.random 2  1>input.random.out 2>input.random.err
cd ${DIR00}/benchspec/CINT2000/300.twolf/run/00000001   && ./twolf_base.${EXT00} test  1>test.stdout 2>test.err
cd ${DIR00}/benchspec/CFP2000/168.wupwise/run/00000001  && ./wupwise_base.${EXT00}  1>wupwise.out 2>wupwise.err
cd ${DIR00}/benchspec/CFP2000/171.swim/run/00000001     && ./swim_base.${EXT00} <swim.in 1>swim.out 2>swim.err
cd ${DIR00}/benchspec/CFP2000/172.mgrid/run/00000001    && ./mgrid_base.${EXT00} <mgrid.in 1>mgrid.out 2>mgrid.err
cd ${DIR00}/benchspec/CFP2000/173.applu/run/00000001    && ./applu_base.${EXT00} <applu.in 1>applu.out 2>applu.err
cd ${DIR00}/benchspec/CFP2000/177.mesa/run/00000001     && ./mesa_base.${EXT00} -frames 10 -meshfile mesa.in -ppmfile mesa.ppm   
cd ${DIR00}/benchspec/CFP2000/178.galgel/run/00000001   && ./galgel_base.${EXT00} <galgel.in 1>galgel.out 2>galgel.err
cd ${DIR00}/benchspec/CFP2000/179.art/run/00000001      && ./art_base.${EXT00} -scanfile c756hel.in -trainfile1 a10.img -stride 2 -startx 134 -starty 220 -endx 139 -endy 225 -objects 1  1>test.out 2>test.err
cd ${DIR00}/benchspec/CFP2000/183.equake/run/00000001   && ./equake_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/187.facerec/run/00000001  && ./facerec_base.${EXT00} <test.in 1>test.out 2>test.err
cd ${DIR00}/benchspec/CFP2000/188.ammp/run/00000001     && ./ammp_base.${EXT00} <ammp.in 1>ammp.out 2>ammp.err
cd ${DIR00}/benchspec/CFP2000/189.lucas/run/00000001    && ./lucas_base.${EXT00} <lucas2.in 1>lucas2.out 2>lucas2.err
cd ${DIR00}/benchspec/CFP2000/191.fma3d/run/00000001    && ./fma3d_base.${EXT00}  1>fma3d.out 2>fma3d.err
cd ${DIR00}/benchspec/CFP2000/200.sixtrack/run/00000001 && ./sixtrack_base.${EXT00} <inp.in 1>inp.out 2>inp.err
cd ${DIR00}/benchspec/CFP2000/301.apsi/run/00000001     && ./apsi_base.${EXT00}  1>apsi.out 2>apsi.err
