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

### 🏠 Home Assistant OS Apps (Add-on)
1. 添加加载项仓库
   * 打开 HomeAssistant，点击左侧菜单的 **配置 (Settings)** -> **加载项 (Add-ons)**
   * 点击右下角的 **加载项商店 (Add-on Store)**
   * 点击右上角的三个点 -> **仓库 (Repositories)**
   * 在输入框填入：`https://gitee.com/hasscc/addons`, 点击添加
   [![添加加载项仓库](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgitee.com%2Fhasscc%2Faddons)

2. **安装加载项**：
   * 刷新页面，找到并点击 **`千问TTS`**
   * 点击 **安装 (Install)**
   * 启动并设置开机启动


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

### 🏠 Home Assistant
1. 安装 AI Conversation 集成
   > 点击这里 [一键安装](https://my.home-assistant.io/redirect/hacs_repository/?category=integration&owner=hasscc&repository=ai-conversation)，安装完记得重启HA
2. [添加 AI Conversation 服务](https://my.home-assistant.io/redirect/config_flow_start/?domain=ai_conversation)，配置模型提供商
   > 服务商: 自定义; 接口: `http://4e0de88e-qwen-tts/v1`; 密钥留空
3. 添加TTS模型，模型ID随意
4. 配置语音助手


## 🔗 Links / 相关链接
- https://qwen-qwen3-tts-demo.ms.show
