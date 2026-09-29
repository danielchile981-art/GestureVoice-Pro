# Checklist para publicação

- [ ] Compilar `clean assembleDebug`, `test`, `lint` com SDK 36.
- [ ] Instalar o APK de debug, executar os fluxos reais e examinar logcat.
- [ ] Validar fala local e duração da bateria em aparelhos distintos.
- [ ] Medir startup, FPS, tamanho do APK e consumo real; as metas ainda não foram comprovadas.
- [ ] Finalizar tradução de todas as strings da interface (a UI inicial está em pt-BR).
- [ ] Enviar política de privacidade com contato e URL reais.
- [ ] Revisar declaração da API Accessibility e texto de consentimento com a política Play vigente.
- [ ] Declarar tipo de foreground service `microphone` no Play Console.
- [ ] Criar keystore seguro, assinar AAB/APK, guardar senhas fora do Git.
- [ ] Fazer testes fechados na Play Console, preencher Data safety e capturas reais.
- [ ] Só então criar tag, release e publicar repositório.
