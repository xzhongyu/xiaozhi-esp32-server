# 晓智 ESP32 Server 项目结构与模型配置分析

## 1. 项目核心结构概览

本项目是一个为 ESP32 语音助手提供云端支持的后端服务（xiaozhi-esp32-server），涵盖了语音端点检测（VAD）、语音识别（ASR）、大语言模型（LLM）、语音合成（TTS）、意图识别、智能体工具（Tools/Plugins）等完整链路。

### 核心目录树分析

- **`config/`**: 配置加载、日志管理 (`logger.py`, `config_loader.py`, `settings.py`) 以及基础资产 (`assets/` 下包含绑定提示音、唤醒词、TTS 提示音等)。
- **`core/`**: 业务核心逻辑
  - **`api/`**: HTTP 接口路由（OTA 接口、视觉分析接口等）。
  - **`handle/`**: WebSocket 交互、消息解析、意图路由、设备通信及核心处理管线（`textHandle`, `receiveAudioHandle`, `sendAudioHandle` 等）。
  - **`providers/`**: 大模型/ AI 能力接入层，实现了标准化的 Base 类与各种厂商的对接：
    - **`asr/`**: 语音识别（阿里、百度、腾讯、豆包、OpenAI、FunASR 等）。
    - **`tts/`**: 语音合成（EdgeTTS、GPT-SoVITS、火山/豆包、阿里、腾讯、Minimax 等）。
    - **`llm/`**: 核心对话模型（DeepSeek、Qwen、Doubao、Ollama、Dify、Coze、Gemini 等）。
    - **`vad/`**: 语音端点检测（Silero VAD）。
    - **`vllm/`**: 视觉多模态大模型。
    - **`memory/`**: 长短记忆管理（Mem0AI、PowerMem）。
    - **`intent/`**: 意图识别（无意图、LLM 意图、Function Call 意图）。
    - **`tools/`**: IoT 设备控制、MCP 协议、扩展插件工具管线。
  - **`utils/`**: 各类工具函数（音频编解码、上下文处理、缓存、唤醒词处理等）。
- **`models/`**: 本地离线模型存放目录（ASR 和 VAD 模型存放地）。
- **`plugins_func/`**: 大模型 Function Call 函数库（查天气、查新闻、HomeAssistant 控制、播放音乐等）。
- **`test/` & `performance_tester/`**: 包含性能基准测试脚本和前端 Web 测试界面（基于 Live2D）。
- **`funasr-server/`**: FunASR 独立 Docker 容器化部署脚本（含 `docker-compose.yml`, `start.sh`, `stop.sh` 等）。
- **`config.yaml`**: 服务端核心主配置文件，串联了所有的底层 Provider 选择。

---

## 2. 本地部署核心模型版本与用途

项目中直接集成或推荐本地部署的核心开源模型如下：

| 模块类别 | 本地模型目录 / 名称 | 作用说明 |
| :--- | :--- | :--- |
| **ASR (语音识别)** | `models/SenseVoiceSmall` | 阿里开源的 SenseVoiceSmall，用于本地 FunASR 语音转文字（高效率、多语种）。配置项为 `ASR.FunASR.model_dir`。|
| **ASR (语音识别)** | `models/sherpa-onnx-*` (例如 paraformer) | 适用于低性能设备的 Sherpa-ONNX 本地识别（中文专用 paraformer 或多语种 sense_voice）。|
| **VAD (端点检测)** | `models/snakers4_silero-vad` | Silero VAD（基于 ONNX）。负责在音频流中实时截断，判断用户说话是否停止。配置默认需确保指向正确的 `.onnx` 路径。|
| **TTS (语音合成)** | `models/vits-melo-tts-zh_en` | Melo TTS（VITS 架构）中英双语合成模型。注：目前该模型仅做文件预留，在代码中主要走云端/外部 HTTP TTS 服务。|

---

## 3. 云端与外部模型配置清单 (基于 `config.yaml`)

服务端支持极为丰富的云端服务对接，可通过在配置中修改 `selected_module` 来灵活切换。以下为主要的模型厂商配置清单及版本特性：

### 3.1 语音识别 (ASR)
- **FunASR / FunASRServer**: 支持阿里 `SenseVoiceSmall`、`paraformer-large`，通过本地或独立 Docker 运行。
- **DoubaoASR / DoubaoStreamASR**: 字节火山引擎，支持多语种流式识别，使用大模型技术。
- **AliyunASR / AliyunBLStreamASR**: 阿里百炼 Paraformer，支持热词、语义断句。
- **OpenaiASR**: `gpt-4o-mini-transcribe`。
- **GroqASR**: `whisper-large-v3-turbo`（基于 Groq 的极速 Whisper 推理）。
- **Qwen3ASRFlash**: 阿里百炼 `qwen3-asr-flash`，多模态基座识别。
- **其他厂商**: 腾讯 (TencentASR)、百度 (BaiduASR)、科大讯飞 (XunfeiStreamASR)、离线方案 (VoskASR, SherpaASR)。

### 3.2 大语言模型 (LLM)
- **AliLLM**: `deepseek-v3.2` / `qwen` 等（基于阿里百炼兼容接口）。
- **DoubaoLLM**: `doubao-1-5-pro-32k-250115`（火山方舟）。
- **DeepSeekLLM**: `deepseek-chat`。
- **ChatGLMLLM**: `glm-4-flash`。
- **GeminiLLM**: `gemini-2.0-flash`。
- **OllamaLLM**: 默认 `qwen2.5`，支持纯本地离线推理。
- **XinferenceLLM**: 本地托管大模型（如 `qwen2.5:72b-AWQ`）。
- **工作流与网关**: DifyLLM、CozeLLM、FastgptLLM、VolcesAiGatewayLLM。

### 3.3 视觉语言大模型 (VLLM)
- **ChatGLMVLLM**: 智谱 `glm-4v-flash`。
- **QwenVLVLLM**: 阿里 `qwen2.5-vl-3b-instruct`。

### 3.4 语音合成 (TTS)
系统内置多达 20+ 种 TTS 引擎对接，涵盖了流式和非流式：
- **EdgeTTS**: 微软免费 TTS (`zh-CN-XiaoxiaoNeural`)。
- **DoubaoTTS / HuoshanDoubleStreamTTS**: 字节火山引擎（支持 `zh_female_wanwanxiaohe_moon_bigtts` 等高级音色及混音特性）。
- **CosyVoice (硅基流动)**: `FunAudioLLM/CosyVoice2-0.5B`。
- **GPT_SOVITS (V2/V3)**: 强大的开源声音克隆模型（通过本地 HTTP API 调用）。
- **FishSpeech**: 优秀的开源开源语音生成模型。
- **AliyunStreamTTS / AliBLTTS**: 阿里 CosyVoice 大模型流式合成（如 `longxiaochun`, `longcheng_v2`）。
- **其他厂商/社区服务**: Minimax、腾讯、302AI、机智云、ACGNTTS、OpenAI、LinkeraiTTS、PaddleSpeechTTS 等。

---

## 4. 核心配置与模块加载逻辑

1. **组合切换 (`selected_module`)**
   在 `config.yaml` 或管理端界面中，使用者可以自由拼装 AI 链路。例如 `VAD` 选 `SileroVAD`，`ASR` 选 `FunASR`，`LLM` 选 `AliLLM`，`TTS` 选 `EdgeTTS`。
2. **初始化机制 (`modules_initialize.py`)**
   系统启动时，解析上述配置，实例化对应的 `Provider`（如 `core.providers.llm.openai.LLMProvider`），并注入到 `ConnectionHandler` 中。
3. **音频流管线 (`receiveAudioHandle.py` & `base.py`)**
   客户端将 Opus/PCM 音频通过 WebSocket 推流 -> VAD 实时端点检测 -> 检测到语音停止 -> 触发 ASR Provider 识别 -> 获取文本后进入 LLM -> 大模型流式返回 -> 截句后推入 TTS Provider -> 生成下行音频返回客户端。
