# passgen
PassGen - Interactive 
# 🔐 PassGen — Code by Cyber Marmouts

A realistic **wordlist generator** based on personal data (full name, nickname, birthday, username, email, and up to 3 extra keywords).  
Designed for **ethical use in authorized security tests** and digital forensics investigations.

---

## ✨ Features
- Combines **name, nickname, username, email, and birthday** into likely password candidates.
- Supports **leet-speak transformations** (e.g., `a → 4`, `e → 3`, `s → $`).
- Adds **common suffixes** (`123`, `!`, `2024`, etc.).
- Generates variations with **separators** (`.`, `_`, `-`).
- Automatic **reverse tokens** (`John → nhoJ`).
- Allows **extra words** (up to 3, e.g., hobbies, favorite team, city).
- **Performance control**: customizable max combinations (`cap`, default: `150,000`).
- Runs in both **Interactive mode** (prompts) and **CLI mode** (arguments).
- Output is **deduplicated** and sorted by **length** and **alphabetical order**.

---

## 📦 Installation
Clone the repository:
```bash
git clone https://github.com/DonMarmmueta/passgen.git
cd passgen
chmod +x passgen.py
python3 passgen.py
or
python3 passgen.py --interactive
<img width="521" height="320" alt="image" src="https://github.com/user-attachments/assets/5187eb86-e2a0-4db7-ac3d-6ae78fdd5e77" />


