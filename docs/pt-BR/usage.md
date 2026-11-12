# Como usar o Voice Tutor

O Voice Tutor tem quatro seções na barra superior: Conversa, Leitura, Vocabulário e Histórico. As configurações ficam no ícone de controles à direita. A interface, as correções, as traduções e as dicas estão no seu idioma (espanhol ou português); o tutor sempre fala inglês americano geral.

## Primeira abertura

Na primeira vez, abre um assistente de configuração: idioma, verificação do computador, modelos, uma medição curta, microfone, voz, conexão de API e nível. Você pode abri-lo de novo quando quiser em Configurações → Desempenho → «Executar o assistente novamente». Veja `hardware.md` para a verificação do computador e `api-keys.md` para a conexão.

## Conversa

<a id="conversation"></a>

1. Escolha um cenário (uma entrevista de emprego, um papo informal, uma reunião…) e o seu nível, e clique em «Começar a conversa». O tutor fala primeiro.
2. Aperte a **barra de espaço** para começar a responder e de novo para enviar. **Esc** cancela a resposta. Enquanto o tutor fala, a barra de espaço o interrompe.
3. A sua resposta aparece como texto; o tutor responde em voz alta e por escrito.

Modos de turno (o seletor do painel inferior):

- **Manual**: a barra de espaço começa e termina cada resposta. É o melhor com caixas de som.
- **Automático**: é só falar; a sua resposta é enviada depois de uma pausa (Configurações → Conversa define a pausa). Com caixas de som, o microfone fecha enquanto o tutor fala; com fones de ouvido você pode interromper o tutor com a voz (Configurações → Conversa → «Estou de fones de ouvido»).

Embaixo de cada fala do tutor: **Repetir**, **Mais devagar** e **Traduzir**. No painel inferior: **Sugestão** (ideias para a sua resposta), **Como se diz?** (digite uma frase no seu idioma e receba em inglês) e **Encerrar**.

### Correções

Os erros da sua resposta ficam sublinhados. O cartão mostra a correção, uma explicação curta no seu idioma e um jeito mais natural de dizer. Escolha quando elas aparecem no painel inferior ou em Configurações → Correções: na hora, ao clicar, no fim da sessão ou desativadas. Erros claros de pronúncia também são marcados na conversa (no perfil `compacto` isso vem desativado; Configurações → Correções).

### Resumo

«Encerrar» mostra o resumo da sessão: o ponto principal, todas as correções, exercícios curtos de fala a partir dos seus erros («Diga em inglês: …»), os erros que se repetem em várias sessões, os sons para praticar e as frases úteis do tutor, que você pode adicionar ao vocabulário.

## Leitura

<a id="reading"></a>

A leitura avalia a sua pronúncia som por som, sem modelo de linguagem (funciona sem conexão de API).

1. Se quiser, ouça a frase («Referência», «Referência devagar»).
2. Aperte a **barra de espaço** ou o microfone, leia a frase em voz alta e aperte a **barra de espaço** de novo.
3. As palavras com algum problema ficam marcadas: «impreciso» ou «erro». Clique em uma palavra para ver qual som foi ouvido no lugar de qual, uma dica no seu idioma e botões para ouvir a palavra e repetir só essa palavra.
4. Se uma marca estiver errada, clique em «Isso estava certo»: a avaliação fica menos rigorosa com esse som.

«Sons para praticar» mostra os sons em que você teve dificuldade nos últimos 7 dias. Cada frase indica os sons que ela treina; «Anterior» e «Próxima frase» percorrem as 30 frases.

## Vocabulário

<a id="vocabulary"></a>

As frases que você adiciona a partir de um resumo voltam para revisão com intervalos cada vez maiores. Leia a frase em inglês, pense no significado, clique em «Mostrar tradução» e depois em «Lembro» ou «Não lembro».

## Histórico

<a id="history"></a>

Cada sessão com a transcrição, as correções e o resumo. Você pode abrir, exportar (JSON ou CSV) ou excluir uma sessão; ao excluir, as gravações dela também são apagadas.

## Configurações

<a id="settings"></a>

| Seção | O que tem |
| --- | --- |
| Conexões de API | Os seus provedores e chaves; uma fica ativa (`api-keys.md`) |
| Idioma | Espanhol ou português para a interface e as explicações, sem reiniciar |
| Áudio e voz | Microfone, caixas de som, a voz e a velocidade do tutor, supressão de ruído |
| Conversa | Nível, modo de turno, duração da pausa no modo automático, reformulações do tutor, fones de ouvido |
| Correções | Quando as correções aparecem; marcas de pronúncia na conversa |
| Desempenho | Perfil (`completo`, `compacto`, automático), última medição, executar o assistente novamente |
| Dados | Por quanto tempo as gravações ficam guardadas, exportar, «Excluir todos os dados», registro detalhado |

## Teclado

| Tecla | Conversa | Leitura |
| --- | --- | --- |
| Barra de espaço | Começar, enviar, interromper | Começar e parar a gravação |
| Esc | Cancelar a resposta | Cancelar a gravação |
