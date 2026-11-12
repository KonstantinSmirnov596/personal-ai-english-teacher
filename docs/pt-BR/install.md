# Como instalar o Voice Tutor

A instalação é feita com um clique duplo e sem permissão de administrador. Você não precisa de Python nem de outra ferramenta: o instalador traz as dele. Conte com 20 a 60 minutos, conforme a sua conexão com a internet; quase todo o tempo vai no download de cerca de 8 GB.

## Antes de começar

- Confira os requisitos no `hardware.md`: uma placa de vídeo NVIDIA GeForce RTX série 20 ou mais nova com 6 GB de memória de vídeo, driver 572.61 ou mais novo, Windows 10 22H2 ou Windows 11, 16 GB de RAM.
- Deixe cerca de 15 GB livres na unidade onde você colocar o aplicativo e na unidade do seu perfil de usuário.
- Tenha em mãos uma chave de API ou um servidor local de modelos (veja o `api-keys.md`). Você também pode adicionar depois.

## Download

<a id="download"></a>

Baixe o `VoiceTutor-<versão>.zip` na página de versões (Releases) do projeto no GitHub. Ao lado, o `SHA256SUMS.txt` traz a soma de verificação; para conferir, abra o PowerShell na pasta de downloads e compare:

```powershell
Get-FileHash .\VoiceTutor-0.1.0.zip -Algorithm SHA256
```

## Extração

<a id="extract"></a>

1. Clique com o botão direito no `.zip` → Propriedades → marque «Desbloquear» → OK. Assim você evita avisos de segurança para cada script.
2. Extraia em uma pasta sua com um caminho curto, por exemplo `C:\VoiceTutor` ou `Documentos\VoiceTutor`. Evite `Arquivos de Programas` (precisa de permissão de administrador) e pastas sincronizadas com o OneDrive.

## Instalação

<a id="install"></a>

Clique duas vezes no `install.cmd`. Uma janela de console mostra cada etapa:

1. **Requisitos.** O instalador confere a placa de vídeo, o driver, a memória de vídeo, o espaço em disco e a memória antes de baixar qualquer coisa. Se faltar algo obrigatório, ele diz o quê e para (veja o `hardware.md`).
2. **Pastas.** Confere se é possível gravar na pasta do aplicativo e na sua pasta de dados, e se o caminho serve.
3. **Ferramentas e Python.** Baixa a ferramenta `uv` e o Python 3.12 dentro da pasta do aplicativo. Nada é adicionado ao sistema nem ao `PATH`.
4. **Pacotes.** Cerca de 5 GB de pacotes Python (PyTorch com CUDA, bibliotecas de voz), exatamente as versões do `uv.lock`.
5. **Modelos.** Cerca de 3,2 GB de modelos de voz em `%LOCALAPPDATA%\VoiceTutor\models`. Se a conexão cair, execute o `install.cmd` de novo: o download continua de onde parou.
6. **Fontes e detector de voz** para a janela do aplicativo.
7. **Atalhos.** Pergunta se você quer atalhos na área de trabalho e no menu Iniciar (Enter significa sim). Um atalho é sempre criado na pasta do aplicativo.

Cada download é fixado em uma versão exata e conferido com uma soma de verificação. No fim, o Voice Tutor abre com o assistente de configuração inicial.

## Primeira abertura

<a id="first-start"></a>

O assistente guia você em oito etapas: idioma, verificação do computador, modelos, uma medição curta, microfone, voz, conexão de API e nível. Cada etapa pode ser repetida depois em Configurações → Desempenho. O `usage.md` explica o aplicativo.

## Atualização

<a id="update"></a>

Baixe a versão nova, extraia por cima da pasta antiga (ou em uma nova) e execute o `install.cmd` de novo. Só é baixado o que mudou. As suas sessões, configurações, chaves e modelos ficam.

## Desinstalação

<a id="uninstall"></a>

Clique duas vezes no `uninstall.cmd`. Ele remove o ambiente Python, as ferramentas baixadas e os atalhos. Pergunta separadamente se você quer apagar os seus dados (`%LOCALAPPDATA%\VoiceTutor`) e as suas chaves de API; sem um «sim», eles ficam. Depois você pode apagar a pasta do aplicativo.

## Se algo der errado

Veja o `troubleshooting.md`. O `install.cmd` sempre pode ser executado de novo: ele continua de onde parou.
