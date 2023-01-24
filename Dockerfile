FROM python:3.8.13-slim

WORKDIR /pose

COPY . /pose

RUN apt-get update -q \
    && apt-get install ffmpeg libsm6 libxext6 git -y \
    && apt-get clean \
    && pip install --upgrade pip setuptools wheel  \
    && pip install -r requirements.txt --no-cache-dir \
    && rm -rf /var/lib/apt/lists/* \
    # && chmod 777 /pose

CMD ["chmod", "777", "/pose"]

# ENTRYPOINT ["gunicorn","--worker-tmp-dir", "/dev/shm", "main:app"]
ENTRYPOINT ["python3","main.py"]
# ENTRYPOINT ['/bin/bash','-l','-c']

# CMD ['python', 'main.py']