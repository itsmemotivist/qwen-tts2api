# 🗣️ Qwen TTS

## Install / 安装

### 🐳 Docker compose
```shell
mkdir /opt/qwen-tts
cd /opt/qwen-tts
wget https://raw.githubusercontent.com/aahl/qwen-tts2api/refs/heads/main/docker-compose.yml
docker compose up -d
```

### 🐳 Docker run
```shell
docker run -d \
  --name qwen-tts \
  --restart=unless-stopped \
  -p 8825:80 \
  ghcr.io/aahl/qwen-tts2api:main
```


## 💻 Usage / 使用

> 通过接口`http://localhost:8825/v1/models`可获取全部音色

### 🌐 CURL调用示例
```shell
curl --request POST \
  --url http://localhost:8825/v1/audio/speech \
  --header 'Content-Type: application/json' \
  --data '{"voice":"vivian", "input":"hello"}' \
  --output audio.wav
```

## 🔗 Links / 相关链接
- https://qwen-qwen3-tts-demo.ms.show
