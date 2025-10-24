# 🤖 F.R.I.D.A.Y. — Unified Multimodal Intelligent AI Assistant

**An advanced, unified AI assistant built for text, vision & automation interaction**

![Last Commit](https://img.shields.io/github/last-commit/ArghDas/F.R.I.D.A.Y.-A-Unified-Multimodal-Intelligent-AI-Assistant?color=blue)  
![Python](https://img.shields.io/badge/python-100%25-blue)  
![Stars](https://img.shields.io/github/stars/ArghDas/F.R.I.D.A.Y.-A-Unified-Multimodal-Intelligent-AI-Assistant?style=social)

---

### 🔧 Built with:
![Python](https://img.shields.io/badge/Python-blue)  
![OpenAI-ChatGPT](https://img.shields.io/badge/OpenAI%20ChatGPT-purple)  
![CoHere](https://img.shields.io/badge/CoHere%20NLP-green)  
![Groq-LLaMA](https://img.shields.io/badge/Groq%20LLaMA-orange)  
![StableDiffusionXL](https://img.shields.io/badge/StableDiffusionXL-red)  
![Modular-Architecture](https://img.shields.io/badge/Modular%20Architecture-lightgrey)

---

## 📚 Table of Contents
- [Overview](#overview)  
- [Why F.R.I.D.A.Y.](#why-friday)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Configure API Keys](#configure-api-keys)  
- [Usage](#usage)  
- [Testing](#testing)  
- [Acknowledgements](#acknowledgements)

---

## 🧠 Overview

**F.R.I.D.A.Y.** is an advanced multimodal AI assistant inspired by Iron Man’s second-generation AI after J.A.R.V.I.S.  
Built in Python using a service-oriented, modular architecture, it integrates multiple APIs for unified intelligence:  
- Text generation via OpenAI ChatGPT  
- NLP tasks via CoHere  
- Vision & large-model inference via Groq LLaMA  
- Image generation via Stable Diffusion XL  

With F.R.I.D.A.Y., you get one assistant capable of text, vision and automation workflows in one platform.

---

## 💡 Why F.R.I.D.A.Y.?

This project achieves seamless interaction across domains by:
- 🧩 Modular components interacting independently but cohesively  
- 🤖 Multimodal intelligence: text, vision & automation in one assistant  
- 🔧 API-integrated: leveraging best-in-class AI platforms  
- 🎯 Automation ready: commands, image generation, system control  
- 🔒 Designed for extensibility and privacy with separate service modules  

---

## 🚀 Getting Started

### 🧱 Prerequisites
- Python 3.9 or newer  
- pip (Python package manager)  

---

### ⚙️ Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ArghDas/F.R.I.D.A.Y.-A-Unified-Multimodal-Intelligent-AI-Assistant.git
2. **Navigate to the project directory**
   ```bash
   cd F.R.I.D.A.Y.-A-Unified-Multimodal-Intelligent-AI-Assistant
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Configure API Keys**
   ```bash
   # Create a .env file in the project root and add your keys:
   echo "OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE" >> .env
   echo "COHERE_API_KEY=YOUR_COHERE_KEY_HERE" >> .env
   echo "GROQ_API_KEY=YOUR_GROQ_KEY_HERE" >> .env
   echo "SDXL_MODEL_KEY=YOUR_SD_XL_KEY_HERE" >> .env
   # Make sure .env is included in your .gitignore so your keys remain private

---

## 💻 Usage
To run **F.R.I.D.A.Y.** : python src/main.py

Then, interact with the assistant through text, voice, or visual commands — F.R.I.D.A.Y. will process and respond intelligently.

🗣️ Example Commands:
“Generate an image of a futuristic city at night”
“Summarize this article about AI ethics”
“Analyze this picture and describe it”
“Execute automation: open browser, search Python updates”

---

## 🧪 Testing
**F.R.I.D.A.Y.** uses the **pytest** framework for modular and integration testing.

To run the test suite: pytest

---

## 🌟 Acknowledgements
Special thanks to:
- [OpenAI ChatGPT](https://openai.com/)  
- [CoHere NLP](https://cohere.ai/)  
- [Groq LLaMA](https://groq.com/)  
- [Hugging Face Stable Diffusion XL](https://huggingface.co/)  
- The Python & open-source community 

