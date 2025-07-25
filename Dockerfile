FROM python:3.12

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" appgroup && \
    useradd --create-home --no-log-init -u "${UID}" -g "${GID}" appuser

WORKDIR /app

# 용량부족
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     wget \
#     gnupg \
#     unzip \
#     fonts-liberation \
#     libappindicator3-1 \
#     libasound2 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libcairo2 \
#     libcups2 \
#     libdbus-1-3 \
#     libgdk-pixbuf2.0-0 \
#     libglib2.0-0 \
#     libgtk-3-0 \
#     libnspr4 \
#     libnss3 \
#     libxss1 \
#     libxtst6 \
#     xauth \
#     libsecret-1-0 \
#     libu2f-udev \
#     libvulkan1 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxext6 \
#     libxfixes3 \
#     libxkbcommon0 \
#     libxrandr2 \
#     libxrender1 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Google Chrome PPA (개인 패키지 아카이브) 추가 및 Chrome Stable 버전 설치
# # 이 부분에서 apt-get update를 다시 하는 것은 필요합니다.
# RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google-chrome.gpg && \
#     echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && \
#     apt-get install -y google-chrome-stable && \
#     rm -rf /var/lib/apt/lists/*

# # 설치된 Chrome 버전에 맞는 ChromeDriver 자동 다운로드 및 설치
# # SeleniumBase (uc=True)를 사용하면 이 부분은 생략 가능성이 높지만,
# # 만약을 위해 일단은 유지합니다. 용량 문제가 계속되면 이 부분을 제일 먼저 제거해 보세요.
# # SeleniumBase 4.6+ 버전은 Selenium Manager가 자동 처리합니다.
# RUN CHROME_VERSION=$(google-chrome --version | sed -E 's/Google Chrome ([0-9]+)\..*/\1/') && \
#     CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
#     wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip -O /tmp/chromedriver.zip && \
#     unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm /tmp/chromedriver.zip
# # --- Chrome 및 ChromeDriver 설치 끝 ---

RUN apt-get update && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 셀리니움 임시 파일 생성
RUN chown -R appuser:appgroup /app
RUN mkdir -p /app/downloaded_files && chown appuser:appgroup /app/downloaded_files

USER appuser:appgroup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]