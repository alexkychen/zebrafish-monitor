# This is Docker file for zebrafish-monitor
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "📈Data_Viewer.py", "--server.address", "0.0.0.0"]