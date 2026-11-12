"""Language guard before speech synthesis (plan item 1.5, SPEC 5)."""

from __future__ import annotations

import pytest

from voicetutor.lang_guard import classify, is_learner_language

# English sentences a tutor might say, full of Spanish and Portuguese names and places.
ENGLISH = [
    "I visited San José and Puerto Vallarta last summer.",
    "Have you ever been to Rio de Janeiro or São Paulo?",
    "My friend Maria de la Cruz works at Banco do Brasil.",
    "José and Ana moved to Buenos Aires in 2019.",
    "We had dinner at La Casa de Toño on Friday.",
    "Los Angeles is a lot bigger than San Diego.",
    "The team in Bogotá ships a release every two weeks.",
    "Did you watch the game between Flamengo and Corinthians?",
    "Our designer, João Pedro, lives in Belo Horizonte.",
    "Mexico City and Guadalajara both have big tech scenes.",
    "Is Medellín a good place for remote work?",
    "I think Santiago de Chile is beautiful in the spring.",
    "She grew up in Porto Alegre and studied in Curitiba.",
    "The conference is in Montevideo this year.",
    "Have you tried pão de queijo? It's a cheese bread from Minas Gerais.",
    "Carlos Gómez is the new product manager on our team.",
    "Our client is a bank in Lima called Banco del Sol.",
    "We flew from Recife to Salvador and then to Fortaleza.",
    "Luis Fernando said the deploy went fine.",
    "The office near Avenida Paulista is really modern.",
    "Do you know the café on Calle Ocho in Miami?",
    "My manager, Ana Luísa, is from Florianópolis.",
    "That startup from Monterrey just raised a big round.",
    "We watched a documentary about Frida Kahlo and Diego Rivera.",
    "He moved from Quito to Austin for a new job.",
    "Is it true that Machu Picchu is hard to get to?",
    "Our standup is at nine, right after Pedro's call with Sofía.",
    "I loved the beaches in Cartagena and Santa Marta.",
    "The new hire, Mariana dos Santos, starts on Monday.",
    "Las Vegas is only a few hours from Los Angeles by car.",
    "We're meeting the team from Campinas next week.",
    "My favorite singer is Caetano Veloso.",
    "The project is named Nova, after a café in Brasília.",
    "Do you prefer tacos al pastor or empanadas?",
    "Thanks, that's very helpful.",
    "So, what does a normal day look like for you?",
    "Interesting. Could you walk me through that decision?",
    "Yes, I see what you mean.",
]

SPANISH = [
    "Hola, ¿cómo estás?",
    "Gracias por la explicación.",
    "La edad se dice con be en inglés.",
    "Para una duración que sigue hasta hoy se usa present perfect.",
    "No te escuché bien, ¿puedes repetirlo?",
    "Este error es muy común entre hispanohablantes.",
    "Trabajo en una empresa de software desde hace tres años.",
    "Usa for con una duración y since con el momento de inicio.",
    "Es una frase muy natural.",
    "¡Muy bien!",
]

PORTUGUESE = [
    "Obrigado pela ajuda.",
    "Para dizer que algo existe em um lugar, use there is.",
    "Você pode repetir, por favor?",
    "Eu trabalho com desenvolvimento há cinco anos.",
    "Não entendi a pergunta.",
    "Isso está muito bom.",
    "People é plural e vem sem the quando falamos em geral.",
    "Use o present perfect para algo que continua até hoje.",
    "Tudo bem com você?",
    "Muito obrigada!",
]


@pytest.mark.parametrize("text", ENGLISH)
def test_english_with_names_and_places_passes(text: str) -> None:
    verdict = classify(text)
    assert verdict.language is None, (text, verdict)


@pytest.mark.parametrize("text", SPANISH)
def test_spanish_is_caught(text: str) -> None:
    verdict = classify(text)
    assert verdict.language == "es-419", (text, verdict)


@pytest.mark.parametrize("text", PORTUGUESE)
def test_portuguese_is_caught(text: str) -> None:
    verdict = classify(text)
    assert verdict.language is not None, (text, verdict)


def test_portuguese_mostly_identified_as_portuguese() -> None:
    hits = sum(1 for t in PORTUGUESE if classify(t).language == "pt-BR")
    assert hits >= len(PORTUGUESE) - 1


def test_counts_cover_the_plan() -> None:
    assert len(ENGLISH) >= 30
    assert not is_learner_language("")
    assert not is_learner_language("OK.")
