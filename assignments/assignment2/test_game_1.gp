set terminal pdfcairo dashed font "Helvetica,16"
set output "test_1.pdf"
set xlabel "Time"  textcolor rgbcolor "yellow"
set ylabel "Time used each 10 fps"  textcolor rgbcolor "yellow"
set border 15 linecolor rgbcolor "yellow"
set object 1 rectangle from screen 0,0 to screen 1,1 fillcolor rgb"black" behind
set key bottom right textcolor rgbcolor "yellow"
set yrange [0:]
plot "game_dataout_1.out" using ($1):2 w l lw 3 lc "#ff0000" title "Start"

