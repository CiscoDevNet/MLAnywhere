cd ./view_container/webserver/static/bolts_demo/
zip -r bolts_demo.zip bolts_demo.ipynb demo_client.ipynb labels.txt bxm 3pax
mv bolts_demo.zip ../
cd ../../../../

docker build -t mimaurer/mlav2setup:test ./setup_container/
docker push mimaurer/mlav2setup:test

docker build -t mimaurer/mlav2web:test ./view_container/
docker push mimaurer/mlav2web:test