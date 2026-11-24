#!/bin/sh
mkdir -p results
env/bin/python3 ./read_pe_info.py --floppy=True ~/Desktop/Win95\ Collection/Microsoft\ Windows\ 95\ \(Retail\ Full\)\ \(3.5\ DMF\)/*.IMG > results/win95_english_rtm_floppy.csv
env/bin/python3 ./read_pe_info.py --floppy=True ~/Desktop/Win95\ Collection/Microsoft\ Windows\ 95\ \(4.00.950\)\ \[Spanish]\ \(5.25-1.2mb\)/*.img > results/win95_rtm_spanish.csv
env/bin/python3 ./read_pe_info.py --cdrom=True ~/Desktop/Win95\ Collection/Win95\ Catalan/Windows_95.iso > results/win95_rtm_catalan.csv
env/bin/python3 ./read_pe_info.py --cdrom=True ~/Desktop/Win95\ Collection/Microsoft\ Windows\ 95\ \(4.00.950\)\ \[Greek]/Windows_95.iso > results/win95_rtm_greek.csv
env/bin/python3 ./read_pe_info.py --cdrom=True ~/Desktop/Win95\ Collection/4.00.812__x86fre_Win95_he-beta.iso > results/win95_hebrew_beta_812.csv
env/bin/python3 ./read_pe_info.py --cdrom=True ~/Desktop/Win95\ Collection/Microsoft\ Windows\ 95\ \(4.00.950\)\ \[Arabic]/Windows_95.iso > results/win95_rtm_arabic.csv
env/bin/python3 ./read_pe_info.py --cdrom=True ~/Desktop/Win95\ Collection/Microsoft\ Windows\ 95\ Japanese\ PC-AT\ Build\ 950\ RC-2\ -\ 09-21-95.ISO > results/win95_jp_rc2.csv