# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV models ""
ENV whitelist ""
ENV blacklist ""
ENV like_content ""
ENV download_content ""
ENV sqladd "192.168.1.128"
ENV sqlport 3306
ENV SQL_USER "python"
ENV SQL_PASS "Jnmjvt20!"
ENV SQL_DATABASE "vue_data"
ENV NUM_SUB_WORKERS 3
ENV LogSubscriptions -1
ENV SCRAPE_MEDIA True

# RUN apt-get update \
#  && apt-get install unixodbc -y \
#  && apt-get install unixodbc-dev -y \
#  && apt-get install freetds-dev -y \
#  && apt-get install freetds-bin -y \
#  && apt-get install tdsodbc -y \
#  && apt-get install --reinstall build-essential -y

# # populate "ocbcinst.ini"
# RUN echo "[FreeTDS]\n\
# Description = FreeTDS unixODBC Driver\n\
# Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
# Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini 

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# RUN mount -t cifs //192.168.1.87/USB_STORAGE/Temp/.folder /app/data -o username=admin,password=Jnmjvt09,vers=1.0
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app && chown -R appuser /tmp


USER appuser

VOLUME /app/data

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "start_ofd.py"]
