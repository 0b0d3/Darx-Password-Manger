# 🛡️ DARX PASS™ – Secure Password Manager

DARX PASS™ is an offline, encrypted, and sleek password manager built with PySide6.  
Designed for cybersecurity professionals, privacy freaks, and anyone who values **security without compromise**.

> 🎯 Built by Abdullah Hussien (a.k.a. 0b0d3) – Founder of DARX Tech  
> ✨ 100% written in Python, without AI-generated code.

---

## 🧠 Features

- 🔐 Master password login (locally hashed with SHA256)
- 💾 Encrypted vault using `cryptography.Fernet`
- 🧠 Password strength indicator (weak / medium / strong)
- 🧊 Modern UI inspired by DARX design language
- 📋 Copy-to-clipboard without exposing the value
- 🎨 Theme switcher (light/dark-ready)
- 🔥 Single-file structure (`main.py`) – easy to read, audit, and fork
- 🧱 Fully offline – no cloud, no tracking, no bullshit

---

## 📂 Files Ignored for Security

These files are **not** included in the repo to protect the user:
.key.key
.master.hash
vault_data.json

## 📊 GitHub Stats

![Abdullah's GitHub Stats](https://github-readme-stats.vercel.app/api?username=0b0d3&show_icons=true&theme=tokyonight&count_private=true)

## 🔥 Most Used Languages

![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=0b0d3&layout=compact&theme=tokyonight)


## 🚀 Getting Started

```bash
git clone https://github.com/0b0d3/Darx-Password-Manger.git
cd Darx-Password-Manger
pip install -r requirements.txt
python main.py
