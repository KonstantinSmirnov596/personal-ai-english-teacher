# Solução de problemas

A maioria dos problemas mostra uma mensagem no seu idioma na janela do aplicativo ou no console do instalador. Esta página explica os mais comuns. Se nenhum servir, veja «Como relatar um problema» no fim.

## Instalação

<a id="install-warning"></a>
### O Windows mostra um aviso de segurança

A versão publicada não é assinada com um certificado de assinatura de código, então o Windows pode avisar ao abrir o `install.cmd` a partir de um arquivo baixado. Antes de extrair, clique com o botão direito no `.zip` → Propriedades → marque «Desbloquear» → OK; ou escolha «Executar» (ou «Mais informações» → «Executar assim mesmo») no aviso. Os scripts são texto simples: você pode lê-los antes de executar.

<a id="install-requirements"></a>
### O instalador para na verificação de requisitos

Ele mostra o que falta (placa de vídeo, driver, memória de vídeo, espaço em disco) e aponta a seção correspondente do `hardware.md`. Nesse ponto nada foi baixado ainda. Resolva o item e execute o `install.cmd` de novo.

<a id="install-path"></a>
### O instalador reclama da pasta

Extraia o arquivo em uma pasta sua, por exemplo `C:\EnglishTeacher` ou `Documentos\EnglishTeacher`, não em `Arquivos de Programas` (precisa de permissão de administrador) nem em uma pasta sincronizada com o OneDrive. Espaços no caminho não são problema. Letras com acento também não, se o Windows mantiver um nome curto para a pasta; se o instalador disser o contrário, escolha um caminho sem acentos.

<a id="install-network"></a>
### Um download falha ou para

Execute o `install.cmd` de novo: cada etapa confere o que já está pronto, e os modelos continuam de onde pararam. Cada arquivo é conferido com uma soma de verificação; um arquivo danificado é baixado de novo. Um proxy ou firewall de empresa pode bloquear o GitHub, o PyPI ou o Hugging Face; tente outra rede.

<a id="antivirus"></a>
### Um antivírus apagou arquivos

Alguns antivírus colocam em quarentena arquivos do ambiente Python do aplicativo. Restaure-os, adicione a pasta do Personal AI English Teacher às exceções e execute o `install.cmd` de novo.

## Ao abrir o aplicativo

<a id="window"></a>
### A janela não abre

O aplicativo usa o Microsoft Edge como janela. Se o Edge foi removido, instale de novo em microsoft.com/edge. Se você abrir o aplicativo quando ele já está aberto, a janela existente vem para a frente em vez de abrir uma segunda cópia.

<a id="problems"></a>
### «A conversa não está disponível»

| Mensagem | O que fazer |
| --- | --- |
| O computador não atende aos requisitos mínimos | Veja a etapa de verificação do computador do assistente (botão «Ver detalhes») e o `hardware.md` |
| Nenhuma placa de vídeo NVIDIA compatível | Instale ou atualize o driver da NVIDIA e reinicie o computador e o aplicativo |
| Os modelos não foram encontrados | Execute o `install.cmd` de novo; depois abra a etapa de modelos do assistente e clique em «Verificar de novo» |
| Não foi possível carregar os modelos | Reinicie o computador; se repetir, execute o `install.cmd` de novo e relate o problema com o arquivo de diagnóstico |

## Microfone e som

<a id="microphone"></a>
### O tutor não me ouve

1. Windows: Configurações → Privacidade e segurança → Microfone: ative «Acesso ao microfone» e «Permitir que aplicativos da área de trabalho acessem o microfone».
2. Na janela do aplicativo: clique no ícone de cadeado ao lado do endereço e permita o microfone.
3. Configurações → Áudio e voz: escolha o microfone certo. A etapa de microfone do assistente (Configurações → Desempenho → «Executar o assistente novamente») mede o nível e o ruído do ambiente.

<a id="sound"></a>
### Não ouço o tutor

Configurações → Áudio e voz → caixas de som ou fones; clique em «Ouvir» para testar. Confira o mixer de volume do Windows.

<a id="auto-mode"></a>
### O modo automático envia a minha resposta cedo demais ou não envia

Configurações → Conversa → aumente a pausa permitida. Em um ambiente barulhento, repita a etapa de microfone do assistente: ela deixa o detector de voz mais rigoroso. Com caixas de som, use o modo manual ou fones de ouvido; senão o microfone ouve o tutor.

## Velocidade e memória

<a id="slow"></a>
### As respostas demoram

- Na bateria, o notebook reduz a velocidade da placa de vídeo: conecte o carregador.
- Jogos, editores de vídeo e outros programas que usam a placa de vídeo ocupam a memória dela: feche-os. Configurações → Desempenho → `compacto` usa menos memória de vídeo.
- A velocidade do modelo de linguagem depende do provedor e do modelo: Configurações → Conexões de API → «Testar» mostra o tempo de uma solicitação.

<a id="vram"></a>
### «Não há memória de vídeo suficiente»

Feche os programas que usam a placa de vídeo e repita a resposta. Se acontecer com frequência, escolha `compacto` em Configurações → Desempenho. Veja o `hardware.md`.

## O modelo de linguagem

<a id="llm"></a>

As mensagens sobre chaves, saldo, espera ou provedores que não respondem estão explicadas no `api-keys.md` («Quando algo dá errado»).

## Como relatar um problema

<a id="report"></a>

1. Execute o `scripts\collect_diagnostics.ps1` (botão direito → Executar com o PowerShell). Ele cria um arquivo com as versões, o perfil do computador e o registro, sem chaves e sem o texto das suas conversas.
2. Descreva o que você fez, o que esperava e o que aconteceu, e anexe o arquivo.

O registro fica em `%LOCALAPPDATA%\VoiceTutor\logs`. Nunca publique uma chave de API.

## Atualizar e reinstalar

<a id="update"></a>

Extraia a versão nova por cima da pasta antiga (ou em uma nova) e execute o `install.cmd`. As suas sessões, configurações, chaves e modelos ficam em `%LOCALAPPDATA%\VoiceTutor` e no Gerenciador de Credenciais do Windows. O `uninstall.cmd` remove o aplicativo e pergunta antes de apagar os seus dados.
