@echo off
echo --- GITHUB SYNC UTILITY ---
set /p repo="Enter GitHub Repo URL (e.g. https://github.com/user/repo.git): "
git remote add origin %repo%
git branch -M main
git push -u origin main
echo --- PUSH COMPLETE. GO TO RENDER.COM TO DEPLOY ---
pause
