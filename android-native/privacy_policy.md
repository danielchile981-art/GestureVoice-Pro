# Política de privacidade — GestureVoice

Atualização: 29 de setembro de 2026.

O GestureVoice permite salvar traços desenhados e executar esses traços mediante frases configuradas pelo usuário. Os pontos dos gestos são armazenados no banco local e criptografados com AES-256-GCM usando uma chave do Android Keystore. Frases dos gatilhos e histórico de execuções ficam no banco local. Não criamos conta, não usamos analytics e não transmitimos esses dados para servidores nossos.

Quando a escuta está ativa, o aplicativo usa o microfone e a implementação **no dispositivo** do reconhecimento de fala oferecida pelo Android. O GestureVoice não guarda gravações e só habilita a escuta onde o sistema informa que esse recurso local está disponível (Android 12 ou superior). O serviço em primeiro plano mostra uma notificação e pode ser parado por ela. Um pacote de fala instalado pelo sistema poderá ter suas próprias práticas de privacidade; consulte o fornecedor do reconhecedor.

O serviço de Acessibilidade pode observar eventos da interface enquanto habilitado pelo usuário, mas o GestureVoice não os registra nem envia. Ele usa `dispatchGesture()` apenas para reproduzir gestos escolhidos. A Acessibilidade é ativada manualmente nas configurações do Android e pode ser desativada a qualquer momento.

Para apagar os dados, exclua os gestos no aplicativo ou limpe os dados/desinstale o app. Não fazemos backup em nuvem. A chave do Keystore não acompanha backups. Esta versão desativa backup do Android para evitar restauração de dados sem a chave.

Contato para solicitação de privacidade: o desenvolvedor deverá inserir um endereço de suporte válido antes da publicação na Play Store.
