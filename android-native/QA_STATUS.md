# Estado da validação — 29/09/2026

## Executado neste ambiente

- `./gradlew clean assembleDebug`: **PASSOU**, após corrigir a referência ao modo de tema na tela de configurações.
- `./gradlew test`: **PASSOU** para debug e release. Os testes unitários cobrem reamostragem/comparação de gestos e equivalência exata de frases com normalização.
- `./gradlew lint`: **PASSOU**, 0 erros e 19 avisos. Há avisos de kapt, recursos de cores reservados, ícones e metadados de backup; não representam teste de execução em aparelho.
- APK de debug compilado localmente, aproximadamente 18 MB: **NÃO distribuído**.
- `adb install -r ...`: **BLOQUEADO**, `adb: no devices/emulators found`; não há `/dev/kvm` neste ambiente.

## Bloqueios de entrega

A execução em aparelho, logcat, fluxos reais, serviço em foreground, Acessibilidade e reconhecimento de fala **não foram verificados**. Por essa razão, não há APK de release assinado, tag `v1.0.0`, repositório público nem GitHub Release. As imagens em `assets/store/` são mockups conceituais, não capturas do aplicativo instalado.

## Escopo implementado

Kotlin/Compose, Hilt, Room, DataStore, AES-GCM no Android Keystore para pontos dos gestos, desenho de um traço, vínculo de frase, reconhecimento local do Android 12+, `AccessibilityService.dispatchGesture`, estatísticas simples, consentimento e notificação persistente.

## Ainda necessário para a visão completa

Teste em aparelho, revisão de políticas Play, tradução integral, wake word, assobio/palma/estalo, calibração da sensibilidade, gesto multitraço, backup JSON, áudio/feedback, animações avançadas, screenshots reais, medição de FPS/bateria/startup e release assinado. Não há promessa de funcionamento contínuo em todos os fabricantes. O código usa o reconhecedor local do sistema, que pode não estar instalado.
