<div align="center">
    <img src="CommandCompanion-logo/cover.png" alt="ComComp logo" style="width: 700px; height: 300px;">
</div>

<div align="center">
  
![GitHub stars](https://img.shields.io/github/stars/negativenagesh/CommandCompanion?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/negativenagesh/CommandCompanion?style=social)
![GitHub forks](https://img.shields.io/github/forks/negativenagesh/CommandCompanion?style=social)
![GitHub license](https://img.shields.io/github/license/negativenagesh/CommandCompanion)
</div>

CommandCompanion is an AI-powered assistant that allows users to control their Fedora system effortlessly using natural language commands. Whether it's launching applications, creating files with AI-generated content, or performing system tasks, CommandCompanion automates these operations with precision.

<div align="center">
  <img src="demo/demo.gif" alt="CommandCompanion Demo" width="800">
</div>

## Setup for Fedora

1. Clone the repository and give a star:

```zsh
git clone https://github.com/yourusername/CommandCompanion.git
cd CommandCompanion
```

2. Install required system packages:

```zsh
sudo dnf install python3-tkinter python3-pip python3-devel
```

3. Create a venv:

```zsh
python3 -m venv .venv
source venv/bin/activate
```

4. Install dependencies:

```zsh
pip isntall -r pkgs.txt
```

5. Setup .env with your gemini API key:

```zsh
echo "GENAI_API_KEY=your_api_key_here" > .env
```

6. Run the application:

```zsh
python main.py
```

## Usage

Simply type a command in natural language, such as:

"open Firefox and search for Python tutorials"
"create a Python file with a neural network model"
"build a portfolio website"
"empty the trash"
