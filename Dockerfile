# This is Docker file for zebrafish-monitor
FROM python:3.10-slim

# Install pip requirements.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["streamlit", "run", "📈Data_Viewer.py"]