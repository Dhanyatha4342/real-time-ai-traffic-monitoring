prometheus --config.file=prometheus.yml --web.listen-address=:9091

prometheus --config.file=prometheus.yml --web.listen-address=:9090

flask --app app run

venv\Scripts\activate


(base) PS C:\Users\DHANIMANUHV> net stop grafana
The Grafana service is stopping.
The Grafana service was stopped successfully.

(base) PS C:\Users\DHANIMANUHV> net start grafana
The Grafana service is starting..
The Grafana service was started successfully.

Copy default.ini to custom.ini
Make the following changes in custom.ini
# set to true if you want to allow browsers to render Grafana in a <frame>, <iframe>, <embed> or <object>. default is false.
allow_embedding = true
x_frame_options = 

net stop grafana
 .\bin\grafana-server.exe --config conf\custom.ini