GESTUREVOICE PRO 0.2.0 - PACOTE ÚNICO
=====================================

Este ZIP substitui o projeto antigo por uma única versão consolidada.

NO TERMUX NORMAL:

1. Extraia:
cd ~
rm -rf gesturevoicepro_novo
mkdir gesturevoicepro_novo
cd gesturevoicepro_novo
unzip /sdcard/Download/GestureVoicePro_Completo.zip

Se o ZIP criou a pasta gesturevoicepro_completo:
cd gesturevoicepro_completo

2. Confira:
ls -la

3. Para substituir o conteúdo do repositório atual:
git init
git config user.name "danielchile981-art"
git config user.email "danielchile981@gmail.com"
git remote add origin https://github.com/danielchile981-art/GestureVoice-Pro.git
git fetch origin
git checkout -B main
git add .
git commit -m "GestureVoice Pro completo 0.2.0"
git push -u origin main --force

4. Depois abra GitHub > GestureVoice-Pro > Actions.
O workflow "Gerar APK Android" será executado automaticamente pelo push.
Quando ficar verde, abra a execução e baixe:
GestureVoice-Pro-APK

O APK estará dentro do ZIP de artefato.
