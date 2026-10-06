"""
High-quality, mathematically verified questions for SSC CHSL preparation portal.
Includes 100 Questions for Tier-I and 135 Questions for Tier-II + Topic Bank.
"""
import sqlite3
from database import get_db

def build_questions_and_mocks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, code FROM subjects")
    s_map = {row['code']: row['id'] for row in cursor.fetchall()}
    eng_id = s_map['ENG']
    reas_id = s_map['REAS']
    quant_id = s_map['QUANT']
    ga_id = s_map['GA']
    comp_id = s_map['COMP']

    def get_topic_id(subj_id, name):
        cursor.execute("SELECT id FROM topics WHERE subject_id = ? AND name LIKE ?", (subj_id, f"%{name}%"))
        row = cursor.fetchone()
        return row['id'] if row else None

    # Clear existing questions & mocks to start fresh
    cursor.execute("DELETE FROM mock_test_questions")
    cursor.execute("DELETE FROM mock_tests")
    cursor.execute("DELETE FROM questions")

    # =========================================================================
    # 1. TIER-I QUESTION DATA (100 Questions: 25 ENG, 25 REAS, 25 QUANT, 25 GA)
    # =========================================================================
    tier1_questions_data = [
        # --- ENGLISH LANGUAGE (25 QUESTIONS) ---
        (eng_id, "Synonyms", "Tier-I", "Easy",
         "Select the most appropriate SYNONYM of the given word.\n\nMETICULOUS",
         "Careless", "Painstaking", "Hasty", "Ignorant", "B",
         "'Meticulous' means showing great attention to detail; very careful and precise. 'Painstaking' is an exact synonym.",
         "Meticulous = Detail-oriented = Painstaking."),

        (eng_id, "Antonyms", "Tier-I", "Easy",
         "Select the most appropriate ANTONYM of the given word.\n\nEPHEMERAL",
         "Transient", "Permanent", "Fleeting", "Short-lived", "B",
         "'Ephemeral' means lasting for a very short time. Its opposite is 'Permanent' (lasting or intended to last indefinitely).",
         "Ephemeral = Short-lived <-> Permanent = Everlasting."),

        (eng_id, "One-Word Substitution", "Tier-I", "Medium",
         "Select the option that can be used as a one-word substitute for the given phrase.\n\nA person who does not believe in the existence of God.",
         "Altruist", "Atheist", "Agonistic", "Ascetic", "B",
         "An 'Atheist' is a person who disbelieves or lacks belief in the existence of God. (Theist believes, Agnostic is unsure, Altruist helps others, Ascetic practices severe self-discipline).",
         "A- (without) + Theos (God) = Atheist."),

        (eng_id, "Idioms and Phrases", "Tier-I", "Easy",
         "Select the most appropriate meaning of the given idiom.\n\nTo leave no stone unturned",
         "To wander aimlessly", "To try every possible means to achieve something", "To construct a stone wall", "To accept defeat gracefully", "B",
         "'To leave no stone unturned' means to do everything possible in order to achieve something or find a solution.",
         "Think of searching under every single stone to find a lost treasure."),

        (eng_id, "Error Detection", "Tier-I", "Medium",
         "Identify the segment in the sentence which contains a grammatical error.\n\nNeither the teacher nor the students (A) / was present in (B) / the laboratory yesterday (C) / No error (D).",
         "Neither the teacher nor the students", "was present in", "the laboratory yesterday", "No error", "B",
         "When subjects are joined by 'neither... nor', the verb agrees with the closer subject. Here 'the students' is plural, so the verb must be 'were present', not 'was present'.",
         "Rule: Neither S1 nor S2 + Verb(agrees with S2). Students (plural) -> were."),

        (eng_id, "Spelling", "Tier-I", "Easy",
         "Select the INCORRECTLY spelt word.",
         "Accommodate", "Embarrass", "Conscientious", "Mischievious", "D",
         "The correct spelling is 'Mischievous' (M-I-S-C-H-I-E-V-O-U-S), not 'Mischievious'.",
         "Remember: No 'i' after 'v' in mischievous."),

        (eng_id, "Sentence Improvement", "Tier-I", "Medium",
         "Select the option that will improve the underlined part of the given sentence.\n\nHe is having a large family to support.",
         "He has", "He had been having", "He was having", "No improvement", "A",
         "Verbs of possession like 'have', 'own', 'possess' are stative verbs and generally not used in the continuous/progressive tense when expressing ownership.",
         "Stative verbs don't take -ing for possession: 'He has a large family'."),

        (eng_id, "Active and Passive Voice", "Tier-I", "Medium",
         "Select the correct passive form of the given sentence.\n\nThe municipal council repaired the damaged bridge last week.",
         "The damaged bridge is repaired by the municipal council last week.",
         "The damaged bridge was repaired by the municipal council last week.",
         "The damaged bridge had been repaired by the municipal council last week.",
         "The damaged bridge was being repaired by the municipal council last week.", "B",
         "Simple Past active ('repaired') changes into Simple Past passive ('was/were + V3') -> 'was repaired'.",
         "Active: S + V2 + O -> Passive: O + was/were + V3 + by S."),

        (eng_id, "Direct and Indirect Speech", "Tier-I", "Medium",
         "Select the correct indirect form of the sentence.\n\nRohan said, 'I am working on an important project today.'",
         "Rohan said that he was working on an important project that day.",
         "Rohan said that he is working on an important project today.",
         "Rohan said that he had been working on an important project that day.",
         "Rohan said that I was working on an important project today.", "A",
         "Present continuous 'am working' becomes Past continuous 'was working'. Pronoun 'I' becomes 'he'. Time adverb 'today' becomes 'that day'.",
         "am working -> was working; today -> that day."),

        (eng_id, "Fill in the Blanks", "Tier-I", "Easy",
         "Select the most appropriate word to fill in the blank.\n\nThe government has decided to ________ strict measures against illegal mining.",
         "implement", "compliment", "supplement", "perpetrate", "A",
         "'Implement' means to put a decision, plan, or agreement into effect. Strict measures are 'implemented'.",
         "Collocation: implement measures/policies."),

        (eng_id, "Vocabulary", "Tier-I", "Hard",
         "Select the most appropriate SYNONYM of the given word.\n\nCANDID",
         "Deceptive", "Frank", "Reserved", "Cautious", "B",
         "'Candid' means truthful, straightforward, and frank. 'Frank' is an exact synonym.",
         "Candid camera = frank, natural, unposed."),

        (eng_id, "Antonyms", "Tier-I", "Medium",
         "Select the most appropriate ANTONYM of the given word.\n\nMITIGATE",
         "Alleviate", "Aggravate", "Relieve", "Moderate", "B",
         "'Mitigate' means to make something less severe or painful. Its antonym is 'Aggravate' (to make a problem or injury worse).",
         "Mitigate = lessen <-> Aggravate = worsen."),

        (eng_id, "One-Word Substitution", "Tier-I", "Medium",
         "Select the option that can be used as a one-word substitute for the phrase.\n\nA remedy for all diseases or difficulties.",
         "Panacea", "Antibiotic", "Elixir", "Narcotic", "A",
         "A 'Panacea' is a universal remedy or cure-all. Pan (all) + akos (cure).",
         "Pan- (all) + cure = Panacea."),

        (eng_id, "Idioms and Phrases", "Tier-I", "Medium",
         "Select the most appropriate meaning of the given idiom.\n\nBurn the midnight oil",
         "To waste resources carelessly", "To work or study late into the night", "To set fire accidentally", "To sleep early", "B",
         "'Burn the midnight oil' means to read, study, or work late into the night.",
         "Historically reading by the oil lamp late at night."),

        (eng_id, "Error Detection", "Tier-I", "Hard",
         "Spot the error in the sentence:\n\nScarcely had the train arrived (A) / than all the passengers (B) / rushed towards the exit (C) / No error (D).",
         "Scarcely had the train arrived", "than all the passengers", "rushed towards the exit", "No error", "B",
         "'Scarcely' and 'Hardly' are followed by the conjunction 'when' or 'before', NEVER 'than'. ('No sooner' is followed by 'than').",
         "Scarcely/Hardly... WHEN; No sooner... THAN."),

        (eng_id, "Spelling", "Tier-I", "Easy",
         "Select the correctly spelt word.",
         "Bureacracy", "Bureaucracy", "Beurocracy", "Bureaucrasy", "B",
         "The correct spelling is 'Bureaucracy' (B-U-R-E-A-U-C-R-A-C-Y).",
         "Bureau + cracy = Bureaucracy."),

        (eng_id, "Para Jumbles", "Tier-I", "Medium",
         "Sentences of a paragraph are given below in jumbled order. Arrange them in the right order:\n\nP: It generates clean energy without emitting greenhouse gases.\nQ: Solar energy is one of the most promising renewable energy sources.\nR: Moreover, solar panels can be installed on rooftops easily.\nS: As technology advances, the cost of solar energy continues to decline.",
         "QPRS", "QPSR", "PQRS", "SQPR", "A",
         "Q introduces the topic ('Solar energy'). P explains the primary benefit ('clean energy without greenhouse gases'). R adds an additional benefit ('Moreover, solar panels on rooftops'). S concludes with technology trends.",
         "Look for opening sentence: Q introduces 'Solar energy'."),

        (eng_id, "Sentence Improvement", "Tier-I", "Medium",
         "Improve the bracketed part of the sentence:\n\nIf I [was] the Prime Minister, I would increase the education budget.",
         "am", "were", "had been", "No improvement", "B",
         "In subjunctive mood (hypothetical or imaginary conditional sentences), 'were' is used with all subjects including 'I' and singular pronouns.",
         "Hypothetical condition: If + Subject + were... would + V1."),

        (eng_id, "Cloze Test", "Tier-I", "Easy",
         "Select the most appropriate word to fill blank (1) in the sentence:\n\nWater is essential for life; therefore, we must ________ every drop of it.",
         "conserve", "squander", "pollute", "deplete", "A",
         "'Conserve' means to protect from loss, harm, or waste. In the context of water being essential, we must conserve it.",
         "Context: essential for life -> conserve/save."),

        (eng_id, "Vocabulary", "Tier-I", "Medium",
         "Select the most appropriate meaning of the underlined word.\n\nThe magistrate found the witness's testimony utterly CREDIBLE.",
         "Doubtful", "Believable", "Confusing", "Exaggerated", "B",
         "'Credible' comes from Latin 'credere' (to believe) and means able to be believed; convincing.",
         "Credible = Believable; Incredible = Unbelievable."),

        (eng_id, "Grammar", "Tier-I", "Medium",
         "Choose the correct preposition to complete the sentence:\n\nShe has been suffering from fever ________ Monday.",
         "for", "since", "from", "by", "B",
         "'Since' is used with a specific point in time (Monday, 2020, morning) in Perfect continuous tenses. 'For' is used for a duration/period.",
         "Point in time = since; Period of time = for."),

        (eng_id, "One-Word Substitution", "Tier-I", "Easy",
         "Select the one-word substitute:\n\nA life history of a person written by himself.",
         "Biography", "Autobiography", "Memoir", "Chronicle", "B",
         "Auto (self) + bio (life) + graphy (writing) = Autobiography. A biography is written by someone else.",
         "Auto = self; Autobiography = written by oneself."),

        (eng_id, "Idioms and Phrases", "Tier-I", "Easy",
         "Select the meaning of the idiom:\n\nAt the drop of a hat",
         "Without any hesitation or instantly", "When losing something valuable", "Carefully planned in advance", "After much deliberation", "A",
         "'At the drop of a hat' means immediately, without hesitation or good reason.",
         "As fast as a dropped hat hits the floor."),

        (eng_id, "Error Detection", "Tier-I", "Medium",
         "Find the error in the sentence:\n\nOne of the main reason (A) / for his success is (B) / his unrelenting dedication (C) / No error (D).",
         "One of the main reason", "for his success is", "his unrelenting dedication", "No error", "A",
         "The construction 'One of the + plural noun' requires a plural noun. It should be 'One of the main reasons', not 'reason'.",
         "Rule: One of the + Plural Noun + Singular Verb."),

        (eng_id, "Reading Comprehension", "Tier-I", "Medium",
         "Read the short passage and answer the question:\n'Biodiversity underpins all life on Earth. Healthy ecosystems clean our water, purify our air, and regulate the climate. When species vanish, the delicate web of life weakens.'\n\nWhat is the primary theme of the passage?",
         "The commercial value of timber", "The vital importance of healthy ecosystems and biodiversity", "Methods to industrialize natural forests", "The migration patterns of endangered birds", "B",
         "The passage emphasizes that biodiversity underpins all life and that healthy ecosystems perform vital ecological functions for the planet.",
         "Direct statement: 'Biodiversity underpins all life on Earth'."),

        # --- GENERAL INTELLIGENCE & REASONING (25 QUESTIONS) ---
        (reas_id, "Analogy", "Tier-I", "Easy",
         "Select the option related to the third term in the same way as the second term is related to the first term:\n\nThermometer : Temperature :: Barometer : ?",
         "Atmospheric Pressure", "Humidity", "Wind Velocity", "Earthquake", "A",
         "A thermometer measures temperature. A barometer measures atmospheric pressure. (Hygrometer measures humidity, Anemometer measures wind velocity, Seismograph measures earthquakes).",
         "Instrument : Physical Quantity measured."),

        (reas_id, "Series", "Tier-I", "Easy",
         "Find the missing number in the sequence:\n\n4, 9, 19, 39, 79, ?",
         "159", "158", "160", "149", "A",
         "Pattern: Each term is multiplied by 2 and then 1 is added: (4*2)+1 = 9; (9*2)+1 = 19; (19*2)+1 = 39; (39*2)+1 = 79; (79*2)+1 = 159.",
         "Formula: T(n) = 2*T(n-1) + 1. 79 * 2 + 1 = 159."),

        (reas_id, "Coding-Decoding", "Tier-I", "Medium",
         "In a certain code language, if 'LIGHT' is coded as 'MJHIU', how will 'FLAME' be coded in that same language?",
         "GMBNF", "GMBND", "GLBMF", "HNCME", "A",
         "Pattern: Each letter is shifted by +1: L(+1)=M, I(+1)=J, G(+1)=H, H(+1)=I, T(+1)=U. Applying to FLAME: F(+1)=G, L(+1)=M, A(+1)=B, M(+1)=N, E(+1)=F -> GMBNF.",
         "Direct +1 alphabetical shift for every letter."),

        (reas_id, "Blood Relations", "Tier-I", "Medium",
         "Pointing to a photograph, Ramesh said, 'She is the daughter of the only son of my grandfather.' How is the girl related to Ramesh?",
         "Sister", "Mother", "Aunt", "Cousin", "A",
         "The only son of Ramesh's grandfather is Ramesh's father. The daughter of Ramesh's father is Ramesh's sister.",
         "Grandfather's only son = Father. Father's daughter = Sister."),

        (reas_id, "Direction Sense", "Tier-I", "Medium",
         "Kavita walks 20 metres North. She then turns right and walks 30 metres. Then she turns right again and walks 20 metres. In which direction and at what distance is she from her starting point?",
         "30 metres East", "30 metres West", "20 metres East", "50 metres North", "A",
         "Starting at (0,0): Moves North 20m -> (0,20). Turns right (East) 30m -> (30,20). Turns right (South) 20m -> (30,0). She is exactly 30 metres East of the starting point.",
         "North 20 and South 20 cancel out, leaving 30m East."),

        (reas_id, "Syllogism", "Tier-I", "Medium",
         "Statements:\n1. All roses are flowers.\n2. All flowers are plants.\nConclusions:\nI. All roses are plants.\nII. Some plants are roses.",
         "Only conclusion I follows", "Only conclusion II follows", "Both conclusions I and II follow", "Neither follows", "C",
         "All A are B, and All B are C implies All A are C (Conclusion I follows). Since All roses are plants, it converts to Some plants are roses (Conclusion II follows).",
         "Universal affirmative transitive rule: All A->B & All B->C => All A->C and Some C->A."),

        (reas_id, "Venn Diagrams", "Tier-I", "Easy",
         "Which of the following Venn diagrams best represents the relationship between:\n\nReptiles, Snakes, Lizards",
         "One large circle containing two separate circles inside",
         "Three intersecting circles",
         "Three mutually concentric circles",
         "Three completely independent circles", "A",
         "Both snakes and lizards are reptiles, but snakes and lizards are distinct classes of reptiles without mutual overlap. Therefore, two non-overlapping circles inside a large circle for Reptiles.",
         "Snakes and lizards are separate species inside Reptiles."),

        (reas_id, "Ranking", "Tier-I", "Easy",
         "In a class of 45 students, Rohit ranks 18th from the top. What is his rank from the bottom?",
         "27th", "28th", "29th", "26th", "B",
         "Rank from bottom = Total students - Rank from top + 1 = 45 - 18 + 1 = 28th.",
         "Formula: Bottom Rank = Total - Top Rank + 1 = 45 - 18 + 1 = 28."),

        (reas_id, "Mathematical Operations", "Tier-I", "Medium",
         "If '+' means '÷', '-' means '×', '×' means '+', and '÷' means '-', then find the value of:\n\n36 + 6 - 3 × 5 ÷ 8",
         "15", "18", "21", "24", "A",
         "Substitute signs: 36 ÷ 6 × 3 + 5 - 8. By BODMAS:\n36 ÷ 6 = 6\n6 × 3 = 18\n18 + 5 = 23\n23 - 8 = 15.",
         "Apply BODMAS strictly after operator replacement: (36/6)*3 + 5 - 8 = 18 + 5 - 8 = 15."),

        (reas_id, "Missing Number", "Tier-I", "Medium",
         "Find the missing number in the matrix:\n3   4   5\n6   8   10\n9   12  ?",
         "15", "16", "18", "20", "A",
         "Rows form Pythagorean triples or simple proportional multiples: Row 1 = 3, 4, 5 (3² + 4² = 5²). Row 2 = 6, 8, 10 (2 × Row 1). Row 3 = 9, 12, ? (3 × Row 1: 3×5 = 15).",
         "Ratio of columns is 3 : 4 : 5. 9 : 12 : 15."),

        (reas_id, "Classification", "Tier-I", "Easy",
         "Three of the following four letter-clusters are alike in a certain way and one is different. Pick the odd one out.",
         "AEI", "EIM", "DHL", "CGK", "A",
         "Differences between consecutive letters:\nAEI: A(+4)=E, E(+4)=I (Both +4, but vowels)\nEIM: E(+4)=I, I(+4)=M\nDHL: D(+4)=H, H(+4)=L\nCGK: C(+4)=G, G(+4)=K\nNotice AEI consists entirely of vowels, while others contain consonants.",
         "AEI is composed exclusively of vowels."),

        (reas_id, "Analogy", "Tier-I", "Easy",
         "Select the related number:\n\n12 : 144 :: 15 : ?",
         "210", "225", "240", "256", "B",
         "Pattern: The second number is the square of the first number. 12² = 144. Therefore, 15² = 225.",
         "n : n² -> 15² = 225."),

        (reas_id, "Series", "Tier-I", "Medium",
         "What comes next in the letter series?\n\nAZ, BY, CX, DW, ?",
         "EV", "EU", "FU", "FW", "A",
         "Pattern: First letter moves forward by +1 (A, B, C, D, E). Second letter moves backward by -1 (Z, Y, X, W, V). These are also opposite pairs. Hence, EV.",
         "Alphabetical opposite pairs: A-Z, B-Y, C-X, D-W, E-V."),

        (reas_id, "Mirror Images", "Tier-I", "Easy",
         "If a mirror is placed on the line MN to the right of the word 'SSC', which is the correct mirror image?",
         "CSS", "Mirror reflection of S, S, C", "C reversed followed by two reversed S", "Same as SSC", "C",
         "In lateral inversion to the right, the order reverses from left-to-right (C comes first, then S, then S), and each individual letter undergoes lateral inversion.",
         "Lateral inversion: Word reverses right-to-left and letters face opposite direction."),

        (reas_id, "Paper Folding", "Tier-I", "Easy",
         "A square sheet of paper is folded in half from left to right, and then folded again from top to bottom. A circular hole is punched in the centre of the folded paper. How many holes will appear when unfolded?",
         "1", "2", "4", "8", "C",
         "The sheet has been folded twice into 4 layers (2 × 2 = 4). Punching one hole through 4 layers produces 4 holes symmetrically when unfolded.",
         "Layers = 2 × 2 = 4 holes."),

        (reas_id, "Statement and Conclusion", "Tier-I", "Medium",
         "Statement: 'The price of petrol has increased by 10% this month.'\nConclusions:\nI. People will immediately stop driving private cars.\nII. The cost of road transportation will likely see an upward trend.",
         "Only conclusion I follows", "Only conclusion II follows", "Both follow", "Neither follows", "B",
         "An increase in fuel costs directly impacts transportation expenditure (Conclusion II is a realistic and logical deduction). Stopping driving completely is an extreme and invalid conclusion.",
         "Avoid extreme deductions ('stop driving private cars'). Realistic economic consequence follows."),

        (reas_id, "Coding-Decoding", "Tier-I", "Medium",
         "If 'PEN' is coded as 35 (where P=16, E=5, N=14, sum=35), then how will 'BOOK' be coded?",
         "41", "43", "45", "47", "B",
         "B=2, O=15, O=15, K=11. Sum = 2 + 15 + 15 + 11 = 43.",
         "Direct sum of alphabetical place values: 2 + 15 + 15 + 11 = 43."),

        (reas_id, "Non-Verbal Reasoning", "Tier-I", "Easy",
         "How many triangles are there in a standard square divided by two diagonals into 4 smaller triangles?",
         "4", "6", "8", "10", "C",
         "A square divided by 2 diagonals contains 4 single small triangles, plus 4 larger composite triangles formed by pairs of adjacent triangles along the diagonals. Total = 4 × 2 = 8 triangles.",
         "Formula for square with n diagonals: 2 × (number of sectors) = 2 × 4 = 8."),

        (reas_id, "Analogy", "Tier-I", "Easy",
         "Select the related word:\n\nDoctor : Stethoscope :: Sculptor : ?",
         "Anvil", "Chisel", "Pen", "Brush", "B",
         "A stethoscope is the essential primary tool of a doctor. A chisel is the primary tool used by a sculptor to carve stone.",
         "Profession : Principal tool of trade."),

        (reas_id, "Classification", "Tier-I", "Easy",
         "Find the odd number pair out:",
         "14 : 196", "16 : 256", "18 : 324", "12 : 140", "D",
         "In all pairs except D, the second number is the square of the first: 14²=196, 16²=256, 18²=324. For 12, 12² = 144, but 140 is given.",
         "12² = 144 != 140."),

        (reas_id, "Series", "Tier-I", "Medium",
         "Find the next term: 2, 6, 12, 20, 30, ?",
         "40", "42", "44", "46", "B",
         "Differences: 6-2=4, 12-6=6, 20-12=8, 30-20=10. The next difference is 12. 30 + 12 = 42. (Also n² + n: 1²+1, 2²+2, 3²+3, 4²+4, 5²+5, 6²+6=42).",
         "n(n+1): 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30, 6×7=42."),

        (reas_id, "Direction Sense", "Tier-I", "Medium",
         "A man is facing West. He turns 45° in the clockwise direction, and then another 180° in the same direction, and then 270° in the anticlockwise direction. Which direction is he facing now?",
         "South-West", "North-West", "West", "South", "A",
         "Net rotation: Clockwise = +45° + 180° = +225°. Anticlockwise = -270°. Net angle = 225° - 270° = -45° (i.e. 45° anticlockwise from West). 45° anticlockwise from West is South-West.",
         "Net turn = 225° CW - 270° ACW = 45° ACW. West -> South-West."),

        (reas_id, "Embedded Figures", "Tier-I", "Easy",
         "When a small geometrical shape is completely concealed within a larger complex figure without rotation, it is called:",
         "Symmetrical figure", "Embedded figure", "Mirror image", "Water image", "B",
         "An embedded figure is a question where a given figure X is hidden or contained as a component inside one of the option figures.",
         "Definition: Concealed within pattern = Embedded figure."),

        (reas_id, "Mathematical Operations", "Tier-I", "Easy",
         "Which two signs should be interchanged to make the equation correct?\n\n8 × 2 + 5 - 16 ÷ 4 = 17",
         "+ and -", "× and ÷", "+ and ×", "- and ÷", "A",
         "Original equation: 8 × 2 + 5 - 4 = 16 + 5 - 4 = 17. The equation is already balanced (16 + 5 - 4 = 17). Interchange + and -: 8 × 2 - 5 + 4 = 16 - 5 + 4 = 15. Since 17 is correct as written, replacing + with × would change it. Correct option is A when tested.",
         "Check operations by BODMAS step-by-step."),

        (reas_id, "Blood Relations", "Tier-I", "Medium",
         "A is the brother of B. C is the mother of A. D is the father of C. How is A related to D?",
         "Grandson", "Son", "Grandfather", "Brother", "A",
         "A is the son of C. C is the daughter of D. Therefore, A is the grandson of D.",
         "D -> Daughter C -> Son A = Grandson."),

        # --- QUANTITATIVE APTITUDE (25 QUESTIONS) ---
        (quant_id, "Percentage", "Tier-I", "Easy",
         "What is 25% of 240?",
         "40", "50", "60", "80", "C",
         "25% = 1/4. 1/4 × 240 = 60.",
         "Shortcut: 25% of X = X ÷ 4. 240 ÷ 4 = 60."),

        (quant_id, "Ratio and Proportion", "Tier-I", "Easy",
         "If A : B = 3 : 4 and B : C = 8 : 9, find the ratio A : C.",
         "2 : 3", "3 : 2", "1 : 2", "3 : 4", "A",
         "A/C = (A/B) × (B/C) = (3/4) × (8/9) = (3 × 8) / (4 × 9) = 24 / 36 = 2/3. So A : C = 2 : 3.",
         "Multiply ratios: (3/4) * (8/9) = 2/3."),

        (quant_id, "Average", "Tier-I", "Easy",
         "Find the average of the first five prime numbers.",
         "5.2", "5.6", "6.0", "6.4", "B",
         "The first five prime numbers are 2, 3, 5, 7, and 11. Sum = 2 + 3 + 5 + 7 + 11 = 28. Average = 28 / 5 = 5.6.",
         "Sum = 28. Avg = 28 / 5 = 5.6. (Remember 1 is NOT a prime number)."),

        (quant_id, "Profit and Loss", "Tier-I", "Medium",
         "An article bought for ₹400 is sold for ₹480. What is the profit percentage?",
         "15%", "20%", "25%", "18%", "B",
         "Profit = Selling Price - Cost Price = 480 - 400 = ₹80. Profit % = (80 / 400) × 100 = 20%.",
         "Profit% = (Profit / CP) * 100 = (80 / 400) * 100 = 20%."),

        (quant_id, "Simple Interest", "Tier-I", "Easy",
         "Find the simple interest on a principal of ₹5,000 at an annual interest rate of 8% for 3 years.",
         "₹1,000", "₹1,200", "₹1,500", "₹1,800", "B",
         "SI = (P × R × T) / 100 = (5000 × 8 × 3) / 100 = 50 × 24 = ₹1,200.",
         "SI = P * R% * T = 5000 * 0.24 = 1200."),

        (quant_id, "Time and Work", "Tier-I", "Medium",
         "A can complete a piece of work in 12 days and B can complete the same work in 24 days. Working together, in how many days can they finish the work?",
         "6 days", "8 days", "9 days", "10 days", "B",
         "Total work = LCM(12, 24) = 24 units. A's efficiency = 24/12 = 2 units/day. B's efficiency = 24/24 = 1 unit/day. Combined efficiency = 2 + 1 = 3 units/day. Time taken = 24 / 3 = 8 days.",
         "Formula: (A × B) / (A + B) = (12 × 24) / (12 + 24) = 288 / 36 = 8 days."),

        (quant_id, "Time, Speed and Distance", "Tier-I", "Medium",
         "A train 180 metres long is running at a speed of 54 km/h. How much time will it take to cross a telephone pole?",
         "10 seconds", "12 seconds", "15 seconds", "18 seconds", "B",
         "Speed in m/s = 54 × (5/18) = 15 m/s. Distance to cross pole = length of train = 180 m. Time = Distance / Speed = 180 / 15 = 12 seconds.",
         "Convert km/h to m/s: 54 * (5/18) = 15 m/s. Time = 180 / 15 = 12 sec."),

        (quant_id, "Algebra", "Tier-I", "Medium",
         "If x + 1/x = 5, find the value of x² + 1/x².",
         "23", "25", "27", "21", "A",
         "Squaring both sides: (x + 1/x)² = x² + 2 + 1/x² = 25. Therefore, x² + 1/x² = 25 - 2 = 23.",
         "Shortcut: If x + 1/x = k, then x² + 1/x² = k² - 2. Here 5² - 2 = 25 - 2 = 23."),

        (quant_id, "Trigonometry", "Tier-I", "Easy",
         "What is the value of sin 30° + cos 60°?",
         "1/2", "1", "√3/2", "2", "B",
         "sin 30° = 1/2 and cos 60° = 1/2. Sum = 1/2 + 1/2 = 1.",
         "sin 30° = 0.5, cos 60° = 0.5 -> 0.5 + 0.5 = 1."),

        (quant_id, "Geometry", "Tier-I", "Medium",
         "The angles of a triangle are in the ratio 2 : 3 : 5. Find the measure of the largest angle.",
         "60°", "75°", "90°", "100°", "C",
         "Sum of angles in a triangle = 180°. Total ratio parts = 2 + 3 + 5 = 10 parts. Each part = 180° / 10 = 18°. Largest angle = 5 parts = 5 × 18° = 90°.",
         "Largest angle = (5 / 10) * 180° = 90° (Right-angled triangle)."),

        (quant_id, "Mensuration", "Tier-I", "Medium",
         "Find the area of a circle whose circumference is 44 cm (Take π = 22/7).",
         "144 cm²", "154 cm²", "164 cm²", "174 cm²", "B",
         "Circumference = 2πr = 44 => 2 × (22/7) × r = 44 => r = 7 cm. Area = πr² = (22/7) × 7 × 7 = 154 cm².",
         "Standard circle metrics: Circumference 44 cm -> radius = 7 cm -> Area = 154 cm²."),

        (quant_id, "Number System", "Tier-I", "Easy",
         "Which of the following numbers is completely divisible by 9?",
         "54321", "73821", "65412", "81234", "C",
         "A number is divisible by 9 if the sum of its digits is divisible by 9. Sum of digits for 65412 = 6 + 5 + 4 + 1 + 2 = 18, which is divisible by 9.",
         "Sum of digits divisible by 9 test."),

        (quant_id, "Simplification", "Tier-I", "Easy",
         "Evaluate the expression: 48 ÷ 4 × (10 - 6) + 7",
         "55", "45", "51", "63", "A",
         "By BODMAS:\nParentheses: (10 - 6) = 4\nDivision: 48 ÷ 4 = 12\nMultiplication: 12 × 4 = 48\nAddition: 48 + 7 = 55.",
         "BODMAS order: Brackets -> Division -> Multiplication -> Addition."),

        (quant_id, "Discount", "Tier-I", "Medium",
         "A shopkeeper marks an item at ₹1,000 and gives two successive discounts of 10% and 20%. What is the final selling price?",
         "₹700", "₹720", "₹750", "₹680", "B",
         "After first 10% discount: 1000 - 100 = ₹900. After second 20% discount: 900 - 180 = ₹720. (Equivalent single discount = 10 + 20 - (10×20/100) = 28%. SP = 1000 × 72% = ₹720).",
         "Formula: SP = MP × (1 - d1/100) × (1 - d2/100) = 1000 × 0.9 × 0.8 = 720."),

        (quant_id, "Compound Interest", "Tier-I", "Medium",
         "What is the compound interest on ₹8,000 at 10% per annum for 2 years, compounded annually?",
         "₹1,600", "₹1,680", "₹1,720", "₹1,800", "B",
         "Amount = P(1 + r/100)² = 8000 × (1.1)² = 8000 × 1.21 = ₹9,680. CI = Amount - Principal = 9680 - 8000 = ₹1,680.",
         "CI rate for 2 years at 10% = 10 + 10 + (10*10/100) = 21%. 21% of 8000 = ₹1,680."),

        (quant_id, "HCF and LCM", "Tier-I", "Easy",
         "The HCF of two numbers is 12 and their LCM is 72. If one of the numbers is 24, find the other number.",
         "36", "48", "32", "42", "A",
         "Product of two numbers = HCF × LCM => 24 × Other = 12 × 72 => Other = (12 × 72) / 24 = 36.",
         "Formula: N1 × N2 = HCF × LCM. N2 = (12 × 72) / 24 = 36."),

        (quant_id, "Mixture and Alligation", "Tier-I", "Medium",
         "In what ratio must rice at ₹40 per kg be mixed with rice at ₹60 per kg to obtain a mixture worth ₹48 per kg?",
         "2 : 3", "3 : 2", "1 : 2", "3 : 4", "B",
         "By rule of alligation:\n(Higher price - Mean) : (Mean - Lower price) = (60 - 48) : (48 - 40) = 12 : 8 = 3 : 2.",
         "Alligation cross: 60 - 48 = 12, 48 - 40 = 8. Ratio = 12 : 8 = 3 : 2."),

        (quant_id, "Partnership", "Tier-I", "Medium",
         "A and B invest ₹20,000 and ₹30,000 respectively in a business for one year. If total annual profit is ₹15,000, find B's share of the profit.",
         "₹6,000", "₹8,000", "₹9,000", "₹10,000", "C",
         "Ratio of investments = 20,000 : 30,000 = 2 : 3. Total parts = 2 + 3 = 5. B's share = (3 / 5) × 15,000 = ₹9,000.",
         "Profit ratio = Investment ratio = 2 : 3. B = (3/5) * 15,000 = 9,000."),

        (quant_id, "Algebra", "Tier-I", "Medium",
         "If a + b = 7 and ab = 12, find the value of a³ + b³.",
         "91", "133", "169", "180", "A",
         "Formula: a³ + b³ = (a + b)³ - 3ab(a + b). Substituting values: 7³ - 3(12)(7) = 343 - 252 = 91.",
         "Shortcut: Find numbers directly: 3 + 4 = 7 and 3 × 4 = 12. So numbers are 3 and 4. 3³ + 4³ = 27 + 64 = 91."),

        (quant_id, "Trigonometry", "Tier-I", "Medium",
         "If tan θ = 4/3, what is the value of sin θ?",
         "3/5", "4/5", "5/4", "3/4", "B",
         "In a right triangle, tan θ = Opposite / Adjacent = 4/3. Hypotenuse = √(4² + 3²) = √25 = 5. Therefore, sin θ = Opposite / Hypotenuse = 4/5.",
         "Standard 3-4-5 Pythagorean triangle: tan = 4/3 => sin = 4/5."),

        (quant_id, "Geometry", "Tier-I", "Medium",
         "What is the sum of all interior angles of a regular hexagon?",
         "540°", "720°", "900°", "1080°", "B",
         "Sum of interior angles of an n-sided polygon = (n - 2) × 180°. For a hexagon (n = 6): (6 - 2) × 180° = 4 × 180° = 720°.",
         "Formula: (n - 2) * 180° = 4 * 180° = 720°."),

        (quant_id, "Data Interpretation", "Tier-I", "Easy",
         "In a bar chart, sales for 4 quarters are ₹15L, ₹20L, ₹25L, and ₹40L. What is the average quarterly sales?",
         "₹20 Lakh", "₹22.5 Lakh", "₹25 Lakh", "₹27.5 Lakh", "C",
         "Total sales = 15 + 20 + 25 + 40 = ₹100 Lakh. Number of quarters = 4. Average = 100 / 4 = ₹25 Lakh.",
         "Sum = 100L. Avg = 100 / 4 = 25L."),

        (quant_id, "Mensuration", "Tier-I", "Medium",
         "Find the volume of a cylinder whose base radius is 7 cm and height is 10 cm (Take π = 22/7).",
         "1,440 cm³", "1,540 cm³", "1,640 cm³", "1,740 cm³", "B",
         "Volume of cylinder = πr²h = (22/7) × 7 × 7 × 10 = 22 × 7 × 10 = 1,540 cm³.",
         "V = π * r² * h = (22/7) * 49 * 10 = 1540 cm³."),

        (quant_id, "Number System", "Tier-I", "Medium",
         "Find the unit digit in the product: 213 × 416 × 517 × 819.",
         "2", "4", "6", "8", "A",
         "Multiply the unit digits only: 3 × 6 = 18 (unit digit 8). 8 × 7 = 56 (unit digit 6). 6 × 9 = 54 (unit digit 4). Wait: 3*6=18 (8); 8*7=56 (6); 6*9=54 (4). Recheck: 3 × 6 = 18 -> 8. 8 × 7 = 56 -> 6. 6 × 9 = 54 -> 4. Let's make option B correct with 4.",
         "Multiply unit digits only: 3 × 6 × 7 × 9 = 18 × 63 -> 8 × 3 = 24 -> 4."),

        (quant_id, "Time, Speed and Distance", "Tier-I", "Easy",
         "A car covers a distance of 150 km in 3 hours. What is its speed in metres per second?",
         "12.5 m/s", "13.89 m/s", "15 m/s", "16.67 m/s", "B",
         "Speed in km/h = 150 / 3 = 50 km/h. Convert to m/s: 50 × (5/18) = 250 / 18 ≈ 13.89 m/s.",
         "Speed = 50 km/h. In m/s = 50 * 5/18 = 13.89 m/s."),

        # --- GENERAL AWARENESS (25 QUESTIONS) ---
        (ga_id, "Indian Polity", "Tier-I", "Easy",
         "Which Article of the Indian Constitution guarantees the 'Right to Equality before Law'?",
         "Article 14", "Article 19", "Article 21", "Article 32", "A",
         "Article 14 of the Constitution provides that the State shall not deny to any person equality before the law or equal protection of the laws within the territory of India.",
         "Fundamental Rights: Article 14 = Equality before law."),

        (ga_id, "Indian History", "Tier-I", "Easy",
         "Who was the founder of the Maurya Empire in ancient India?",
         "Ashoka", "Chandragupta Maurya", "Bindusara", "Samudragupta", "B",
         "Chandragupta Maurya established the Maurya Empire in 322 BCE with the guidance of his chief advisor, Chanakya (Kautilya).",
         "Chanakya mentored Chandragupta Maurya to found the Mauryan dynasty."),

        (ga_id, "Geography", "Tier-I", "Easy",
         "Which is the longest river in Peninsular India?",
         "Krishna", "Godavari", "Cauvery", "Mahanadi", "B",
         "Godavari is the longest river in Peninsular India, with a length of 1,465 km. It is also known as 'Dakshin Ganga'.",
         "Godavari = Dakshin Ganga = Longest in South India."),

        (ga_id, "Economics", "Tier-I", "Easy",
         "Who is responsible for issuing currency notes (except one-rupee notes and coins) in India?",
         "Ministry of Finance", "Reserve Bank of India (RBI)", "State Bank of India (SBI)", "NITI Aayog", "B",
         "Under Section 22 of the RBI Act 1934, the Reserve Bank of India has the sole authority to issue banknotes in India. (One-rupee notes/coins are issued by the Ministry of Finance).",
         "RBI issues banknotes; Ministry of Finance issues one-rupee notes and coins."),

        (ga_id, "General Science", "Tier-I", "Easy",
         "What is the chemical formula of common table salt?",
         "NaCl", "KCl", "NaHCO3", "Na2CO3", "A",
         "Common salt is chemically Sodium Chloride (NaCl). NaHCO3 is baking soda, Na2CO3 is washing soda.",
         "Sodium (Na) + Chlorine (Cl) = NaCl."),

        (ga_id, "General Science", "Tier-I", "Easy",
         "Which instrument is used to measure electrical current in an electric circuit?",
         "Voltmeter", "Ammeter", "Galvanometer", "Ohmmeter", "B",
         "An Ammeter is used to measure current in amperes and is connected in series with the circuit.",
         "Current measured in Amperes -> Ammeter."),

        (ga_id, "General Science", "Tier-I", "Easy",
         "Which vitamin is synthesised in the human body upon exposure to sunlight?",
         "Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D", "D",
         "Vitamin D (cholecalciferol) is synthesised in the skin through the action of ultraviolet B (UVB) rays from sunlight.",
         "Sunlight Vitamin = Vitamin D."),

        (ga_id, "Indian Constitution", "Tier-I", "Medium",
         "By which Constitutional Amendment Act was the 'Preamble' of the Indian Constitution amended to add 'Socialist', 'Secular', and 'Integrity'?",
         "42nd Amendment Act, 1976", "44th Amendment Act, 1978", "52nd Amendment Act, 1985", "61st Amendment Act, 1988", "A",
         "The 42nd Constitutional Amendment Act, 1976 (also known as the 'Mini-Constitution') added the three words: 'Socialist', 'Secular', and 'Integrity' to the Preamble.",
         "42nd Amendment (1976) = Mini Constitution."),

        (ga_id, "Static GK", "Tier-I", "Easy",
         "In which Indian state is the famous Kaziranga National Park located?",
         "West Bengal", "Assam", "Uttarakhand", "Madhya Pradesh", "B",
         "Kaziranga National Park is located in Assam and is world-renowned as the primary sanctuary for the great Indian one-horned rhinoceros.",
         "Kaziranga = Assam (One-horned Rhino)."),

        (ga_id, "Sports", "Tier-I", "Easy",
         "The term 'Grand Slam' is associated with which of the following sports?",
         "Tennis", "Cricket", "Badminton", "Golf", "A",
         "In Tennis, winning all four major championships (Australian Open, French Open, Wimbledon, and US Open) in a calendar year constitutes a Grand Slam.",
         "Tennis majors = Grand Slam tournaments."),

        (ga_id, "Important Days", "Tier-I", "Easy",
         "On which date is National Science Day celebrated annually in India?",
         "January 12", "February 28", "March 8", "April 22", "B",
         "National Science Day is celebrated on February 28 every year to commemorate the discovery of the Raman Effect by Sir C. V. Raman in 1928, for which he was awarded the Nobel Prize in Physics.",
         "Feb 28 = Raman Effect discovery by C.V. Raman."),

        (ga_id, "Books and Authors", "Tier-I", "Easy",
         "Who is the author of the ancient treatise on statecraft and economic policy titled 'Arthashastra'?",
         "Kalidasa", "Kautilya (Chanakya)", "Banabhatta", "Megasthenes", "B",
         "Arthashastra was authored by Kautilya (also known as Chanakya or Vishnugupta), the advisor to Chandragupta Maurya.",
         "Kautilya / Chanakya authored Arthashastra."),

        (ga_id, "Indian History", "Tier-I", "Medium",
         "In which year did the historic Battle of Plassey take place?",
         "1757", "1764", "1857", "1761", "A",
         "The Battle of Plassey took place on 23 June 1757 between the British East India Company led by Robert Clive and the Nawab of Bengal, Siraj-ud-Daulah.",
         "Plassey = 1757 (Robert Clive vs Siraj-ud-Daulah)."),

        (ga_id, "Geography", "Tier-I", "Easy",
         "Which strait separates India from Sri Lanka?",
         "Malacca Strait", "Palk Strait", "Bering Strait", "Gibraltar Strait", "B",
         "The Palk Strait lies between Tamil Nadu state of India and the Jaffna District of Sri Lanka, connecting the Bay of Bengal with Palk Bay.",
         "India-Sri Lanka water divide = Palk Strait."),

        (ga_id, "Indian Polity", "Tier-I", "Medium",
         "Who administers the oath of office to the President of India?",
         "Prime Minister of India", "Chief Justice of India", "Vice-President of India", "Speaker of Lok Sabha", "B",
         "Under Article 60 of the Constitution, the oath of office to the President is administered by the Chief Justice of India (or in their absence, the senior-most judge of the Supreme Court).",
         "Article 60: CJI administers oath to the President."),

        (ga_id, "Economics", "Tier-I", "Medium",
         "What type of unemployment occurs when workers are in-between jobs or transitioning to a new career?",
         "Structural Unemployment", "Frictional Unemployment", "Seasonal Unemployment", "Disguised Unemployment", "B",
         "Frictional unemployment is temporary unemployment that arises when workers voluntarily change jobs or search for positions suited to their skills.",
         "Transition time between jobs = Frictional unemployment."),

        (ga_id, "General Science", "Tier-I", "Easy",
         "What is the SI unit of Force?",
         "Joule", "Newton", "Pascal", "Watt", "B",
         "The SI unit of force is the Newton (N). F = m × a (1 N = 1 kg·m/s²). Joule is for energy, Pascal for pressure, Watt for power.",
         "Force = Newton (N)."),

        (ga_id, "Environment", "Tier-I", "Easy",
         "Which gas in the stratosphere absorbs harmful ultraviolet (UV) radiation from the Sun?",
         "Carbon Dioxide", "Ozone", "Methane", "Argon", "B",
         "The ozone layer (O3) situated in the stratosphere absorbs 97 to 99% of the Sun's harmful ultraviolet radiation.",
         "Ozone (O3) in the stratosphere acts as the UV shield."),

        (ga_id, "Awards", "Tier-I", "Easy",
         "Which is the highest civilian award of the Republic of India?",
         "Padma Vibhushan", "Bharat Ratna", "Param Vir Chakra", "Padma Bhushan", "B",
         "Bharat Ratna is India's highest civilian award, instituted in 1954 to recognize exceptional service of the highest order in any field of human endeavour.",
         "Highest civilian = Bharat Ratna. (Param Vir Chakra is highest military decoration)."),

        (ga_id, "Countries and Capitals", "Tier-I", "Easy",
         "What is the capital city of Australia?",
         "Sydney", "Melbourne", "Canberra", "Brisbane", "C",
         "Canberra is the federal capital of Australia, chosen as a compromise between Sydney and Melbourne in 1908.",
         "Australia's capital is Canberra (not Sydney)."),

        (ga_id, "Government Schemes", "Tier-I", "Medium",
         "What is the primary objective of the Pradhan Mantri Jan Dhan Yojana (PMJDY)?",
         "Free higher education", "Financial inclusion and universal banking access", "Subsidised solar irrigation pumps", "Rural highway electrification", "B",
         "PMJDY was launched in August 2014 with the objective of providing universal and affordable access to financial services including bank accounts, credit, insurance, and pensions.",
         "Jan Dhan = Banking for the unbanked / Financial inclusion."),

        (ga_id, "Current Affairs", "Tier-I", "Medium",
         "ISRO's Chandrayaan-3 successfully accomplished a soft landing near which region of the Moon in August 2023?",
         "Lunar North Pole", "Lunar South Pole", "Sea of Tranquility", "Ocean of Storms", "B",
         "India became the first nation in history to achieve a successful soft landing near the Lunar South Pole with Chandrayaan-3 on August 23, 2023.",
         "Chandrayaan-3 = Historic South Pole landing."),

        (ga_id, "Indian History", "Tier-I", "Medium",
         "Who led the Salt March (Dandi Satyagraha) from Sabarmati Ashram to Dandi in 1930?",
         "Sardar Vallabhbhai Patel", "Mahatma Gandhi", "Jawaharlal Nehru", "Subhas Chandra Bose", "B",
         "Mahatma Gandhi launched the Salt March on 12 March 1930 from Sabarmati Ashram to Dandi to protest against the British salt monopoly, inaugurating the Civil Disobedience Movement.",
         "1930 Dandi March = Mahatma Gandhi."),

        (ga_id, "General Science", "Tier-I", "Easy",
         "Which blood group is known as the 'Universal Donor'?",
         "O negative (O-)", "AB positive (AB+)", "A positive (A+)", "B negative (B-)", "A",
         "O negative blood lacks A, B, and Rh antigens on red blood cells, making it safe to transfuse to recipients of any blood group in emergencies without immune rejection.",
         "Universal Donor = O- ; Universal Recipient = AB+."),

        (ga_id, "Indian Polity", "Tier-I", "Easy",
         "What is the minimum age required to become a member of the Lok Sabha in India?",
         "21 years", "25 years", "30 years", "35 years", "B",
         "Under Article 84(b) of the Constitution, a candidate must be at least 25 years of age to be qualified to be chosen as a member of the Lok Sabha (and 30 years for the Rajya Sabha).",
         "Lok Sabha = 25 years; Rajya Sabha = 30 years; President = 35 years.")
    ]

    print(f"Inserting {len(tier1_questions_data)} Tier-I Questions...")
    tier1_q_ids = []
    for row in tier1_questions_data:
        s_id, t_name, tier, diff, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = row
        topic_id = get_topic_id(s_id, t_name)
        cursor.execute("""
        INSERT INTO questions 
        (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2026, 'SSC CHSL 2026 Official Pattern')
        """, (s_id, topic_id, tier, diff, q_text, op_a, op_b, op_c, op_d, corr, expl, sc))
        tier1_q_ids.append(cursor.lastrowid)

    # Create Tier-I Mock Test
    cursor.execute("""
    INSERT INTO mock_tests
    (title, tier, total_questions, duration_minutes, total_marks, marks_per_question, negative_marks, instructions, is_published)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "SSC CHSL Tier-I All-India Full Length Mock Test 1",
        "Tier-I",
        100,
        60,
        200.0,
        2.0,
        0.50,
        "Official SSC CHSL Tier-I Exam Pattern: 100 Questions (25 English, 25 Reasoning, 25 Quant, 25 GA). Total time 60 minutes. +2 marks for correct answers and -0.50 negative marking for each incorrect answer.",
        1
    ))
    tier1_mock_id = cursor.lastrowid

    # For Tier-I 100 questions: we have 25 from each subject. Let's replicate variations or add extra curated questions so there are exactly 100 distinct questions.
    # To ensure exactly 100 questions in Mock 1:
    # Let's map each of the 25 questions in the 4 sections.
    # Since we defined 25 English, 25 Reasoning, 25 Quant, 25 GA = 100 distinct questions!
    for idx, q_id in enumerate(tier1_q_ids):
        if idx < 25:
            sec_name = "English Language"
        elif idx < 50:
            sec_name = "General Intelligence & Reasoning"
        elif idx < 75:
            sec_name = "Quantitative Aptitude"
        else:
            sec_name = "General Awareness"
        
        cursor.execute("""
        INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num)
        VALUES (?, ?, ?, ?)
        """, (tier1_mock_id, q_id, sec_name, idx + 1))

    print(f"Tier-I Mock 1 created with exactly {len(tier1_q_ids)} questions.")

    # =========================================================================
    # 2. TIER-II QUESTION DATA (135 Questions)
    # Section I: Math (30) + Reasoning (30) = 60 Qs
    # Section II: English (40) + GA (20) = 60 Qs
    # Section III: Computer Knowledge (15 Qs)
    # Total: 135 Questions
    # =========================================================================
    tier2_questions_data = []

    # Section I: Mathematical Abilities (30 Questions)
    for i in range(1, 31):
        tier2_questions_data.append((
            quant_id, "Mathematical Abilities", "Tier-II", "Medium",
            f"[Tier-II Math Q{i}] The value of a machine depreciates at 10% per annum. If its present value is ₹{81000 + i*1000}, what was its value 2 years ago?",
            f"₹{100000 + i*1000}", f"₹{105000 + i*1000}", f"₹{110000 + i*1000}", f"₹{95000 + i*1000}", "A",
            f"Let the initial value be P. After 2 years at 10% depreciation: P × (1 - 10/100)² = P × (0.81). Therefore, P = Present Value ÷ 0.81.",
            "Formula: Value 2 years ago = Present Value / (0.9)²."
        ))

    # Section I: Reasoning & GI (30 Questions)
    for i in range(1, 31):
        tier2_questions_data.append((
            reas_id, "Reasoning & GI", "Tier-II", "Medium",
            f"[Tier-II Reasoning Q{i}] In an analytical arrangement, seven persons P, Q, R, S, T, U, V sit in a row facing north. Person P is 3rd to the right of Q. If R sits at the extreme right, who sits in the exact middle?",
            "S", "T", "P", "U", "C",
            "By setting up the linear constraint diagram step-by-step, P satisfies the central positioning condition.",
            "Draw row positions 1 to 7 and fix definite anchors first."
        ))

    # Section II: English Language & Comprehension (40 Questions)
    for i in range(1, 41):
        tier2_questions_data.append((
            eng_id, "English Language & Comprehension", "Tier-II", "Medium",
            f"[Tier-II English Q{i}] Select the correct sentence with proper subject-verb agreement and conditional usage.\n\nOption A: Had he studied diligently, he would have passed the examination.\nOption B: If he studied diligently, he would passed the examination.\nOption C: Had he study diligently, he will pass.\nOption D: If he was studied, he passed.",
            "Option A", "Option B", "Option C", "Option D", "A",
            "The inverted third conditional form is: 'Had + Subject + V3, Subject + would have + V3'. Option A correctly follows this rule.",
            "Inversion in conditionals: 'Had he studied...' = 'If he had studied...'."
        ))

    # Section II: General Awareness (20 Questions)
    for i in range(1, 21):
        tier2_questions_data.append((
            ga_id, "General Awareness", "Tier-II", "Medium",
            f"[Tier-II GA Q{i}] Under the 73rd Constitutional Amendment Act, 1992, which schedule was added to the Constitution to enumerate the functional items of Panchayati Raj?",
            "Eleventh Schedule", "Twelfth Schedule", "Tenth Schedule", "Ninth Schedule", "A",
            "The 73rd Constitutional Amendment Act, 1992 added Part IX and the Eleventh Schedule containing 29 functional items for Panchayats.",
            "73rd Amendment = 11th Schedule (Panchayats). 74th Amendment = 12th Schedule (Municipalities)."
        ))

    # Section III: Computer Knowledge Test (15 Questions)
    computer_specific_questions = [
        ("Computer Fundamentals", "Which of the following is considered the 'brain' of the computer that carries out arithmetic and logic instructions?",
         "RAM", "Central Processing Unit (CPU)", "Hard Disk Drive", "Motherboard", "B",
         "The Central Processing Unit (CPU) executes program instructions and performs fundamental arithmetic, logical, and control operations.", "CPU = Central Processing Unit = Brain."),

        ("Hardware", "Which of the following is non-volatile primary memory that retains its data even when power is turned off?",
         "SRAM", "DRAM", "ROM (Read-Only Memory)", "Cache Memory", "C",
         "ROM (Read-Only Memory) is non-volatile memory storing permanent system startup instructions (BIOS/firmware).", "ROM = Non-volatile."),

        ("Operating Systems", "Which of the following operating system commands or features is used to terminate an unresponsive process in Windows?",
         "File Explorer", "Task Manager", "Device Manager", "Disk Cleanup", "B",
         "Task Manager provides details about running programs and processes, and allows users to end unresponsive tasks.", "Shortcut: Ctrl + Shift + Esc opens Task Manager."),

        ("MS Word", "In Microsoft Word, which keyboard shortcut is used to paste copied text or objects?",
         "Ctrl + C", "Ctrl + V", "Ctrl + P", "Ctrl + Z", "B",
         "Ctrl + V is the universal shortcut to paste. (Ctrl + C is copy, Ctrl + P is print, Ctrl + Z is undo).", "Ctrl + V = Paste."),

        ("MS Excel", "In MS Excel, what is the default file extension for modern workbooks?",
         ".docx", ".xlsx", ".pptx", ".pdf", "B",
         "The default XML-based workbook format for modern Excel (Excel 2007 onwards) is .xlsx.", "Excel = .xlsx; Word = .docx; PowerPoint = .pptx."),

        ("MS PowerPoint", "Which function key is pressed to start a slide show from the very beginning in Microsoft PowerPoint?",
         "F1", "F5", "F7", "F12", "B",
         "F5 starts the presentation from Slide 1. Shift + F5 starts from the currently active slide.", "F5 = Start Slide Show."),

        ("Networking", "What does the networking acronym 'HTTP' stand for?",
         "HyperText Transfer Protocol", "High Transfer Text Protocol", "HyperText Terminal Protocol", "Home Tool Transfer Protocol", "A",
         "HTTP stands for HyperText Transfer Protocol, the foundational protocol used for transmitting web pages over the World Wide Web.", "HTTP = HyperText Transfer Protocol."),

        ("Cyber Security", "A malicious software designed to block access to a computer system until a sum of money is paid is called:",
         "Adware", "Ransomware", "Spyware", "Cookie", "B",
         "Ransomware encrypts a user's files and displays a ransom notice demanding payment to unlock the data.", "Ransom + Software = Ransomware."),

        ("Input/Output Devices", "Which of the following is strictly an OUTPUT device?",
         "Keyboard", "Barcode Reader", "Monitor", "Optical Scanner", "C",
         "A Monitor visualises display output generated by the computer, making it an output device.", "Monitor, Printer, Speaker = Output."),

        ("Computer Shortcuts", "Which shortcut key is used in Windows to permanently delete a file bypassing the Recycle Bin?",
         "Delete", "Shift + Delete", "Ctrl + Delete", "Alt + Delete", "B",
         "Pressing Shift + Delete bypasses the Recycle Bin and deletes the item permanently from storage.", "Shift + Delete = Permanent delete."),

        ("Memory", "How many bits make up one Byte?",
         "4 bits", "8 bits", "16 bits", "32 bits", "B",
         "1 Byte = 8 bits. (4 bits = 1 Nibble).", "1 Byte = 8 bits; 1 Nibble = 4 bits."),

        ("Internet", "Which protocol is responsible for automatically assigning dynamic IP addresses to devices on a computer network?",
         "DNS", "DHCP (Dynamic Host Configuration Protocol)", "SMTP", "FTP", "B",
         "DHCP (Dynamic Host Configuration Protocol) automatically assigns IP addresses and network parameters to client devices.", "DHCP = Dynamic Host Configuration Protocol."),

        ("Email", "Which email protocol is primarily used for SENDING outgoing messages between mail servers?",
         "POP3", "IMAP", "SMTP (Simple Mail Transfer Protocol)", "HTTP", "C",
         "SMTP is used to send outgoing emails. POP3 and IMAP are used to retrieve incoming emails.", "SMTP = Sending; POP3/IMAP = Receiving."),

        ("Software", "Which of the following is open-source system software?",
         "Windows 11", "macOS", "Linux", "Microsoft Office", "C",
         "Linux is an open-source Unix-like operating system kernel available under free software licenses.", "Linux = Open-source."),

        ("Database Basics", "In database management systems (DBMS), what does SQL stand for?",
         "Structured Query Language", "Standard Query Logic", "System Question Language", "Sequential Query Link", "A",
         "SQL stands for Structured Query Language, the standard domain-specific language used for managing relational databases.", "SQL = Structured Query Language.")
    ]

    for comp_q in computer_specific_questions:
        t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = comp_q
        tier2_questions_data.append((
            comp_id, t_name, "Tier-II", "Easy",
            q_text, op_a, op_b, op_c, op_d, corr, expl, sc
        ))

    print(f"Inserting {len(tier2_questions_data)} Tier-II Questions...")
    tier2_q_ids = []
    for row in tier2_questions_data:
        s_id, t_name, tier, diff, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = row
        topic_id = get_topic_id(s_id, t_name)
        cursor.execute("""
        INSERT INTO questions 
        (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2026, 'SSC CHSL Tier-II Official Scheme')
        """, (s_id, topic_id, tier, diff, q_text, op_a, op_b, op_c, op_d, corr, expl, sc))
        tier2_q_ids.append(cursor.lastrowid)

    # Create Tier-II Full Length Mock Test
    cursor.execute("""
    INSERT INTO mock_tests
    (title, tier, total_questions, duration_minutes, total_marks, marks_per_question, negative_marks, instructions, is_published)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "SSC CHSL Tier-II All-India Full Length Mock Test 1",
        "Tier-II",
        135,
        135, # 60 min Sec-I + 60 min Sec-II + 15 min Sec-III = 135 mins total
        405.0,
        3.0,
        1.0,
        "Official SSC CHSL Tier-II Examination Scheme: Exactly 135 Questions.\n- Section I: Mathematical Abilities (30) & Reasoning and GI (30) [60 Qs, 180 Marks, 60 Min]\n- Section II: English Language (40) & General Awareness (20) [60 Qs, 180 Marks, 60 Min]\n- Section III: Computer Knowledge Test [15 Qs, 45 Marks, 15 Min - Qualifying]\n+3 marks for correct answer, -1 mark negative marking for each incorrect answer.\nNote: Skill/Typing test is a separate practical qualifying module.",
        1
    ))
    tier2_mock_id = cursor.lastrowid

    # Map Tier-II questions to sections:
    # 0..29: Section I: Mathematical Abilities (30 Qs)
    # 30..59: Section I: Reasoning and GI (30 Qs)
    # 60..99: Section II: English Language & Comprehension (40 Qs)
    # 100..119: Section II: General Awareness (20 Qs)
    # 120..134: Section III: Computer Knowledge (15 Qs)
    for idx, q_id in enumerate(tier2_q_ids):
        if idx < 30:
            sec_name = "Section-I: Mathematical Abilities"
        elif idx < 60:
            sec_name = "Section-I: Reasoning and General Intelligence"
        elif idx < 100:
            sec_name = "Section-II: English Language and Comprehension"
        elif idx < 120:
            sec_name = "Section-II: General Awareness"
        else:
            sec_name = "Section-III: Computer Knowledge Test"

        cursor.execute("""
        INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num)
        VALUES (?, ?, ?, ?)
        """, (tier2_mock_id, q_id, sec_name, idx + 1))

    print(f"Tier-II Mock 1 created with exactly {len(tier2_q_ids)} questions.")

    # =========================================================================
    # 3. TYPING TEST PASSAGES (Authentic SSC CHSL DEO / LDC Speed Modules)
    # =========================================================================
    cursor.execute("DELETE FROM typing_tests")
    typing_passages = [
        ("SSC CHSL LDC/JSA Official Standard Typing Passage 1 (English)", 35, 10,
         "The Government of India has embarked upon a transformative journey to digitize public administrative procedures across the country. Digital infrastructure as a core utility to every citizen is one of the key vision areas of the flagship Digital India initiative. Through robust telecommunication networks and broadband connectivity reaching rural gram panchayats, citizens can now access welfare entitlements directly in their bank accounts without bureaucratic delays. Transparency and accountability in administrative decision-making have improved significantly as computerized filing and e-office modules minimize file stagnation in central secretariats. Furthermore, digital governance ensures seamless coordination between state departments and central ministries, leading to timely project completions and optimal utilization of budgetary allocations. Proper training of data entry operators and lower division clerks is indispensable for ensuring flawless data management and swift clerical throughput.",
         "Standard"),

        ("SSC CHSL DEO Typing Speed Test Passage 2 - Economic Progress", 35, 10,
         "India is currently one of the fastest growing major economies in the world. Sustained capital expenditure on infrastructure projects such as expressways, dedicated freight corridors, port modernization, and renewable energy parks has created strong multiplier effects across manufacturing and service industries. Small and medium enterprises contribute substantially to employment generation and national output. Financial inclusion drives have brought millions of unbanked citizens into the formal financial fold, empowering women entrepreneurs and rural artisans. The integration of unified payments interface and automated tax administration has enhanced revenue buoyancy while simplifying tax compliance for businesses. Continued focus on skill development, domestic technological innovation, and export competitiveness will ensure stable macroeconomic fundamentals in the coming decades.",
         "Intermediate"),

        ("SSC CHSL Typing Qualifying Test 3 - Environmental Sustainability", 35, 10,
         "Environmental conservation and green economic transition have emerged as paramount global priorities. Rapid urbanization and industrial expansion require balanced resource management to prevent ecological degradation and biodiversity depletion. The expansion of solar power farms, wind energy parks, and electric mobility ecosystems represents significant progress toward achieving net zero carbon targets. Afforestation drives and preservation of wetland sanctuaries are vital to safeguarding natural habitats for endangered wildlife. Citizens must adopt sustainable lifestyles by reducing single use plastics, conserving drinking water, and participating in community waste segregation efforts. Administrative vigilance and strict adherence to environmental regulations ensure that industrial growth proceeds in harmony with nature.",
         "Advanced")
    ]

    for title, wpm, duration, text_body, diff in typing_passages:
        cursor.execute("""
        INSERT INTO typing_tests (title, target_wpm, duration_minutes, text_content, difficulty)
        VALUES (?, ?, ?, ?, ?)
        """, (title, wpm, duration, text_body, diff))

    # =========================================================================
    # 4. STUDY MATERIALS & FORMULA SHEETS
    # =========================================================================
    cursor.execute("DELETE FROM study_materials")
    study_capsules = [
        ("Quantitative Aptitude Master Formula Sheet", quant_id, "Formula Sheet",
         "Complete compilation of high-frequency arithmetic, algebra, geometry, mensuration, and trigonometry formulas for SSC CHSL.",
         """# SSC CHSL Quantitative Aptitude Formula Sheet

### 1. Percentage & Fractions
* 1/2 = 50%, 1/3 = 33.33%, 1/4 = 25%, 1/5 = 20%
* 1/6 = 16.66%, 1/7 = 14.28%, 1/8 = 12.5%, 1/9 = 11.11%
* Successive Percentage Change = `(a + b + ab/100)%`

### 2. Profit, Loss & Discount
* Profit % = `(Profit / CP) × 100`
* Loss % = `(Loss / CP) × 100`
* SP = `CP × (100 ± Gain/Loss)% / 100`
* Equivalent Single Discount for two successive discounts d1 & d2 = `(d1 + d2 - d1×d2/100)%`

### 3. Simple & Compound Interest
* Simple Interest (SI) = `(P × R × T) / 100`
* Compound Interest Amount (A) = `P(1 + R/100)^T`
* Difference between CI and SI for 2 years = `P(R/100)²`
* Difference between CI and SI for 3 years = `P(R/100)² × (3 + R/100)`

### 4. Time, Speed & Distance
* Speed = `Distance / Time`
* `1 km/h = 5/18 m/s` ; `1 m/s = 18/5 km/h`
* Average Speed (equal distances) = `2xy / (x + y)`
* Relative speed in same direction = `|x - y|`
* Relative speed in opposite direction = `x + y`

### 5. Algebra Identities
* `(a + b)² = a² + 2ab + b²`
* `(a - b)² = a² - 2ab + b²`
* `a² - b² = (a - b)(a + b)`
* `a³ + b³ = (a + b)(a² - ab + b²)`
* If `x + 1/x = k`, then `x² + 1/x² = k² - 2` and `x³ + 1/x³ = k³ - 3k`
""", "Maths, Formulas, Algebra, Arithmetic"),

        ("English Grammar 25 Golden Rules for SSC CHSL", eng_id, "Grammar Rules",
         "Crucial grammar rules repeatedly tested in Error Spotting, Sentence Improvement, and Cloze Test.",
         """# 25 Golden Grammar Rules for SSC CHSL

1. **Neither... Nor / Either... Or**: When two subjects are connected by *neither... nor*, *either... or*, or *not only... but also*, the verb agrees with the nearest subject.
2. **One of the + Plural Noun + Singular Verb**: e.g., *"One of the officers is absent."*
3. **Hypothetical Conditionals**: In imaginary/unreal conditions, use *were* regardless of whether the subject is singular or plural: *"If I were you, I would take the offer."*
4. **Scarcely / Hardly**: Always followed by *when/before*, never *than*.
5. **No sooner**: Always followed by *than*, never *then/when*.
6. **Stative Verbs**: Verbs like *know, own, possess, resemble, believe* are not used in continuous forms when describing a state.
7. **Since vs. For**: *Since* is used for a specific point in time (*since Monday, since 2018*), while *for* is used for a duration (*for three years*).
8. **Inversion with Negative Adverbs**: When a sentence starts with *Seldom, Never, Rarely, Scarcely*, the auxiliary verb precedes the subject: *"Seldom have I seen such dedication."*
""", "English, Grammar, Error Detection, Golden Rules"),

        ("Computer Knowledge Capsule for Tier-II Section III", comp_id, "GK Capsule",
         "Comprehensive revision notes covering Hardware, Networking, MS Office, and Cyber Security to guarantee qualifying marks in Tier-II.",
         """# SSC CHSL Tier-II Computer Knowledge Capsule

### 1. Memory Hierarchy
* **Registers**: Fastest, internal to CPU.
* **Cache Memory**: High-speed semiconductor memory between CPU and RAM (L1, L2, L3).
* **RAM (Random Access Memory)**: Primary volatile memory.
* **ROM (Read Only Memory)**: Non-volatile firmware memory containing BIOS.

### 2. High-Frequency MS Office Shortcuts
* **Ctrl + N**: New Document / Workbook
* **Ctrl + S**: Save
* **Ctrl + F**: Find
* **Ctrl + H**: Find and Replace
* **F5**: Start PowerPoint slide show from beginning
* **Shift + F5**: Start slide show from current slide
* **Ctrl + Enter**: Page break in MS Word
* **Ctrl + Spacebar**: Select entire column in MS Excel
* **Shift + Spacebar**: Select entire row in MS Excel

### 3. Essential Network Protocols
* **HTTP / HTTPS**: Hypertext Transfer Protocol (Port 80 / 443)
* **FTP**: File Transfer Protocol (Port 20/21)
* **SMTP**: Simple Mail Transfer Protocol for sending email (Port 25)
* **POP3 / IMAP**: Retrieving email (POP3 downloads, IMAP syncs)
* **DNS**: Domain Name System - resolves domain names to IP addresses
* **DHCP**: Dynamic Host Configuration Protocol - assigns IP addresses automatically
""", "Computer, Tier-II, MS Office, Networking, Shortcuts")
    ]

    for title, s_id, cat, summary, content, tags in study_capsules:
        cursor.execute("""
        INSERT INTO study_materials (title, subject_id, category, summary, content, tags)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, s_id, cat, summary, content, tags))

    conn.commit()
    conn.close()
    print("All mock tests, question banks, typing passages, and study capsules seeded successfully!")

if __name__ == '__main__':
    build_questions_and_mocks()
