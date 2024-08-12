#!/bin/bash

# Atualiza os pacotes do sistema
sudo apt-get update -y
sudo apt-get upgrade -y

# Instala o Python e pip
sudo apt-get install -y python3 python3-pip

# Instala o ffmpeg
sudo apt-get install -y ffmpeg

# Instala pacotes Python necessários
pip3 install -r requirements.txt

# Verifica a instalação das bibliotecas
python3 -c "import boto3; import pyffmpeg; print('boto3 and pyffmpeg installed successfully')"

echo "Instalação de dependências concluída."
