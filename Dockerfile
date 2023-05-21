# This is Docker file for zebrafish-monitor
FROM python:3.10-slim

# Install pip requirements.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Default Streamlit's web port is 8501
# To run docker image, use:
# 'docker run -d -p [any_port_number]:8501 [image_name]:[tags]'
CMD ["streamlit", "run", "📈Data_Viewer.py"]