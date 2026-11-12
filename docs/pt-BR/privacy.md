# Privacidade

O Voice Tutor é um aplicativo de desktop sem contas, sem estatísticas de uso e sem telemetria. Esta página diz exatamente o que sai do seu computador, o que fica nele e como apagar.

## O que sai do computador

<a id="llm"></a>
### Enquanto você pratica

Só um tipo de tráfego: solicitações HTTPS para a URL base da sua conexão de API ativa (ou para `http://127.0.0.1` se você usa um servidor local como o Ollama). Elas contêm:

- o texto da conversa: as falas do tutor e a transcrição das suas respostas;
- o cenário e o seu nível, para o tutor se adaptar;
- para correções, traduções, dicas e o resumo: as frases de que eles tratam.

Elas nunca contêm áudio, o seu nome, o seu usuário do Windows, dados do computador nem as chaves das suas outras conexões. O que o provedor recebe segue a política de privacidade dele; leia antes de escolher um provedor, ou use um servidor local.

O aplicativo não procura atualizações, não envia relatórios de falha e não carrega fontes, scripts nem imagens da internet. Um teste (`tests/gpu/test_network.py`) registra cada conexão que o aplicativo abre durante uma sessão completa e falha se alguma for para outro lugar que não seja o modelo de linguagem.

<a id="install"></a>
### Durante a instalação

O `install.cmd` baixa, uma única vez: a ferramenta `uv` a partir da versão publicada no GitHub, o Python a partir das versões do `python-build-standalone` no GitHub, os pacotes Python do PyPI e do índice de pacotes do PyTorch, os modelos de voz do Hugging Face, e as fontes e o detector de voz do registro do npm. Cada download é fixado em uma versão exata e conferido com uma soma de verificação. Nada sobre você é enviado além do que qualquer download envia (o seu endereço IP).

## O que fica no computador

<a id="local"></a>

Todo o resto fica em `%LOCALAPPDATA%\VoiceTutor`:

| O quê | Onde | Por quanto tempo |
| --- | --- | --- |
| Sessões, transcrições, correções, vocabulário, resultados de pronúncia, configurações, medições do computador | `voicetutor.db` (SQLite) | Até você apagar |
| Gravações das suas respostas | `audio\` | 30 dias por padrão (Configurações → Dados; 0 não guarda nenhuma) |
| Registro | `logs\` | No máximo 6 arquivos de 2 MB; o mais antigo é substituído |
| Modelos de voz | `models\` | Até você desinstalar |
| Perfil do navegador da janela (permissão do microfone) | `edge-profile\` | Até você desinstalar |

As chaves de API ficam no Gerenciador de Credenciais do Windows com o nome `VoiceTutor`, nunca em um arquivo, no registro ou no banco de dados. A janela só recebe os quatro últimos caracteres de uma chave.

<a id="logs"></a>
### Registro

Por padrão o registro não contém o texto das suas conversas: só eventos, tempos e códigos de erro. Para um relato de erro, você pode ativar Configurações → Dados → «Registro detalhado», que também grava o texto de cada turno; a janela avisa, e é bom desativar depois. O `scripts\collect_diagnostics.ps1` junta versões, o perfil e o registro para um relato de erro e tira deles as chaves e o texto dos turnos.

<a id="server"></a>
### O servidor local

O núcleo do aplicativo só escuta em `127.0.0.1` (o seu próprio computador), na primeira porta livre entre 47613 e 47622. Ele só aceita a janela do aplicativo: um token de abertura de uso único, um cookie de sessão e a verificação dos cabeçalhos `Origin` e `Host` deixam de fora outros sites e programas.

## Como apagar os seus dados

<a id="delete"></a>

- Configurações → Dados → «Excluir todos os dados» apaga sessões, correções, estatísticas, vocabulário e gravações; marque a caixa para apagar também as conexões de API e as chaves delas. As configurações ficam.
- Configurações → Dados → «Exportar todos os dados» salva tudo antes em JSON ou CSV, se você quiser uma cópia.
- O `uninstall.cmd` remove o aplicativo, o ambiente Python e os atalhos; ele pergunta antes de apagar `%LOCALAPPDATA%\VoiceTutor` e as suas chaves.
