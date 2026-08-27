@echo off
cd /d D:\at-affiliate
set LOG=D:\at-affiliate\output\cron.log
echo [%date% %time%] Start daily AT refresh >> "%LOG%"
python at_api.py build --niche finance >> "%LOG%" 2>&1
python at_api.py build --niche mother_baby >> "%LOG%" 2>&1
python at_api.py build --niche fashion >> "%LOG%" 2>&1
python at_api.py gen --niche finance >> "%LOG%" 2>&1
python at_api.py gen --niche mother_baby >> "%LOG%" 2>&1
python at_api.py gen --niche fashion >> "%LOG%" 2>&1
python at_api.py articles >> "%LOG%" 2>&1
python at_api.py site >> "%LOG%" 2>&1
cd /d D:\at-affiliate\site
git add -A >> "%LOG%" 2>&1
git -c user.email="at@local" -c user.name="AT Bot" commit -q -m "daily update" >> "%LOG%" 2>&1
git push -q >> "%LOG%" 2>&1
cd /d D:\at-affiliate
echo [%date% %time%] Done >> "%LOG%"
