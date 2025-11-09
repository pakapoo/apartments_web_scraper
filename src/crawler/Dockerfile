FROM python:3.9-bookworm

# Install dependencies for Firefox and geckodriver
RUN apt-get update && apt-get install -y \
    wget unzip curl \
    libnss3 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 \
    libxrandr2 libgbm1 libasound2 libatk1.0-0 libgtk-3-0 \
    fonts-liberation libappindicator3-1 xdg-utils \
    firefox-esr

# Download geckodriver (Firefox driver) from the official GitHub release page
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.30.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-v0.30.0-linux64.tar.gz

# Install Python dependencies
WORKDIR /app
COPY requirements_docker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install specific MySQL Python connector
RUN pip install --force-reinstall mysql-connector-python

# Set the display environment for headless mode
ENV DISPLAY=:99
ENV FIREFOX_BIN=/usr/bin/firefox-esr
ENV GECKODRIVER_PATH=/usr/local/bin/geckodriver

# Copy project files
COPY . /app