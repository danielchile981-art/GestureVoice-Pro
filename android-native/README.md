# GestureVoice

Projeto Android nativo em Kotlin + Jetpack Compose. Desenhe um gesto normalizado, vincule uma frase e reproduza o traço por `AccessibilityService.dispatchGesture()` ao ouvir a frase no reconhecedor local do Android.

## Escopo desta versão-fonte

Inclui tema escuro/claro, criação e biblioteca, frases exatas, histórico local, banco Room, pontos AES-256-GCM com Android Keystore, DataStore, serviço de microfone em primeiro plano e consentimento visível. A execução de um gesto exige ativação manual da Acessibilidade. A escuta de voz exige Android 12+ com reconhecedor no dispositivo instalado; em Android 8–11, criação e biblioteca estão disponíveis. Não inclui classificação de palma/assobio/estalo, wake word, captura MediaProjection, overlay, exportação JSON, calibração por app, múltiplos traços simultâneos ou motor Vosk/Whisper/YAMNet. O mecanismo de comparação de formas é uma variante simples de reamostragem do $1, com testes, mas não é usado para disparar frases.

## Build

Requisitos: JDK 17, Android SDK API 36 e Build Tools, Android Studio com Gradle 8.11.1. Abra a raiz do projeto e execute:

```bash
./gradlew clean assembleDebug
./gradlew test
./gradlew lint
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Os scripts `gradlew` baixam a distribuição oficial Gradle 8.11.1 na primeira execução; é necessário acesso à internet. O projeto compilou, passou nos testes unitários e lint neste ambiente, mas não foi instalado em aparelho ou emulador. Leia `QA_STATUS.md`. Não há APK distribuído.

## Permissões

Microfone: somente durante escuta iniciada pelo usuário. Acessibilidade: ativação manual para reproduzir os toques. Notificações: exibir controle persistente. O app não solicita overlay ou MediaProjection porque não precisa deles para executar gestos.

## Teste manual antes da publicação

Instalar em aparelho API 31–35; criar e salvar gesto; vincular frase; ativar Acessibilidade; conceder microfone; iniciar escuta em primeiro plano; minimizar; falar frase; conferir traço e histórico; parar pela notificação; verificar reinício, bloqueio de tela e ausência de vazamento de microfone. Testar API 26, TalkBack e rotação. Só gerar um release depois disso.

## Release

Crie um keystore privado (`keytool -genkeypair -v -keystore gesturevoice-release.jks -alias gesturevoice -keyalg RSA -keysize 3072 -validity 10000`), mantenha senhas fora do repositório, configure signing no Android Studio e exporte APK/AAB. Não faça upload de builds sem teste em aparelho.

## Licença

Copyright 2026. Todos os direitos reservados até definição de licença pelo autor.
