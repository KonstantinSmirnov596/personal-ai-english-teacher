# Requisitos de hardware

O Voice Tutor reconhece a sua voz, fala como tutor e avalia a sua pronúncia no seu próprio computador, com a sua placa de vídeo NVIDIA. O áudio nunca sai do computador. Esta página explica cada item que o instalador (`install.cmd`) e o assistente de configuração inicial verificam, e o que fazer quando algum não é atendido.

## Mínimo e recomendado

| Componente | Mínimo | Recomendado |
| --- | --- | --- |
| Windows | Windows 10 22H2 (compilação 19045) ou Windows 11, 64 bits | Windows 11 |
| Placa de vídeo | NVIDIA, arquitetura Turing ou mais nova (GeForce RTX série 20 em diante), 6 GB de memória de vídeo | NVIDIA com 8 GB ou mais |
| Driver da NVIDIA | 572.61 ou mais novo | O driver estável mais recente |
| Memória (RAM) | 16 GB | 16 GB ou mais |
| Disco | 15 GB livres para a instalação, em um SSD | 20 GB livres |
| Microfone | Qualquer um | Headset ou fones de ouvido |
| Rede | Para a instalação e para o modelo de linguagem | — |

O instalador para antes de baixar qualquer coisa quando falta um item obrigatório, e diz qual. O assistente mostra os mesmos itens na segunda etapa, com a memória de vídeo livre medida naquele momento.

## O que cada item significa

<a id="gpu"></a>
### Placa de vídeo

O reconhecimento de voz (Whisper), a voz do tutor (Kokoro) e a avaliação de pronúncia (wav2vec2) rodam em uma placa de vídeo NVIDIA com CUDA. Um computador que só tem gráficos Intel ou AMD não consegue rodá-los. Se o seu computador tem duas placas de vídeo (um notebook com Intel e NVIDIA), confira se o driver da NVIDIA está instalado: a verificação usa a primeira placa NVIDIA que encontra.

<a id="driver"></a>
### Driver da NVIDIA

O aplicativo usa o CUDA 12.8 Update 1, que precisa do driver 572.61 ou mais novo ([notas de versão do CUDA, "Corresponding Driver Versions"](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)). Atualize o driver em [nvidia.com/drivers](https://www.nvidia.com/drivers) ou pelo aplicativo NVIDIA, reinicie o computador e execute o instalador de novo. Se a verificação diz que o driver está faltando, o Windows está usando um driver de vídeo genérico: instale o da NVIDIA.

<a id="architecture"></a>
### Arquitetura da placa

As bibliotecas CUDA que o aplicativo usa têm código para a capacidade de computação 7.5 (Turing) em diante. A GeForce RTX série 20 (por exemplo, a RTX 2060) é a geração mais antiga confirmada. Placas anteriores (GTX série 10, capacidade de computação 6.1) não são compatíveis. A verificação lê a capacidade de computação pelo driver, então você não precisa procurar o seu modelo.

<a id="vram"></a>
### Memória de vídeo

O instalador e o aplicativo precisam de uma placa com cerca de 6 GB de memória de vídeo. O assistente mede a memória de vídeo *livre*, porque a área de trabalho do Windows, os navegadores e os jogos usam uma parte:

- 7 GB livres ou mais: perfil `completo`;
- de 5 a 7 GB livres: perfil `compacto`;
- menos de 5 GB livres em uma placa que, fora isso, serve: feche jogos, editores de vídeo e outros programas que usam a placa de vídeo e clique em «Verificar de novo». Se você continuar, o aplicativo usa o `compacto`.

No computador de desenvolvimento (placa de 8 GB), o aplicativo usou no máximo 3,7 GB no `completo` e 2,5 GB no `compacto` durante uma sessão completa.

<a id="ram"></a>
### Memória (RAM)

Com menos de 16 GB o aplicativo funciona, mas carregar os modelos e a janela junto com outros programas pode deixá-lo lento. É um aviso, não impede a instalação.

<a id="disk"></a>
### Espaço em disco

A instalação precisa de cerca de 15 GB: o ambiente Python (cerca de 5 GB), os modelos (cerca de 3,2 GB) e o cache de pacotes (cerca de 5 GB). Enquanto o aplicativo roda, as gravações, o registro e o banco de dados precisam de espaço: deixe pelo menos 2 GB livres.

<a id="power"></a>
### Alimentação

Na bateria, o notebook reduz a velocidade da placa de vídeo para economizar energia, e o tutor responde mais tarde. O aplicativo avisa uma vez; conecte o carregador para ter a melhor velocidade.

<a id="windows"></a>
### Versão do Windows

O aplicativo é testado no Windows 10 22H2 e no Windows 11. Uma compilação mais antiga só gera um aviso; se algo não funcionar, atualize o Windows primeiro.

## Perfis

<a id="profiles"></a>

| Perfil | Quando | Reconhecimento de voz | Modelo de pronúncia |
| --- | --- | --- | --- |
| `completo` | 7 GB de memória de vídeo livres ou mais | Whisper turbo, `float16` | Fica na memória depois de carregado; as marcas de pronúncia na conversa ficam ativadas |
| `compacto` | De 5 a 7 GB livres | Whisper turbo, `int8_float16` (menos memória, a mesma precisão nos nossos testes) | É carregado quando a «Leitura» ou uma avaliação precisa dele e descarregado depois de 5 minutos sem uso; as marcas de pronúncia na conversa vêm desativadas |

A etapa de medição do assistente (cerca de um minuto) confirma o perfil. O `completo` passa para `compacto` quando o tempo entre o fim da sua resposta e o primeiro som do tutor (sem contar o modelo de linguagem) passa de 1,2 s, ou quando sobram menos de 0,8 GB de memória de vídeo livre depois do carregamento.

Para escolher o perfil você mesmo, abra Configurações → Desempenho. «Automático» segue a medição. Essa página também mostra a última medição e executa o assistente novamente.

## Quando falta memória de vídeo

Se você abrir um jogo ou outro programa que usa a placa de vídeo enquanto pratica:

- o aplicativo primeiro libera o modelo de pronúncia;
- se ainda faltar memória para o reconhecimento de voz, o aplicativo avisa e pede para você fechar outros programas; ele não fecha sozinho;
- os drivers recentes da NVIDIA no Windows também podem usar a memória do sistema quando a memória de vídeo está cheia ([NVIDIA: uso da memória do sistema](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion), em inglês). Tudo continua funcionando, só que mais devagar.

Quando a placa de vídeo ou o driver muda, o aplicativo propõe repetir a verificação do computador e a medição na próxima inicialização.
