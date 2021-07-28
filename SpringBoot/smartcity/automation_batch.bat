cd /D "%~dp0"
git stash
git pull
pause
cd smartcity
call mvn install
cd target
docker build -f Dockerfile .
docker run -p 8080:8080 -e API_URL=https://rpixnvd51i.execute-api.us-east-1.amazonaws.com/deployedStage ecrystal/smart_city_repository:latest
cd ..\..