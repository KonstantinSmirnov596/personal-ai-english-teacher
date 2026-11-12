# Chaves de API e provedores

As respostas do tutor, as correções, as traduções e o resumo da sessão vêm de um modelo de linguagem grande (LLM) de um provedor que você escolhe. O Voice Tutor envia a ele só o texto da conversa: nunca o áudio, nunca o seu nome. Você paga direto ao provedor; o Voice Tutor não tem contas nem cobranças próprias.

## Como escolher um provedor

A janela de conexões traz modelos de conexão prontos. Cada valor foi conferido na documentação do provedor (`docs/reports/providers.md`).

| Modelo de conexão | Tipo | Chave | Observações |
| --- | --- | --- | --- |
| DeepSeek | Nuvem | Obrigatória | Saldo pré-pago |
| OpenAI | Nuvem | Obrigatória | Limites de gasto por projeto |
| OpenRouter | Nuvem | Obrigatória | Uma chave para modelos de muitas empresas; você digita o nome do modelo (`empresa/modelo`) |
| Ollama | Local | Não precisa | Roda no seu computador; divide a placa de vídeo com o reconhecimento de voz (veja abaixo) |
| LM Studio | Local | Não precisa | Roda no seu computador; o mesmo aviso do Ollama |
| Outro compatível com OpenAI | Qualquer | Quase sempre | Qualquer serviço com um endpoint `chat/completions` compatível com OpenAI |

## Como criar uma chave com limite de gasto

Crie uma chave separada só para o Voice Tutor e coloque um limite, para que um erro nunca custe mais do que você decidiu.

<a id="deepseek"></a>
### DeepSeek

1. Entre em [platform.deepseek.com](https://platform.deepseek.com), abra «API keys» e crie uma chave ([DeepSeek: primeira chamada à API](https://api-docs.deepseek.com/), em inglês).
2. Faça uma recarga pequena. O DeepSeek funciona com saldo pré-pago: o uso é descontado do saldo e, quando ele acaba, o provedor responde «saldo insuficiente» (HTTP 402) em vez de cobrar mais ([códigos de erro](https://api-docs.deepseek.com/quick_start/error_codes), em inglês). O próprio saldo é o seu limite.

<a id="openai"></a>
### OpenAI

1. Na plataforma da OpenAI, crie um projeto para o Voice Tutor e, dentro dele, crie uma chave secreta ([gerenciar projetos](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform), em inglês).
2. Defina um limite de gasto mensal para o projeto e ative «Enforce a hard limit»: assim as solicitações falham quando o limite é atingido, em vez de só enviar um alerta ([limites de gasto](https://developers.openai.com/api/docs/guides/spend-limits), em inglês).

<a id="openrouter"></a>
### OpenRouter

1. Crie uma chave no painel do OpenRouter e coloque um limite de crédito, que pode ser renovado todo dia, semana ou mês ([limitar chaves](https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys), em inglês).
2. Escolha um modelo no OpenRouter e digite o identificador dele (por exemplo, `empresa/nome-do-modelo`) no campo «Modelo» da conexão.

<a id="local"></a>
### Ollama e LM Studio

Servidores locais não precisam de chave e não enviam nada para a internet. Mas um modelo de linguagem na sua própria placa de vídeo disputa a memória de vídeo com o reconhecimento de voz, a voz do tutor e a avaliação de pronúncia. Com 6 a 8 GB só cabe um modelo pequeno, e a qualidade das correções cai. Se quiser testar, escolha o perfil `compacto` em Configurações → Desempenho e um modelo pequeno.

## Como adicionar a chave no aplicativo

1. Abra Configurações → Conexões de API → Adicionar conexão (o assistente de configuração inicial mostra o mesmo formulário na etapa 7).
2. Escolha o modelo de conexão, cole a chave em «Chave de API», clique em «Salvar» e depois em «Testar». O teste envia uma solicitação curta e mostra quanto tempo levou ou o erro do provedor.
3. A primeira conexão fica ativa. Se você tiver várias, o botão redondo da tabela escolhe a ativa; a mudança vale a partir da próxima resposta.

A chave fica guardada no Gerenciador de Credenciais do Windows, não em um arquivo. A janela só mostra os quatro últimos caracteres. Nunca envie uma chave para ninguém, nem em um relato de erro.

## Quanto custa uma conversa

<a id="cost"></a>

Os provedores cobram por token. Um token é um pedaço de palavra; o DeepSeek, por exemplo, conta cerca de 0,3 token por caractere em inglês ([uso de tokens](https://api-docs.deepseek.com/quick_start/token_usage), em inglês). Cada resposta sua gera duas solicitações: a resposta do tutor e a correção da sua frase (nenhuma se as correções estiverem desativadas). O resumo da sessão é mais uma solicitação, e cada dica, tradução ou «Como se diz?» é mais uma.

Medido com o provedor de teste (`scripts/token_usage.py`, uma sessão de entrevista de emprego no nível B1, 10 respostas de 10 a 15 palavras, correções ativadas):

| Solicitação | Tokens de entrada | Tokens de saída, no máximo |
| --- | --- | --- |
| Resposta do tutor | 850 na primeira resposta, cerca de 50 a mais em cada uma (1300 na décima) | 400 |
| Correção da sua resposta | cerca de 1450 | 800 |
| Resumo da sessão | cerca de 1000 | 1200 |
| Sugestão | cerca de 300 | 600 |
| Uma sessão completa de 10 respostas com uma sugestão | cerca de 26 000 | quase sempre bem abaixo do máximo |

Custo de uma sessão ≈ (tokens de entrada × preço de entrada + tokens de saída × preço de saída), somado em todas as solicitações. Os preços mudam com frequência; confira a página de preços do seu provedor e a página de uso da sua conta depois das primeiras sessões.

## Quando algo dá errado

| O que o aplicativo diz | Causa comum | O que fazer |
| --- | --- | --- |
| O provedor recusou a chave ou a conta está sem saldo | Chave errada ou apagada, saldo zerado, limite de gasto atingido | Confira a chave e o saldo ou o limite no provedor |
| O provedor pede para esperar | Solicitações demais por minuto | Espere um minuto; o botão «Tentar de novo» repete a resposta |
| Não é possível falar com o provedor | Sem internet, firewall, URL base errada | Confira a conexão; para servidores locais, veja se o Ollama ou o LM Studio está aberto |
| O provedor devolveu um erro ou uma resposta incompleta | Nome do modelo errado, o modelo não aceita o formato pedido, falha do provedor | Confira o nome do modelo; tente outro modelo ou outro provedor |
