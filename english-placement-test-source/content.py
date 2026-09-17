# -*- coding: utf-8 -*-
"""
Contenido íntegro de la Prueba de Nivel de Inglés — Nexo Académico.
Fuente única de verdad: el generador de HTML (build.py) construye tanto
el cuadernillo del examen como la clave de respuestas a partir de estos
mismos datos, por lo que ambos quedan siempre sincronizados.
"""

# ---------------------------------------------------------------------------
# PARTE 1 — GRAMÁTICA Y VOCABULARIO (Multiple choice, 60 ítems, orden B1→C2)
# Cada ítem: (nivel, pregunta, [opciones], índice_correcto)
# ---------------------------------------------------------------------------

PART1 = [
    # ---- Bloque B1 (1-15) ----
    ("B1", "I ___ this film before. Let's watch something else.",
     ["saw", "have seen", "was seeing", "see"], 1),
    ("B1", "She ___ TV when the phone rang.",
     ["watched", "watches", "was watching", "has watched"], 2),
    ("B1", "This exercise is ___ than the last one.",
     ["more difficult", "difficulter", "most difficult", "as difficult"], 0),
    ("B1", "If it ___ tomorrow, we'll cancel the picnic.",
     ["rains", "will rain", "rained", "is raining"], 0),
    ("B1", "You ___ smoke in here — it's forbidden.",
     ["don't have to", "mustn't", "shouldn't to", "don't must"], 1),
    ("B1", "Look at those clouds! It ___ rain.",
     ["will", "is going to", "is", "would"], 1),
    ("B1", "The woman ___ lives next door is a doctor.",
     ["which", "whose", "who", "whom"], 2),
    ("B1", "This cheese ___ in France.",
     ["makes", "is made", "is making", "made"], 1),
    ("B1", "There isn't ___ milk left in the fridge.",
     ["many", "much", "a few", "several"], 1),
    ("B1", "I enjoy ___ to music while I work.",
     ["listen", "to listen", "listening", "listened"], 2),
    ("B1", "Can you ___ my cat while I'm on holiday?",
     ["look after", "look for", "look at", "look up"], 0),
    ("B1", "I need to ___ my homework before dinner.",
     ["make", "do", "have", "take"], 1),
    ("B1", "He's very good ___ maths.",
     ["in", "at", "for", "with"], 1),
    ("B1", "The hotel room was extremely small. In other words, it was ___.",
     ["spacious", "tiny", "comfortable", "modern"], 1),
    ("B1", "I usually ___ breakfast at 7 am.",
     ["do", "make", "have", "take"], 2),

    # ---- Bloque B2 (16-30) ----
    ("B2", "If I ___ you were coming, I would have cooked more food.",
     ["knew", "had known", "would know", "know"], 1),
    ("B2", "She said that she ___ tired.",
     ["is", "was", "has been", "be"], 1),
    ("B2", "He asked me ___.",
     ["where did I live", "where I lived", "where I live", "where lived I"], 1),
    ("B2", "The report ___ by tomorrow morning.",
     ["must finish", "must be finished", "must be finishing", "must have finished"], 1),
    ("B2", "My brother, ___ has just moved to Canada, works as an engineer.",
     ["that", "who", "which", "whom"], 1),
    ("B2", "I ___ play the piano when I was a child, but I've forgotten how now.",
     ["use to", "was used to", "used to", "would used to"], 2),
    ("B2", "She isn't answering her phone. She ___ have already left.",
     ["must", "should", "can", "would"], 0),
    ("B2", "___ the heavy rain, the match continued.",
     ["Although", "Despite", "However", "Even though"], 1),
    ("B2", "I was really ___ by the ending of the film.",
     ["impress", "impressive", "impressed", "impression"], 2),
    ("B2", "Don't forget to ___ the lights when you leave.",
     ["turn off", "turn into", "turn up", "turn out"], 0),
    ("B2", "Can you give me some ___ on how to improve my CV?",
     ["advices", "advice", "suggestion", "suggest"], 1),
    ("B2", "It's important to ___ a good relationship with your colleagues.",
     ["do", "make", "maintain", "held"], 2),
    ("B2", "Many companies are trying to reduce their carbon ___.",
     ["footprint", "footstep", "fingerprint", "trace"], 0),
    ("B2", "I'm not a morning person — it takes me ages to ___.",
     ["wake up", "wake on", "get on", "wake off"], 0),
    ("B2", "He's very ambitious and always likes to ___ risks in business.",
     ["take", "do", "make", "have"], 0),

    # ---- Bloque C1 (31-45) ----
    ("C1", "___ had I arrived home than the phone started ringing.",
     ["No sooner", "Hardly", "Scarcely", "Barely"], 0),
    ("C1", "___ really annoys me is people who talk during films.",
     ["What", "That", "It", "This"], 0),
    ("C1", "I wish I ___ harder for the exam — I would have passed easily.",
     ["studied", "had studied", "would study", "study"], 1),
    ("C1", "The doctor recommended that he ___ more exercise.",
     ["does", "do", "did", "will do"], 1),
    ("C1", "We ___ our house painted last month.",
     ["had", "did", "made", "took"], 0),
    ("C1", "___ nothing more to say, she left the room.",
     ["Having", "Had", "Have", "To have"], 0),
    ("C1", "The man ___ over there is my uncle.",
     ["who standing", "stands", "standing", "stood"], 2),
    ("C1", "You ___ bought so much food — half of it will go to waste.",
     ["didn't need to", "needn't have", "mustn't have", "shouldn't"], 1),
    ("C1", "You can borrow my car ___ you bring it back before 6 pm.",
     ["provided that", "even though", "in case", "despite"], 0),
    ("C1", "A: I don't think it'll rain. B: I hope ___.",
     ["so", "that", "it", "yes"], 0),
    ("C1", "The government has come under ___ fire for its handling of the crisis.",
     ["heavy", "strong", "hard", "big"], 0),
    ("C1", "Her ___ to detail makes her an excellent editor.",
     ["attentive", "attention", "attentively", "attend"], 1),
    ("C1", "The peace talks suddenly ___ when the delegation walked out of the room.",
     ["broke down", "broke up", "broke out", "broke off"], 3),
    ("C1", "The CEO's speech was full of ___ remarks that many found condescending.",
     ["patronizing", "patronal", "patronized", "patron"], 0),
    ("C1", "After months of hard work, the project finally ___.",
     ["paid off", "paid up", "paid out", "paid back"], 0),

    # ---- Bloque C2 (46-60) ----
    ("C2", "___ was the flight delayed, but our luggage was also lost.",
     ["Not only", "Not never", "No only", "Not just"], 0),
    ("C2", "___ hard she tried, she couldn't open the jar.",
     ["How", "However", "As", "So"], 1),
    ("C2", "It is essential that the matter ___ investigated immediately.",
     ["is", "be", "was", "will be"], 1),
    ("C2", "___ the CEO to resign, the company's shares would probably fall.",
     ["If", "Were", "Should", "Was"], 1),
    ("C2", "They have introduced a new scheme ___ employees can buy shares in the company.",
     ["whereby", "wherein", "whereupon", "whereas"], 0),
    ("C2", "My grandmother has always been very ___ — she never wastes anything.",
     ["economic", "economical", "economics", "economy"], 1),
    ("C2", "I think you're barking up the wrong ___ if you think he's responsible for this.",
     ["tree", "path", "road", "branch"], 0),
    ("C2", "The negotiations were fraught ___ difficulty from the very beginning.",
     ["of", "by", "with", "in"], 2),
    ("C2", "There was a general feeling of ___ among staff after the announcement.",
     ["disgruntlement", "disgruntled", "disgruntle", "disgruntling"], 0),
    ("C2", "The committee decided to ___ the proposal for further review.",
     ["shelve", "shelf", "unshelve", "shell"], 0),
    ("C2", "She has a good eye for detail, which makes her ___ suited to quality control.",
     ["ideal", "ideally", "idea", "idealize"], 1),
    ("C2", "The minister was accused of trying to ___ public opinion through selective use of statistics.",
     ["manipulate", "fabricate", "generate", "stimulate"], 0),
    ("C2", "The two countries were on the ___ of war after the border incident.",
     ["verge", "edge", "border", "brink"], 3),
    ("C2", "The report's findings were largely ___ by subsequent research.",
     ["backed up", "corroborated", "proved", "shown"], 1),
    ("C2", "Let's not beat around the ___ — sales figures are simply not good enough.",
     ["tree", "bush", "field", "corner"], 1),
]

assert len(PART1) == 60

# ---------------------------------------------------------------------------
# PARTE 2 — OPEN CLOZE (2 textos, 8 huecos cada uno = 16 puntos)
# ---------------------------------------------------------------------------

PART2_TEXTS = [
    {
        "title": "Texto 1",
        "level": "B1–B2",
        "example": "to",
        "text": (
            "Last summer, my sister and I decided <b>(0 — to)</b> travel around "
            "Portugal for two weeks. We had never been <u>(1)</u>&nbsp;&nbsp;&nbsp; "
            "the country before, so we were really excited. On <u>(2)</u>&nbsp;&nbsp;&nbsp; "
            "first day, we visited Lisbon and walked <u>(3)</u>&nbsp;&nbsp;&nbsp; the old "
            "streets for hours. The weather was so hot <u>(4)</u>&nbsp;&nbsp;&nbsp; we had "
            "to stop every few minutes to drink water. <u>(5)</u>&nbsp;&nbsp;&nbsp; of the "
            "restaurants we tried were absolutely delicious, especially the fish dishes. "
            "By the end of the trip, we <u>(6)</u>&nbsp;&nbsp;&nbsp; visited five different "
            "cities. We only had ten days, so we <u>(7)</u>&nbsp;&nbsp;&nbsp; to skip the "
            "south of the country. We're already planning <u>(8)</u>&nbsp;&nbsp;&nbsp; go "
            "back next year."
        ),
        "gaps": [
            (1, ["to"]),
            (2, ["our", "the"]),
            (3, ["through", "around", "along"]),
            (4, ["that"]),
            (5, ["most", "many"]),
            (6, ["had"]),
            (7, ["had"]),
            (8, ["to"]),
        ],
    },
    {
        "title": "Texto 2",
        "level": "C1–C2",
        "example": "the",
        "text": (
            "Remote work has transformed <b>(0 — the)</b> way many of us live and work. "
            "<u>(1)</u>&nbsp;&nbsp;&nbsp; has this shift been more visible than in large "
            "cities, where office towers now stand half-empty. Some economists argue that, "
            "<u>(2)</u>&nbsp;&nbsp;&nbsp; the initial disruption, remote work has ultimately "
            "made the workforce more productive. Others, <u>(3)</u>&nbsp;&nbsp;&nbsp;, "
            "believe that it has eroded the sense of community that traditionally existed "
            "within companies. <u>(4)</u>&nbsp;&nbsp;&nbsp; matter which side of the debate "
            "you fall on, it is clear that the traditional nine-to-five office model is "
            "unlikely to return in <u>(5)</u>&nbsp;&nbsp;&nbsp; original form. Employees "
            "have grown accustomed to the flexibility remote work provides, and few would "
            "be willing to give it <u>(6)</u>&nbsp;&nbsp;&nbsp; without a fight. "
            "<u>(7)</u>&nbsp;&nbsp;&nbsp; this trend continues, cities may need to rethink "
            "<u>(8)</u>&nbsp;&nbsp;&nbsp; they use office space altogether."
        ),
        "gaps": [
            (1, ["nowhere"]),
            (2, ["despite"]),
            (3, ["however"]),
            (4, ["no"]),
            (5, ["its"]),
            (6, ["up"]),
            (7, ["if"]),
            (8, ["how"]),
        ],
    },
]

# ---------------------------------------------------------------------------
# PARTE 3 — WORD FORMATION (10 ítems, 1 punto cada uno)
# ---------------------------------------------------------------------------

PART3 = [
    ("Her presentation was extremely ___.", "IMPRESS", "impressive"),
    ("The company's new policy has led to widespread ___ among employees, "
     "many of whom have complained to HR.", "SATISFY", "dissatisfaction"),
    ("It's important to remain ___ during a job interview.", "CONFIDENCE", "confident"),
    ("The novel's ___ ending surprised every reader.", "EXPECT", "unexpected"),
    ("Scientists are still trying to find a ___ explanation for the phenomenon.",
     "SCIENCE", "scientific"),
    ("The company was praised for its ___ approach to recycling.", "INNOVATE", "innovative"),
    ("The manager's decision was met with strong ___ from the staff.", "OPPOSE", "opposition"),
    ("She gave a very ___ account of what had happened.", "DETAIL", "detailed"),
    ("The new regulations will ___ affect how small businesses operate.",
     "SIGNIFICANT", "significantly"),
    ("His argument was based on a fundamental ___ of the data, which invalidated his entire conclusion.",
     "UNDERSTAND", "misunderstanding"),
]

assert len(PART3) == 10

# ---------------------------------------------------------------------------
# PARTE 4 — KEY WORD TRANSFORMATION (8 ítems, 2 puntos cada uno = 16 puntos)
# ---------------------------------------------------------------------------

PART4 = [
    ("It's not necessary for you to finish the report today.", "HAVE",
     "You", "the report today.", "don't have to finish"),
    ("I last saw her three years ago.", "SEEN",
     "I", "three years.", "haven't seen her for"),
    ("Someone stole my bike while I was at work.", "STOLEN",
     "My bike", "I was at work.", "was stolen while"),
    ("She started learning English five years ago and still learns it now.", "FOR",
     "She", "five years.", "has been learning English for"),
    ("I'm sure he didn't know about the meeting.", "HAVE",
     "He", "about the meeting.", "can't have known"),
    ("It's possible that they missed the train.", "MIGHT",
     "They", "the train.", "might have missed"),
    ("Despite being very tired, she finished the marathon.", "THOUGH",
     "", ", she finished the marathon.", "Tired though she was"),
    ("I regret not studying harder at university.", "WISH",
     "I", "harder at university.", "wish I had studied"),
]

assert len(PART4) == 8

# ---------------------------------------------------------------------------
# PARTE 5 — VOCABULARY IN USE (15 ítems, 1 punto cada uno)
# ---------------------------------------------------------------------------

PART5_COLLOCATIONS = [
    ("You should always ___ care when crossing a busy road.",
     ["do", "take", "make", "have"], 1),
    ("It's easy to ___ mistakes when you're tired.",
     ["do", "make", "have", "take"], 1),
    ("He decided to ___ a stand against the new policy.",
     ["take", "make", "do", "have"], 0),
    ("Could you ___ me a favour and pick up some milk?",
     ["make", "do", "take", "give"], 1),
    ("The new evidence ___ doubt on his account of events.",
     ["makes", "puts", "casts", "gives"], 2),
]

PART5_PHRASAL_VERBS = [
    ("She had to put up with a lot of criticism early in her career. "
     "“Put up with” most nearly means:",
     ["avoid", "tolerate", "enjoy", "cause"], 1),
    ("The meeting was called off at the last minute. "
     "“Called off” most nearly means:",
     ["postponed", "cancelled", "started", "shortened"], 1),
    ("He came across an old photograph while cleaning the attic. "
     "“Came across” most nearly means:",
     ["destroyed", "looked for", "found by chance", "remembered"], 2),
    ("Prices have gone up considerably over the past year. "
     "“Gone up” most nearly means:",
     ["increased", "decreased", "stabilised", "disappeared"], 0),
    ("They finally managed to sort out the misunderstanding. "
     "“Sort out” most nearly means:",
     ["create", "resolve", "ignore", "discuss"], 1),
]

PART5_IDIOMS = [
    ("“It's raining cats and dogs outside.” This means:",
     ["It's raining very lightly", "It's raining very heavily",
      "It's about to rain", "Animals are falling from the sky"], 1),
    ("“I think we should let sleeping dogs lie.” This means:",
     ["We should wake everyone up",
      "We should not disturb a situation that could cause problems if brought up",
      "We should get more sleep", "We should be more honest"], 1),
    ("“She's clearly under the weather today.” This means:",
     ["She's outside in the rain", "She's feeling slightly ill",
      "She's in a bad mood", "She's very busy"], 1),
    ("“That decision really cost him an arm and a leg.” This means:",
     ["It caused him a physical injury", "It was very expensive",
      "It took a long time", "It made him famous"], 1),
    ("“Once in a blue moon, we go out for dinner.” This means:",
     ["Very often", "Every month", "Very rarely", "Only at night"], 2),
]

PART5 = PART5_COLLOCATIONS + PART5_PHRASAL_VERBS + PART5_IDIOMS
assert len(PART5) == 15

# ---------------------------------------------------------------------------
# PUNTUACIÓN Y NIVELES
# ---------------------------------------------------------------------------

SCORING = {
    "part1_points": 60,
    "part2_points": 16,
    "part3_points": 10,
    "part4_points": 16,   # 8 items x 2 points
    "part5_points": 15,
    "total_points": 117,
    "bands": [
        (0, 46, "Pre-B1", "A2 o inferior — se recomienda una prueba de nivel más básica."),
        (47, 64, "B1", "Usuario independiente — nivel intermedio."),
        (65, 83, "B2", "Usuario independiente — nivel intermedio alto."),
        (84, 101, "C1", "Usuario competente — nivel avanzado."),
        (102, 117, "C2", "Usuario competente — nivel de maestría."),
    ],
}

# ---------------------------------------------------------------------------
# SPEAKING TEST
# ---------------------------------------------------------------------------

SPEAKING_PART1_QUESTIONS = [
    ("Datos personales", [
        "Could you tell me a little about yourself and where you're from?",
        "What do you do — do you work or are you a student?",
    ]),
    ("Vida diaria y tiempo libre", [
        "What do you usually do in your free time?",
        "How do you usually spend your weekends?",
    ]),
    ("Gustos y experiencias", [
        "What's something you've really enjoyed doing recently?",
        "Do you prefer spending time alone or with other people? Why?",
    ]),
    ("Planes de futuro", [
        "Do you have any plans for the near future you'd like to share?",
    ]),
]

SPEAKING_PART2_CARDS = [
    ("B1", "A typical day",
     "Talk about a typical day in your life. You should say: what time you "
     "usually get up, what you do during the day, and say whether you think "
     "it's a good routine or not."),
    ("B2", "A change you have made",
     "Talk about a change you have made in your life. You should say: what "
     "the change was, why you made it, and explain how it has affected you."),
    ("C1", "Technology in daily life",
     "Talk about the role technology plays in your daily life. You should "
     "say: which technologies you rely on most, how your life would be "
     "different without them, and give your opinion on whether we depend on "
     "technology too much."),
    ("C2", "Society in the future",
     "Talk about how you think society will change over the next twenty "
     "years. You should say: what changes you expect, what is driving them, "
     "and evaluate whether these changes will be positive or negative "
     "overall."),
]

SPEAKING_PART3_SCENARIOS = [
    ("B1–B2", "Helping a friend settle in",
     "Imagine a friend is moving to your city and doesn't know anyone. Here "
     "are some ways to help them settle in. Talk together about the "
     "advantages of each idea, and decide which two would be most helpful.",
     ["Introduce them to your friends",
      "Show them around the neighbourhood",
      "Help them find a language exchange group",
      "Invite them to join a local club or sports team",
      "Help them find useful apps and websites for newcomers"]),
    ("C1–C2", "Funding a city project",
     "A local council has some money to spend on improving quality of life "
     "in the city. Here are some possible projects. Discuss the benefits "
     "and drawbacks of each, and decide together which one should receive "
     "the funding.",
     ["Building more green spaces and parks",
      "Improving public transport",
      "Investing in free digital skills courses for residents",
      "Supporting local small businesses",
      "Funding community mental health services"]),
]

SPEAKING_PART4_DISCUSSION = [
    ("Comunidad y amistad (enlaza con el escenario B1–B2)", [
        "How important do you think it is to have a strong sense of "
        "community where you live?",
        "Do you think it's more difficult to make friends as an adult than "
        "as a child? Why?",
        "How has technology changed the way people build friendships?",
    ]),
    ("Sociedad y gobierno (enlaza con el escenario C1–C2)", [
        "What responsibility do you think local governments have towards "
        "improving citizens' wellbeing?",
        "Do you think money is always the solution to social problems?",
        "How might cities need to change in the future to remain good "
        "places to live?",
    ]),
]

# Rúbrica analítica: 4 criterios x 4 bandas (1 = B1 ... 4 = C2)
SPEAKING_RUBRIC = [
    {
        "criterion": "Grammar & Vocabulary",
        "criterion_es": "Gramática y vocabulario",
        "bands": {
            "B1": "Uses basic grammatical structures with reasonable accuracy; "
                  "vocabulary is sufficient for familiar, everyday topics but "
                  "limited when discussing less familiar subjects; noticeable "
                  "errors occur but rarely block understanding.",
            "B2": "Uses a range of grammatical structures with good control; "
                  "errors are minor and don't affect communication; vocabulary "
                  "allows discussion of a wide range of familiar and some "
                  "unfamiliar topics with occasional circumlocution.",
            "C1": "Uses a wide range of grammatical structures flexibly and "
                  "accurately, including more complex forms; vocabulary is "
                  "broad and precise, including some idiomatic expressions "
                  "and collocations, used appropriately for context.",
            "C2": "Uses grammar with full flexibility and precision, including "
                  "subtle and less common structures; commands a very wide "
                  "vocabulary, including idiomatic and colloquial expressions, "
                  "used with sensitivity to register and nuance.",
        },
    },
    {
        "criterion": "Discourse Management",
        "criterion_es": "Gestión del discurso y fluidez",
        "bands": {
            "B1": "Produces simple, connected speech using basic linking words "
                  "(and, but, because); can maintain a short monologue but may "
                  "need prompting to develop ideas further; some repetition "
                  "and hesitation.",
            "B2": "Produces extended, coherent stretches of speech using a "
                  "variety of linking devices; can develop an argument or "
                  "narrative with some clarity, though organisation may "
                  "occasionally be uneven.",
            "C1": "Speaks fluently and coherently over extended turns, "
                  "organising ideas logically and using a wide range of "
                  "cohesive devices; can develop arguments, hypothesise and "
                  "evaluate with relatively little hesitation.",
            "C2": "Produces sophisticated, coherent and well-structured "
                  "extended speech with apparent ease, using cohesive devices "
                  "skilfully and appropriately across a wide range of "
                  "abstract and complex topics.",
        },
    },
    {
        "criterion": "Pronunciation",
        "criterion_es": "Pronunciación",
        "bands": {
            "B1": "Generally clear enough to be understood despite a "
                  "noticeable accent; occasional mispronunciations may "
                  "require the listener's effort.",
            "B2": "Clear pronunciation and generally natural intonation; the "
                  "accent may still be noticeable but rarely causes "
                  "misunderstanding.",
            "C1": "Natural intonation, rhythm and stress; easy to understand "
                  "throughout, with only occasional traces of a first-"
                  "language accent.",
            "C2": "Highly natural pronunciation, intonation and stress "
                  "patterns, comparable to a proficient speaker; "
                  "communication is never impeded.",
        },
    },
    {
        "criterion": "Interactive Communication",
        "criterion_es": "Comunicación interactiva",
        "bands": {
            "B1": "Initiates and responds appropriately in familiar, "
                  "predictable situations; sometimes needs support or "
                  "repetition to keep the conversation going.",
            "B2": "Initiates, maintains and closes conversations on a wide "
                  "range of topics; contributes to discussions and can "
                  "generally keep up with the pace of natural conversation.",
            "C1": "Interacts with ease, adapting language and register to the "
                  "situation; can negotiate, persuade and manage turn-taking "
                  "skilfully, including in more abstract or unfamiliar "
                  "discussions.",
            "C2": "Communicates with complete flexibility and spontaneity, "
                  "effortlessly handling humour, nuance, disagreement, and "
                  "abstract or specialised discussion; skilfully manages the "
                  "interaction to achieve communicative goals.",
        },
    },
]

SPEAKING_SCORING_BANDS = [
    (4, 6, "B1"),
    (7, 10, "B2"),
    (11, 13, "C1"),
    (14, 16, "C2"),
]
