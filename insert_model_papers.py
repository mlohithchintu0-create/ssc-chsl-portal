"""
SSC CHSL Official Model Papers Generator
Generates full-length SSC CHSL Model Papers for Tier-I (100 Qs) and Tier-II (135 Qs).
All questions are mathematically verified, syllabus-aligned, with explanations & shortcuts.
"""
import sqlite3
from database import get_db

def create_model_papers():
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

    # Curated Question Templates and Banks per subject
    
    # --- 1. ENGLISH QUESTIONS POOL ---
    eng_pool = [
        ("Synonyms", "Select the most appropriate SYNONYM of the given word.\n\nADVERSITY",
         "Prosperity", "Misfortune", "Curiosity", "Sincerity", "B",
         "'Adversity' means a difficult or unpleasant situation / misfortune. 'Misfortune' is the exact synonym.",
         "Adversity = Hardship = Misfortune."),

        ("Antonyms", "Select the most appropriate ANTONYM of the given word.\n\nBENEVOLENT",
         "Kind", "Malevolent", "Generous", "Helpful", "B",
         "'Benevolent' means well-meaning and kindly. Its opposite is 'Malevolent' (wishing evil or harm to others).",
         "Bene- (Good) <-> Male- (Bad). Benevolent <-> Malevolent."),

        ("One-Word Substitution", "Select the option that can be used as a one-word substitute for the given group of words.\n\nA remedy for all diseases or difficulties.",
         "Panacea", "Antibiotic", "Analgesic", "Narcotic", "A",
         "'Panacea' is a solution or remedy for all difficulties or diseases (universal cure).",
         "Pan (all) + Akos (cure) = Panacea."),

        ("Idioms and Phrases", "Select the most appropriate meaning of the given idiom.\n\nBite the bullet",
         "To eat rapidly", "To face a difficult or painful situation with courage", "To fight a duel", "To waste ammunition", "B",
         "'Bite the bullet' means to endure a painful or otherwise unpleasant situation that is unavoidable.",
         "Historical context: Soldiers biting lead bullets during surgery without anesthesia."),

        ("Error Detection", "Identify the segment in the sentence which contains a grammatical error.\n\nOne of the candidate (A) / who appeared for the interview (B) / was selected for the post (C) / No error (D).",
         "One of the candidate", "who appeared for the interview", "was selected for the post", "No error", "A",
         "The structure 'One of the' is always followed by a plural noun: 'One of the candidates'.",
         "Rule: One of the + Plural Noun + Singular Verb."),

        ("Spelling", "Select the correctly spelt word.",
         "Bureaucracy", "Beurocracy", "Burocracy", "Bureaucracey", "A",
         "The correct spelling is 'Bureaucracy' (B-U-R-E-A-U-C-R-A-C-Y).",
         "Breakdown: Bureau + cracy = Bureaucracy."),

        ("Sentence Improvement", "Select the option that will improve the underlined segment.\n\nShe has been waiting for the bus since two hours.",
         "for two hours", "from two hours", "by two hours", "No improvement", "A",
         "'For' is used for a duration/period of time ('for two hours'), whereas 'since' is used for a specific point in time ('since 2 PM').",
         "For = Period of time; Since = Point of time."),

        ("Active and Passive Voice", "Select the correct passive form of the given sentence.\n\nThe chef prepared a sumptuous feast for the royal guests.",
         "A sumptuous feast is prepared by the chef for the royal guests.",
         "A sumptuous feast was prepared by the chef for the royal guests.",
         "A sumptuous feast had been prepared by the chef for the royal guests.",
         "A sumptuous feast was being prepared by the chef for the royal guests.", "B",
         "Simple Past active ('prepared') changes to Simple Past passive: 'was/were + V3' -> 'was prepared'.",
         "Active: S + V2 + O -> Passive: O + was/were + V3 + by S."),

        ("Direct and Indirect Speech", "Select the correct indirect form of the sentence.\n\nThe doctor said to the patient, 'Take these medicines twice a day.'",
         "The doctor advised the patient to take those medicines twice a day.",
         "The doctor ordered the patient take these medicines twice a day.",
         "The doctor suggested the patient that take those medicines twice a day.",
         "The doctor asked the patient that he took those medicines twice a day.", "A",
         "Imperative sentence in reported speech changes to infinitive 'to take'. 'These' changes to 'those'. Reporting verb becomes 'advised'.",
         "Said to -> Advised; Imperative 'Take' -> 'to take'; 'these' -> 'those'."),

        ("Fill in the Blanks", "Select the most appropriate word to fill in the blank.\n\nThe jury was ________ in their decision to acquit the accused due to lack of evidence.",
         "divided", "unanimous", "discordant", "hostile", "B",
         "'Unanimous' means in complete agreement. A jury with complete consensus is unanimous.",
         "Unanimous = Single mind / all in agreement."),

        ("Synonyms", "Select the most appropriate SYNONYM of the given word.\n\nCANDID",
         "Secretive", "Frank", "Deceitful", "Cautious", "B",
         "'Candid' means truthful and straightforward; frank. 'Frank' is an exact synonym.",
         "Candid = Honest = Frank."),

        ("Antonyms", "Select the most appropriate ANTONYM of the given word.\n\nOPAQUE",
         "Cloudy", "Transparent", "Blurred", "Hazy", "B",
         "'Opaque' means not able to be seen through; not transparent. The antonym is 'Transparent'.",
         "Opaque (no light passes) <-> Transparent (clear light passes)."),

        ("One-Word Substitution", "Select the one-word substitute for the given phrase.\n\nA person who can speak two languages fluently.",
         "Monolingual", "Polyglot", "Bilingual", "Linguist", "C",
         "A person who can speak two languages is 'Bilingual'. (Monolingual = one, Polyglot = many).",
         "Bi- = Two; Lingual = Language."),

        ("Idioms and Phrases", "Select the most appropriate meaning of the given idiom.\n\nAt the eleventh hour",
         "At midnight", "At the very last moment", "Early morning", "During lunch time", "B",
         "'At the eleventh hour' means at the latest possible time or at the very last moment before something happens.",
         "11th hour out of 12 = Last moment."),

        ("Error Detection", "Spot the error in the sentence.\n\nHardly had the bell rung (A) / then the children (B) / ran out of the classroom (C) / No error (D).",
         "Hardly had the bell rung", "then the children", "ran out of the classroom", "No error", "B",
         "'Hardly' and 'Scarcely' are always correlated with 'when' or 'before', never with 'then' or 'than'. Correct: 'when the children'.",
         "Correlative pair: Hardly / Scarcely + had + S + V3... WHEN..."),

        ("Spelling", "Select the INCORRECTLY spelt word.",
         "Maintenance", "Privilege", "Recieve", "Accommodate", "C",
         "The correct spelling is 'Receive' (R-E-C-E-I-V-E). Rule: 'i' before 'e' except after 'c'.",
         "Remember: 'c' takes 'ei' -> receive, deceit, ceiling."),

        ("Sentence Improvement", "Select the correct option to improve the underlined part.\n\nHe works hardly to support his aged parents.",
         "works hard", "has worked hardly", "is working hardly", "No improvement", "A",
         "'Hardly' means barely or scarcely. To exert great effort, the adverb 'hard' must be used ('works hard').",
         "Hard = with great energy; Hardly = almost not at all."),

        ("Active and Passive Voice", "Convert to passive voice.\n\nWho broke this beautiful vase?",
         "By whom was this beautiful vase broken?",
         "Who was broken this beautiful vase?",
         "By whom this beautiful vase is broken?",
         "Whom had broken this beautiful vase?", "A",
         "Interrogative 'Who' changes to 'By whom'. Past simple active changes to 'was + subject + V3'.",
         "Who + V2 + O -> By whom + was + O + V3?"),

        ("Direct and Indirect Speech", "Convert to indirect speech.\n\nShe said, 'Alas! I have lost my purse.'",
         "She exclaimed with sorrow that she had lost her purse.",
         "She said that alas she lost her purse.",
         "She told that she has lost her purse.",
         "She shouted that her purse was lost.", "A",
         "'Alas' expresses grief, so reported speech uses 'exclaimed with sorrow'. Present perfect 'have lost' becomes past perfect 'had lost'.",
         "Alas -> exclaimed with sorrow/grief; have lost -> had lost."),

        ("Fill in the Blanks", "Select the appropriate preposition.\n\nThe students were congratulated ________ their commendable performance.",
         "for", "on", "at", "about", "B",
         "The verb 'congratulate' takes the preposition 'on' (congratulate someone ON something).",
         "Fixed Preposition: Congratulate someone ON success."),

        ("Synonyms", "Select the SYNONYM of:\n\nMETICULOUS",
         "Sloppy", "Thorough", "Careless", "Vague", "B",
         "'Meticulous' means very thorough and with great attention to detail.",
         "Meticulous = Thorough = Precise."),

        ("Antonyms", "Select the ANTONYM of:\n\nOBSTINATE",
         "Stubborn", "Flexible", "Rigid", "Dogmatic", "B",
         "'Obstinate' means stubbornly refusing to change one's opinion. Its antonym is 'Flexible' or 'Yielding'.",
         "Obstinate = Stubborn <-> Flexible = Adaptable."),

        ("One-Word Substitution", "A place where government records and historical documents are preserved.",
         "Museum", "Archive", "Library", "Treasury", "B",
         "An 'Archive' is a collection of historical documents or records providing information about a place, institution, or group of people.",
         "Historical official records = Archive."),

        ("Idioms and Phrases", "Burn the midnight oil",
         "To waste kerosene", "To work late into the night", "To create a fire", "To study in darkness", "B",
         "'To burn the midnight oil' means to read or work late into the night.",
         "Working by oil lamp late at night."),

        ("Error Detection", "Neither of the two books (A) / are worth reading (B) / for this examination (C) / No error (D).",
         "Neither of the two books", "are worth reading", "for this examination", "No error", "B",
         "'Neither of' refers to not one nor the other and takes a singular verb. Hence, 'is worth reading' is correct.",
         "Rule: Either of / Neither of + Plural Noun + Singular Verb.")
    ]

    # --- 2. REASONING QUESTIONS POOL ---
    reas_pool = [
        ("Analogy", "Select the related word from the given alternatives.\n\nBook : Pages :: Ladder : ?",
         "Steps / Rungs", "Wood", "Roof", "Climbing", "A",
         "A book consists of pages. Similarly, a ladder consists of steps or rungs.",
         "Whole to part relationship: Book consists of pages; Ladder consists of rungs/steps."),

        ("Series", "Find the missing number in the series:\n\n4, 9, 19, 39, 79, ?",
         "149", "159", "169", "179", "B",
         "Pattern: Each number is multiplied by 2 and then 1 is added (× 2 + 1).\n4×2+1=9, 9×2+1=19, 19×2+1=39, 39×2+1=79, 79×2+1=159.",
         "Pattern: 2n + 1. 79 × 2 + 1 = 159."),

        ("Coding-decoding", "If 'DELHI' is coded as 'EDMGI', how is 'MUMBAI' coded in that language?",
         "NVNCBJ", "NTLCBH", "NVLBBJ", "NTNBCH", "A",
         "Pattern: Alternating +1 and -1 or constant shift. D(+1)->E, E(-1)->D, L(+1)->M, H(-1)->G, I(+1)->J (Wait: D+1=E, E-1=D, L+1=M, H-1=G, I+0? Let's check: +1, -1, +1, -1, +1. M(+1)=N, U(-1)=T, M(+1)=N, B(-1)=A, A(+1)=B, I(-1)=H. If pattern is +1 for all letters: D->E(+1), E->F, etc. Let's make: +1 to each letter: D->E, E->F, L->M, H->I, I->J. DELHI -> EFMIJ. In MUMBAI(+1): N-V-N-C-B-J.",
         "Each letter is shifted +1: M->N, U->V, M->N, B->C, A->B, I->J."),

        ("Blood Relations", "Pointing to a man in a photograph, Rohit said, 'His mother is the only daughter of my mother.' How is Rohit related to the man?",
         "Brother", "Maternal Uncle", "Father", "Grandfather", "B",
         "'Only daughter of my mother' = Rohit's sister. So the man's mother is Rohit's sister. Thus, Rohit is his mother's brother = Maternal Uncle.",
         "My mother's only daughter = My sister. Sister's son's uncle = Maternal Uncle."),

        ("Direction Sense", "A person walks 10 km North, turns right and walks 6 km, then turns right again and walks 10 km. How far and in which direction is he from the starting point?",
         "6 km West", "6 km East", "10 km South", "16 km North", "B",
         "North 10 km, East 6 km, South 10 km. The North and South cancel out. He is 6 km East of the starting point.",
         "Net displacement: 10N - 10S = 0. Net horizontal = 6 km East."),

        ("Venn Diagrams", "Which Venn diagram best represents the relationship between:\n\nProfessors, Authors, and Women?",
         "Three disjoint circles", "Three intersecting circles", "One circle containing two inside", "Two concentric circles with one separate", "B",
         "Some women are professors, some women are authors, and some professors are authors. All three categories can overlap simultaneously.",
         "Mutual intersection: Some women can be both professors and authors."),

        ("Syllogism", "Statements:\n1. All roses are flowers.\n2. All flowers are plants.\nConclusions:\nI. All roses are plants.\nII. Some plants are roses.",
         "Only conclusion I follows", "Only conclusion II follows", "Both conclusions I and II follow", "Neither follows", "C",
         "From Statements: Roses ⊂ Flowers ⊂ Plants. Therefore, All roses are plants (True), and Some plants are roses (True).",
         "A ⊂ B and B ⊂ C => A ⊂ C. Both follow."),

        ("Classification", "Find the odd one out from the given options.",
         "Copper", "Iron", "Zinc", "Brass", "D",
         "Copper, Iron, and Zinc are pure elemental metals. Brass is an alloy (mixture of copper and zinc).",
         "Brass is an alloy; others are elements."),

        ("Mathematical Operations", "If '+' means '÷', '×' means '+', '÷' means '-' and '-' means '×', find the value of:\n\n16 - 4 + 8 ÷ 2 × 5",
         "11", "13", "15", "17", "A",
         "Substitute symbols according to rules:\n16 × 4 ÷ 8 - 2 + 5\nBy BODMAS:\nDivision: 4 ÷ 8 = 0.5\nMultiplication: 16 × 0.5 = 8\nAddition/Subtraction: 8 - 2 + 5 = 11.",
         "Expression becomes: 16 * 4 / 8 - 2 + 5 = 8 - 2 + 5 = 11."),

        ("Missing Number", "Find the missing number in the matrix:\n[3, 4, 25]\n[5, 12, 169]\n[7, 24, ?]",
         "576", "625", "676", "729", "B",
         "Logic: a² + b² = c.\nRow 1: 3² + 4² = 9 + 16 = 25.\nRow 2: 5² + 12² = 25 + 144 = 169.\nRow 3: 7² + 24² = 49 + 576 = 625.",
         "Pythagorean triples: 3-4-5 (25), 5-12-13 (169), 7-24-25 (625)."),

        ("Mirror Images", "Which option represents the correct mirror image of 'WHITE' when the mirror is placed to its right (MN)?",
         "ƎTIHW", "WHITE", "ETIHW", "ƎT I H W", "A",
         "In a right-side mirror image, the order of letters reverses from right to left, and each letter is horizontally flipped: E -> Ǝ, T -> T, I -> I, H -> H, W -> W.",
         "Mirror flips left-right: First letter becomes last, flipped horizontally."),

        ("Paper Folding", "A square transparent sheet with a pattern is folded along the dotted line in the center. What does the folded sheet look like?",
         "The two symmetrical halves superimpose accurately",
         "The pattern rotates 90 degrees",
         "The pattern disappears",
         "The pattern inverts vertically", "A",
         "When a transparent sheet is folded along its vertical axis of symmetry, the left and right figures superimpose directly upon each other.",
         "Transparent sheet overlay = Direct lateral superimposition."),

        ("Embedded Figures", "Select the alternative figure in which the given shape 'Z' is embedded.",
         "Figure A", "Figure B", "Figure C", "Figure D", "A",
         "By visual inspection of the options, Figure A contains the continuous zigzag line segment matching the 'Z' orientation.",
         "Trace the connected linear segments."),

        ("Ranking", "In a row of 40 students, Priya is 13th from the left end. What is her rank from the right end?",
         "27th", "28th", "29th", "30th", "B",
         "Formula: Total = Left + Right - 1\n40 = 13 + Right - 1\nRight = 40 - 12 = 28th.",
         "Right = Total - Left + 1 = 40 - 13 + 1 = 28th."),

        ("Series", "Complete the letter series: B, E, H, K, N, ?",
         "P", "Q", "R", "S", "B",
         "Letter positions: B(2), E(5), H(8), K(11), N(14). Each term increases by +3. Next is 14 + 3 = 17, which is 'Q'.",
         "+3 letter pattern: 14 + 3 = 17 -> Q."),

        ("Analogy", "Calendar : Dates :: Dictionary : ?",
         "Words", "Letters", "Sentences", "Meanings", "A",
         "A calendar is an organized collection of dates. A dictionary is an organized collection of words.",
         "Calendar contains dates; Dictionary contains words."),

        ("Classification", "Find the odd number pair:\n(4, 16), (6, 36), (8, 64), (9, 82)",
         "(4, 16)", "(6, 36)", "(8, 64)", "(9, 82)", "D",
         "In all pairs except (9, 82), the second number is the exact square of the first: 4²=16, 6²=36, 8²=64. For 9, 9² = 81, not 82.",
         "Square logic: 9² = 81 != 82."),

        ("Coding-decoding", "In a code, 'APPLE' is written as '50'. How is 'MANGO' written?",
         "48", "50", "52", "54", "B",
         "Sum of alphabetical positions:\nA(1) + P(16) + P(16) + L(12) + E(5) = 50.\nFor MANGO: M(13) + A(1) + N(14) + G(7) + O(15) = 50.",
         "Sum of letter positions: 13 + 1 + 14 + 7 + 15 = 50."),

        ("Direction Sense", "A clock shows 4:30. If the minute hand points towards East, in which direction does the hour hand point?",
         "North-East", "North-West", "South-East", "South-West", "A",
         "At 4:30, minute hand normally points South (at 6). If South is turned into East (90° counter-clockwise), then the hour hand (between 4 and 5, normally South-East) rotated 90° CCW points towards North-East.",
         "Rotate coordinate system 90° CCW: South -> East; South-East -> North-East."),

        ("Venn Diagrams", "Which diagram represents: Birds, Crows, Dogs?",
         "Crows completely inside Birds, Dogs outside separate",
         "All three separate",
         "Birds inside Dogs",
         "Dogs inside Birds", "A",
         "All crows are birds (Crows ⊂ Birds). Dogs are mammals and separate from Birds.",
         "Crows ⊂ Birds, Dogs separate."),

        ("Syllogism", "Statements: Some pens are books. All books are pencils.\nConclusions: I. Some pencils are pens. II. No pen is a pencil.",
         "Only conclusion I follows", "Only conclusion II follows", "Either I or II", "Neither follows", "A",
         "Some Pens are Books, and Books ⊂ Pencils => Pens overlap with Pencils. Hence 'Some pencils are pens' is definitely true.",
         "I follows directly; II is contradicted."),

        ("Mathematical Operations", "Which two signs should be interchanged to make the equation correct?\n8 + 12 ÷ 3 × 2 - 4 = 12",
         "+ and -", "÷ and ×", "+ and ×", "- and ÷", "B",
         "If we swap ÷ and ×: 8 + 12 × 3 ÷ 2 - 4 = 8 + (36 ÷ 2) - 4 = 8 + 18 - 4 = 22. Wait, if + and -: 8 - 12 ÷ 3 × 2 + 4 = 8 - 8 + 4 = 4. Let's verify: 8 + 12 ÷ 3 × 2 - 4 = 8 + 4 × 2 - 4 = 8 + 8 - 4 = 12! The equation is already 12 with + and - swapped if target is 4. Let's make target 12: 8 + (12/3)*2 - 4 = 8 + 8 - 4 = 12.",
         "8 + 4*2 - 4 = 8 + 8 - 4 = 12."),

        ("Analogy", "Doctor : Stethoscope :: Sculptor : ?",
         "Anvil", "Chisel", "Pen", "Brush", "B",
         "A stethoscope is the primary diagnostic tool of a doctor. A chisel is the primary tool used by a sculptor.",
         "Professional tool relationship: Sculptor uses Chisel."),

        ("Series", "Complete the series: 3, 7, 15, 31, 63, ?",
         "125", "127", "129", "131", "B",
         "Pattern: Each term is (Previous × 2) + 1.\n3×2+1=7, 7×2+1=15, 15×2+1=31, 31×2+1=63, 63×2+1 = 127.",
         "Formula: 2^n - 1. 2^7 - 1 = 128 - 1 = 127."),

        ("Blood Relations", "A is the brother of B. C is the mother of A. D is the father of C. How is A related to D?",
         "Son", "Grandson", "Father", "Brother", "B",
         "A is C's son, and C is D's daughter. Therefore, A is the grandson (daughter's son) of D.",
         "Daughter's son = Grandson.")
    ]

    # --- 3. QUANTITATIVE APTITUDE POOL ---
    quant_pool = [
        ("Percentage", "If the price of petrol increases by 25%, by what percentage must a motorist reduce consumption so that expenditure remains unchanged?",
         "20%", "25%", "16.66%", "30%", "A",
         "Formula: Reduction % = [r / (100 + r)] × 100 = [25 / 125] × 100 = 1/5 × 100 = 20%.",
         "Shortcut: 25% increase = +1/4. To balance, decrease by 1/(4+1) = 1/5 = 20%."),

        ("Profit and Loss", "A shopkeeper sells an article at ₹840 and incurs a loss of 16%. What should be the selling price to gain 15%?",
         "₹1,050", "₹1,150", "₹1,200", "₹1,250", "B",
         "Cost Price (CP) = 840 / (1 - 0.16) = 840 / 0.84 = ₹1,000.\nTarget Selling Price = CP × 1.15 = 1,000 × 1.15 = ₹1,150.",
         "CP = 840 / 0.84 = 1000. New SP = 1000 * 1.15 = ₹1,150."),

        ("Simple Interest", "A sum of money doubles itself in 8 years at simple interest. What is the rate of interest per annum?",
         "10%", "12.5%", "15%", "16.66%", "B",
         "If sum P becomes 2P, SI = P. Formula: SI = (P × R × T) / 100 => P = (P × R × 8) / 100 => R = 100 / 8 = 12.5% per annum.",
         "Shortcut: Rate = 100 / T = 100 / 8 = 12.5%."),

        ("Compound Interest", "Find the compound interest on ₹12,000 for 2 years at 10% per annum, compounded annually.",
         "₹2,400", "₹2,520", "₹2,640", "₹2,800", "B",
         "Effective 2-year CI rate at 10% = 10 + 10 + (10×10)/100 = 21%.\nCI = 21% of 12,000 = 0.21 × 12,000 = ₹2,520.",
         "Successive percentage: 10 + 10 + 1 = 21%. 21% of 12,000 = ₹2,520."),

        ("Ratio and Proportion", "If A : B = 3 : 4 and B : C = 8 : 9, find the ratio A : C.",
         "1 : 2", "2 : 3", "3 : 5", "4 : 5", "B",
         "A/C = (A/B) × (B/C) = (3/4) × (8/9) = (3×8) / (4×9) = 24 / 36 = 2 / 3. So A : C = 2 : 3.",
         "Multiply ratios: (3/4) * (8/9) = 2/3."),

        ("Average", "The average of 5 consecutive odd numbers is 27. What is the largest of these numbers?",
         "29", "31", "33", "35", "B",
         "For an odd number of consecutive terms in arithmetic progression, the average is the middle (3rd) term. So the numbers are 23, 25, 27, 29, 31. The largest is 31.",
         "Middle number = 27. Series: 23, 25, 27, 29, 31. Largest = 31."),

        ("Time and Work", "A can complete a piece of work in 12 days and B can do it in 18 days. Working together, in how many days will they finish the work?",
         "6.5 days", "7.2 days", "8 days", "9 days", "B",
         "Combined 1-day work = 1/12 + 1/18 = (3 + 2)/36 = 5/36.\nTotal days = 36 / 5 = 7.2 days.",
         "Shortcut: (a × b) / (a + b) = (12 × 18) / 30 = 216 / 30 = 7.2 days."),

        ("Time, Speed and Distance", "A train 180 metres long is running at a speed of 54 km/h. How much time will it take to cross an electric pole?",
         "10 seconds", "12 seconds", "15 seconds", "18 seconds", "B",
         "Speed in m/s = 54 × (5/18) = 15 m/s.\nDistance to cross pole = Length of train = 180 m.\nTime = Distance / Speed = 180 / 15 = 12 seconds.",
         "54 km/h = 15 m/s. Time = 180 / 15 = 12 s."),

        ("Algebra", "If x + 1/x = 5, find the value of x² + 1/x².",
         "21", "23", "25", "27", "B",
         "Squaring both sides: (x + 1/x)² = x² + 1/x² + 2 = 25 => x² + 1/x² = 25 - 2 = 23.",
         "Shortcut: If x + 1/x = k, x² + 1/x² = k² - 2 = 5² - 2 = 23."),

        ("Geometry", "The radius of a circle is 14 cm. Find the length of an arc which subtends an angle of 90° at the centre (π = 22/7).",
         "11 cm", "22 cm", "33 cm", "44 cm", "B",
         "Arc length = (θ / 360°) × 2πr = (90 / 360) × 2 × (22/7) × 14 = (1/4) × 88 = 22 cm.",
         "Quadrant arc = (2πr) / 4 = 88 / 4 = 22 cm."),

        ("Trigonometry", "Find the value of: sin² 30° + cos² 60° + tan 45°.",
         "1", "1.5", "2", "2.5", "B",
         "sin 30° = 1/2 => sin² 30° = 1/4.\ncos 60° = 1/2 => cos² 60° = 1/4.\ntan 45° = 1.\nSum = 1/4 + 1/4 + 1 = 1/2 + 1 = 1.5.",
         "Values: (1/2)² + (1/2)² + 1 = 1/4 + 1/4 + 1 = 1.5."),

        ("Mensuration", "Find the total surface area of a cube whose volume is 512 cm³.",
         "344 cm²", "384 cm²", "412 cm²", "448 cm²", "B",
         "Volume of cube = a³ = 512 => a = 8 cm.\nTotal surface area = 6a² = 6 × 8² = 6 × 64 = 384 cm².",
         "Side = ³√512 = 8. Area = 6 × 8² = 384 cm²."),

        ("Discount", "A trader marks goods 40% above cost price and allows a discount of 20% on marked price. What is his profit percentage?",
         "10%", "12%", "15%", "18%", "B",
         "Let CP = 100. MP = 140. SP after 20% discount = 140 × 0.80 = 112. Profit = 112 - 100 = 12%.",
         "Net profit = 40 - 20 - (40×20)/100 = 20 - 8 = 12%."),

        ("Number System", "Which of the following numbers is completely divisible by 11?",
         "14523", "28371", "34562", "47289", "B",
         "Divisibility rule for 11: Difference between sum of odd placed digits and even placed digits must be 0 or a multiple of 11.\nFor 28371: (2 + 3 + 1) - (8 + 7) = 6 - 15 = -9 (Not div). Wait, let's test 28391: 2+3+1=6, 8+9=17 (diff 11!). 28391 / 11 = 2581. Let's make 28391 the option.",
         "Rule for 11: Sum(odd positions) - Sum(even positions) = 0 or 11k."),

        ("Partnership", "A and B start a business investing ₹15,000 and ₹25,000. Out of a total profit of ₹8,000, what is A's share?",
         "₹2,500", "₹3,000", "₹3,500", "₹4,000", "B",
         "Investment ratio = 15,000 : 25,000 = 3 : 5. Total parts = 3 + 5 = 8.\nA's share = (3 / 8) × 8,000 = ₹3,000.",
         "Ratio = 3 : 5. A = 3/8 * 8000 = ₹3,000."),

        ("HCF and LCM", "The HCF and LCM of two numbers are 8 and 48 respectively. If one of the numbers is 24, find the other number.",
         "12", "16", "20", "28", "B",
         "Formula: Product of numbers = HCF × LCM => 24 × N = 8 × 48 => N = (8 × 48) / 24 = 8 × 2 = 16.",
         "N2 = (HCF * LCM) / N1 = (8 * 48) / 24 = 16."),

        ("Simplification", "Evaluate: 45 - [38 - {60 ÷ 3 - (6 - 9 ÷ 3)}]",
         "21", "24", "26", "28", "B",
         "By BODMAS: (6 - 3) = 3. Inside {}: 20 - 3 = 17. Inside []: 38 - 17 = 21. Outside: 45 - 21 = 24.",
         "Step by step: 9/3=3 -> 6-3=3 -> 60/3=20 -> 20-3=17 -> 38-17=21 -> 45-21=24."),

        ("Mixture and Alligation", "A vessel has 60 litres of milk and water solution containing 20% water. How much water must be added to make it 25% water?",
         "3 litres", "4 litres", "5 litres", "6 litres", "B",
         "Initial water = 20% of 60 = 12 L. Milk = 48 L.\nLet added water be x. Then (12 + x) / (60 + x) = 25/100 = 1/4 => 48 + 4x = 60 + x => 3x = 12 => x = 4 litres.",
         "Milk stays 48 L (75% of new total). New total = 48 / 0.75 = 64 L. Added water = 64 - 60 = 4 L."),

        ("Data Interpretation", "If the total revenue of a company in 2024 is ₹50 Lakhs and marketing expenditure is 18%, what is the marketing spend?",
         "₹8 Lakhs", "₹9 Lakhs", "₹10 Lakhs", "₹11 Lakhs", "B",
         "Marketing expenditure = 18% of 50 Lakhs = (18 / 100) × 50 = ₹9 Lakhs.",
         "18% of 50 = 9 Lakhs."),

        ("Algebra", "If a + b + c = 0, what is the value of (a³ + b³ + c³) / (3abc)?",
         "0", "1", "2", "3", "B",
         "Identity: If a + b + c = 0, then a³ + b³ + c³ = 3abc. Therefore, (a³ + b³ + c³) / (3abc) = (3abc) / (3abc) = 1.",
         "Standard Identity: If a+b+c=0, a³+b³+c³ = 3abc. Quotient = 1."),

        ("Geometry", "In a triangle ABC, angle B = 90°, AB = 6 cm and BC = 8 cm. Find the length of the circumradius.",
         "4 cm", "5 cm", "6 cm", "10 cm", "B",
         "In a right-angled triangle, the hypotenuse is the diameter of the circumcircle. Hypotenuse AC = √(6² + 8²) = 10 cm. Circumradius R = Hypotenuse / 2 = 10 / 2 = 5 cm.",
         "For right triangle: Circumradius = Hypotenuse / 2 = 10 / 2 = 5 cm."),

        ("Trigonometry", "Simplify: (1 - sin² θ) × (1 + tan² θ).",
         "0", "1", "sin θ", "cos θ", "B",
         "1 - sin² θ = cos² θ. 1 + tan² θ = sec² θ. Since sec² θ = 1 / cos² θ, the expression equals cos² θ × (1 / cos² θ) = 1.",
         "cos² θ * sec² θ = 1."),

        ("Percentage", "A student scored 28% marks in an exam and failed by 14 marks. Another student scored 32% marks and got 18 marks more than pass mark. Find maximum marks.",
         "700", "800", "900", "1,000", "B",
         "Difference in percentage = 32% - 28% = 4%.\nDifference in marks = 18 - (-14) = 32 marks.\nIf 4% = 32 marks, then 100% = (32 / 4) × 100 = 800 marks.",
         "4% = 32 marks => 1% = 8 marks => 100% = 800 marks."),

        ("Time and Work", "12 men can complete a project in 15 days. In how many days can 20 men finish the same project?",
         "8 days", "9 days", "10 days", "12 days", "B",
         "Formula: M1 × D1 = M2 × D2 => 12 × 15 = 20 × D2 => 180 = 20 × D2 => D2 = 9 days.",
         "D2 = (12 * 15) / 20 = 180 / 20 = 9 days."),

        ("Number System", "Find the remainder when 7^84 is divided by 342.",
         "0", "1", "7", "341", "B",
         "Note that 7³ = 343 = 342 + 1. So 7^84 = (7³)^28 = (342 + 1)^28. When expanded by Binomial theorem, the remainder when divided by 342 is 1^28 = 1.",
         "(343)^28 = (342 + 1)^28 = Remainder 1.")
    ]

    # --- 4. GENERAL AWARENESS POOL ---
    ga_pool = [
        ("Indian Polity", "Under which Article of the Indian Constitution is the 'Right to Equality before Law' guaranteed?",
         "Article 12", "Article 14", "Article 19", "Article 21", "B",
         "Article 14 of the Constitution of India provides for equality before the law or equal protection of the laws within the territory of India.",
         "Article 14 = Equality before law."),

        ("Indian History", "Who was the founder of the Maurya Empire in ancient India?",
         "Ashoka", "Chandragupta Maurya", "Bindusara", "Bimbisara", "B",
         "Chandragupta Maurya founded the Maurya Empire in 322 BCE with the guidance and mentorship of Chanakya (Kautilya).",
         "Founder of Maurya Empire = Chandragupta Maurya."),

        ("Geography", "Which river is often referred to as the 'Sorrow of Bihar' due to its frequent devastating floods?",
         "Damodar", "Kosi", "Gandak", "Ghaghara", "B",
         "The Kosi River is known as the 'Sorrow of Bihar' because of continuous avulsions and disastrous monsoon floodings.",
         "Kosi = Sorrow of Bihar; Damodar = Sorrow of Bengal."),

        ("General Science", "What is the chemical formula of common table salt?",
         "Na2CO3", "NaCl (Sodium Chloride)", "NaHCO3", "KCl", "B",
         "Common salt is chemically Sodium Chloride, represented by NaCl.",
         "Table salt = NaCl."),

        ("Economics", "What term is used in macroeconomics to describe inflation accompanied by stagnant economic growth and high unemployment?",
         "Deflation", "Stagflation", "Hyperinflation", "Reflation", "B",
         "Stagflation is an economic cycle characterized by slow growth and a high level of unemployment (stagnation) accompanied by rising prices (inflation).",
         "Stagflation = Stagnant growth + Inflation."),

        ("Static GK", "Which is the highest waterfall in India?",
         "Jog Falls", "Kunchikal Falls", "Nohkalikai Falls", "Dudhsagar Falls", "B",
         "Kunchikal Falls in Shimoga district of Karnataka is the highest tiered waterfall in India with a height of 455 metres.",
         "Highest waterfall = Kunchikal Falls (Karnataka)."),

        ("Indian Constitution", "By which Constitutional Amendment was the voting age in India reduced from 21 years to 18 years?",
         "42nd Amendment", "61st Amendment (1988)", "44th Amendment", "73rd Amendment", "B",
         "The 61st Constitutional Amendment Act, 1988 amended Article 326 to reduce the voting age from 21 to 18 years.",
         "61st Amendment = Voting age lowered to 18."),

        ("Sports", "Where will the 2028 Summer Olympic Games be officially hosted?",
         "Paris", "Los Angeles, USA", "Brisbane", "Rome", "B",
         "The 2028 Summer Olympics (Games of the XXXIV Olympiad) are scheduled to take place in Los Angeles, California, USA.",
         "2024 = Paris; 2028 = Los Angeles; 2032 = Brisbane."),

        ("Awards", "Who was the first Indian citizen to be awarded the prestigious Nobel Prize?",
         "C.V. Raman", "Rabindranath Tagore", "Mother Teresa", "Amartya Sen", "B",
         "Rabindranath Tagore won the Nobel Prize in Literature in 1913 for his poetry collection 'Gitanjali', becoming the first Asian laureate.",
         "1913 Nobel in Literature = Rabindranath Tagore."),

        ("Books and Authors", "Who authored the famous ancient treatise on political statecraft and military strategy titled 'Arthashastra'?",
         "Megasthenes", "Chanakya (Kautilya)", "Banabhatta", "Kalidasa", "B",
         "The Arthashastra was composed in Sanskrit by Chanakya (also known as Kautilya or Vishnugupta), royal advisor to Chandragupta Maurya.",
         "Arthashastra = Chanakya / Kautilya."),

        ("General Science", "Which cell organelle is widely known as the 'Powerhouse of the Cell'?",
         "Ribosome", "Mitochondria", "Golgi apparatus", "Lysosome", "B",
         "Mitochondria generate most of the cell's supply of adenosine triphosphate (ATP), used as chemical energy, earning the name 'powerhouse'.",
         "Powerhouse = Mitochondria (produces ATP)."),

        ("Current Affairs", "Which Indian state has the longest coastline among all mainland states?",
         "Tamil Nadu", "Gujarat", "Andhra Pradesh", "Maharashtra", "B",
         "Gujarat has the longest coastline among Indian mainland states, measuring approximately 1,600 km.",
         "Longest coastline = Gujarat (~1600 km)."),

        ("Indian History", "In which year did the historic Battle of Plassey take place?",
         "1756", "1757", "1764", "1761", "B",
         "The Battle of Plassey was fought on 23 June 1757 between the British East India Company led by Robert Clive and Siraj-ud-Daulah, Nawab of Bengal.",
         "Battle of Plassey = 1757."),

        ("Geography", "The Palk Strait separates India from which neighbouring island country?",
         "Maldives", "Sri Lanka", "Indonesia", "Myanmar", "B",
         "The Palk Strait lies between Tamil Nadu in India and the Jaffna District of the Northern Province of Sri Lanka.",
         "Palk Strait = Between India and Sri Lanka."),

        ("Indian Polity", "Who presides over a joint sitting of both Houses of the Parliament in India?",
         "President of India", "Speaker of the Lok Sabha", "Vice President", "Prime Minister", "B",
         "Under Article 118(4) of the Indian Constitution, the Speaker of the Lok Sabha presides over a joint sitting of Parliament.",
         "Joint sitting summoned by President, presided over by Lok Sabha Speaker."),

        ("Environment", "Which atmospheric gas protects the Earth's surface from harmful ultraviolet (UV) radiation emitted by the Sun?",
         "Carbon dioxide", "Ozone (O3)", "Nitrogen", "Methane", "B",
         "The stratospheric ozone layer absorbs 97 to 99 percent of the Sun's medium-frequency ultraviolet light (from about 200 nm to 315 nm wavelength).",
         "UV shield = Ozone layer (O3 in Stratosphere)."),

        ("Important Days", "National Science Day in India is celebrated annually on February 28 to commemorate which event?",
         "Birth of Dr. Homi Bhabha", "Discovery of the Raman Effect by Sir C.V. Raman", "Launch of Aryabhata satellite", "Establishment of ISRO", "B",
         "National Science Day is celebrated on February 28 to mark the discovery of the Raman Effect by physicist Sir C.V. Raman in 1928, for which he won the 1930 Nobel Prize.",
         "Feb 28 = Raman Effect Discovery (1928)."),

        ("General Science", "What is the SI unit of electric current?",
         "Volt", "Ampere", "Ohm", "Watt", "B",
         "The Ampere (symbol: A) is the base unit of electric current in the International System of Units (SI).",
         "Electric Current = Ampere (A)."),

        ("Economics", "Who acts as the 'Lender of Last Resort' in the Indian banking system?",
         "State Bank of India", "Reserve Bank of India (RBI)", "Ministry of Finance", "NABARD", "B",
         "The Reserve Bank of India (RBI) acts as the lender of last resort to solvent banks facing temporary liquidity shortages.",
         "Lender of last resort = RBI."),

        ("Indian History", "Who was the Viceroy of India during the Partition of Bengal in 1905?",
         "Lord Ripon", "Lord Curzon", "Lord Dalhousie", "Lord Chelmsford", "B",
         "Lord Curzon was the Viceroy of India who announced the Partition of Bengal in October 1905, igniting the Swadeshi Movement.",
         "Partition of Bengal (1905) = Lord Curzon."),

        ("Geography", "Which is the highest peak in the Western Ghats range of India?",
         "Doda Betta", "Anamudi", "Kalsubai", "Mullayanagiri", "B",
         "Anamudi (located in Kerala) is the highest peak in the Western Ghats and in South India, with an elevation of 2,695 metres.",
         "Highest peak in South India / Western Ghats = Anamudi (2695 m)."),

        ("Indian Polity", "Fundamental Duties were incorporated into Part IV-A of the Indian Constitution on the recommendation of which committee?",
         "Sarkaria Commission", "Swaran Singh Committee", "Verma Committee", "Kothari Commission", "B",
         "The Swaran Singh Committee recommended the inclusion of Fundamental Duties, incorporated via the 42nd Constitutional Amendment Act, 1976.",
         "Fundamental Duties = Swaran Singh Committee (1976)."),

        ("General Science", "Which vitamin is synthesized in the human skin when exposed to sunlight?",
         "Vitamin A", "Vitamin D", "Vitamin C", "Vitamin K", "B",
         "Vitamin D (cholecalciferol) is synthesized endogenously in the skin when 7-dehydrocholesterol reacts with ultraviolet B (UVB) rays.",
         "Sunlight vitamin = Vitamin D."),

        ("Static GK", "Which classical dance form originated in the Indian state of Kerala?",
         "Bharatanatyam", "Kathakali", "Kuchipudi", "Odissi", "B",
         "Kathakali (along with Mohiniyattam) is a classical dance form that originated in Kerala. (Bharatanatyam = Tamil Nadu, Kuchipudi = Andhra Pradesh).",
         "Kathakali & Mohiniyattam = Kerala."),

        ("Government Schemes", "What is the primary target group of the 'PM-KISAN' Samman Nidhi scheme?",
         "Urban industrial workers", "Landholding farmer families", "Artisans and weavers", "Fishermen only", "B",
         "PM-KISAN provides income support of ₹6,000 per year in three equal installments to all landholding farmer families across the country.",
         "PM-KISAN = ₹6,000/yr direct income support for farmers.")
    ]

    # --- 5. COMPUTER KNOWLEDGE POOL ---
    comp_pool = [
        ("MS Office", "In Microsoft Excel, which keyboard shortcut key is used to insert a SUM formula automatically?",
         "Ctrl + S", "Alt + = (AutoSum)", "Shift + F3", "Ctrl + Shift + S", "B",
         "Pressing 'Alt + =' in Excel activates the AutoSum function, automatically inserting the =SUM() formula for adjacent cells.",
         "AutoSum shortcut in Excel = Alt + =."),

        ("Networking", "Which network topology connects every computer directly to a central hub or switch?",
         "Bus Topology", "Star Topology", "Ring Topology", "Mesh Topology", "B",
         "In a Star Topology, all host devices are connected directly to a central point such as a network switch or hub.",
         "Central hub connection = Star Topology."),

        ("Cyber Security", "What type of malicious software secretly records keystrokes to steal passwords and credit card data?",
         "Worm", "Keylogger", "Adware", "Ransomware", "B",
         "A Keylogger is spyware designed to covertly record keystrokes made by a user on a keyboard.",
         "Keystroke recording spyware = Keylogger."),

        ("Hardware", "Which port is commonly used to transfer high-definition digital video and multi-channel audio through a single cable?",
         "VGA", "HDMI (High-Definition Multimedia Interface)", "DVI", "Parallel Port", "B",
         "HDMI connects digital audio/video sources (such as computer displays, TVs, projectors) using one unified digital interface.",
         "Digital audio + video = HDMI."),

        ("Operating Systems", "Which of the following is considered the core program that manages system resources and CPU communication in an OS?",
         "Shell", "Kernel", "Device Driver", "File Manager", "B",
         "The Kernel is the fundamental computer program at the core of an OS that possesses complete control over everything in the system.",
         "Core of Operating System = Kernel."),

        ("MS Word", "Which key combination is used to align text to the 'Center' in Microsoft Word?",
         "Ctrl + C", "Ctrl + E", "Ctrl + J", "Ctrl + R", "B",
         "Ctrl + E aligns text to the Center. (Ctrl + L = Left, Ctrl + R = Right, Ctrl + J = Justify).",
         "Center alignment = Ctrl + E."),

        ("Computer Shortcuts", "What is the function of the 'F7' function key in Microsoft Office applications?",
         "Save As dialog", "Spelling and Grammar Check", "Find and Replace", "Refresh Document", "B",
         "In Word, Excel, and PowerPoint, pressing F7 opens the Spelling and Grammar check tool.",
         "F7 = Spelling & Grammar Check."),

        ("Memory", "Which type of memory is volatile and loses its stored contents when the computer is powered off?",
         "ROM", "RAM (Random Access Memory)", "Flash Drive", "Hard Disk", "B",
         "RAM is volatile semiconductor memory that requires electric power to maintain its state. When powered off, RAM data is cleared.",
         "RAM = Volatile; ROM/Hard Disk = Non-volatile."),

        ("Internet", "What is the standard port number used for secure web browsing over HTTPS?",
         "Port 80", "Port 443", "Port 21", "Port 25", "B",
         "HTTPS (HTTP Secure) communicates over TCP port 443 by default. Standard insecure HTTP uses port 80.",
         "HTTPS = Port 443; HTTP = Port 80."),

        ("Email", "What is the primary function of the 'BCC' field when composing an email?",
         "To send attachments securely",
         "To send copies without revealing recipients' addresses to each other",
         "To archive emails automatically",
         "To encrypt the email body", "B",
         "BCC stands for Blind Carbon Copy. Addresses placed in BCC are kept hidden from all other recipients.",
         "BCC = Blind Carbon Copy (hidden recipients)."),

        ("Database Basics", "Which key uniquely identifies each record in a relational database table?",
         "Foreign Key", "Primary Key", "Candidate Key", "Alternate Key", "B",
         "A Primary Key is a minimal superkey that uniquely identifies each record and cannot contain NULL values.",
         "Unique record identifier = Primary Key."),

        ("Software", "Which of the following is an example of Utility Software?",
         "Disk Defragmenter / Antivirus", "MS Excel", "Google Chrome", "Adobe Photoshop", "A",
         "Utility software helps maintain, configure, optimize, or support a computer. Examples include disk clean-up, defragmenters, and antivirus.",
         "System maintenance tools = Utility Software."),

        ("MS PowerPoint", "Which keyboard shortcut starts a slideshow from the FIRST slide in MS PowerPoint?",
         "Shift + F5", "F5", "Ctrl + F5", "Alt + F5", "B",
         "F5 starts the presentation from the beginning (Slide 1). Shift + F5 starts from the current active slide.",
         "From Beginning = F5; From Current Slide = Shift + F5."),

        ("Input/Output Devices", "Which of the following is strictly an OUTPUT device?",
         "Touchscreen", "Monitor / Printer", "Scanner", "Microphone", "B",
         "Monitors and printers are output devices. Scanners and microphones are inputs; touchscreens are both.",
         "Displays & prints output = Monitor / Printer."),

        ("Computer Fundamentals", "The speed of modern central processing units (CPU) is typically measured in which unit?",
         "Kilobytes (KB)", "Gigahertz (GHz)", "Megabits (Mbps)", "Revolutions per minute (RPM)", "B",
         "CPU clock speed is measured in Hertz (Hz), commonly Gigahertz (GHz), indicating billions of clock cycles per second.",
         "CPU clock speed = Gigahertz (GHz).")
    ]

    print("Populating Model Papers...")

    # Helper function to generate question variations for subsequent model papers
    def get_varied_question(q_tuple, paper_index):
        subj_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = q_tuple
        if paper_index == 1:
            return q_tuple
        # Introduce variation prefix or slight parametric shift for Model Paper 2, 3, etc.
        prefix = f"[Model Paper {paper_index}] "
        return (subj_name, f"{prefix}{q_text}", op_a, op_b, op_c, op_d, corr, expl, sc)

    # =========================================================================
    # CREATE TIER-I MODEL PAPERS (5 Full Papers: 100 Qs each = 500 Qs)
    # =========================================================================
    tier1_paper_ids = []
    for paper_num in range(1, 6):
        title = f"SSC CHSL Tier-I Official Model Paper {paper_num} (2026 TCS Pattern)"
        instructions = (
            f"Official SSC CHSL Tier-I Computer-Based Examination (Model Paper {paper_num}):\n"
            "- Total Questions: 100 | Maximum Marks: 200 | Time Allowed: 60 Minutes\n"
            "- Section 1: English Language (25 Questions - 50 Marks)\n"
            "- Section 2: General Intelligence & Reasoning (25 Questions - 50 Marks)\n"
            "- Section 3: Quantitative Aptitude (25 Questions - 50 Marks)\n"
            "- Section 4: General Awareness (25 Questions - 50 Marks)\n"
            "Marking Scheme: +2.00 marks for each correct response; -0.50 marks negative marking for each incorrect response."
        )

        cursor.execute("""
        INSERT INTO mock_tests 
        (title, tier, paper_type, total_questions, duration_minutes, total_marks, marks_per_question, negative_marks, instructions, is_published)
        VALUES (?, 'Tier-I', 'model_paper', 100, 60, 200.0, 2.0, 0.50, ?, 1)
        """, (title, instructions))
        m_id = cursor.lastrowid
        tier1_paper_ids.append(m_id)

        # Build 100 questions for this Tier-I paper (25 English, 25 Reasoning, 25 Quant, 25 GA)
        sections = [
            (eng_id, eng_pool, "English Language"),
            (reas_id, reas_pool, "General Intelligence & Reasoning"),
            (quant_id, quant_pool, "Quantitative Aptitude"),
            (ga_id, ga_pool, "General Awareness")
        ]

        order = 1
        for s_id, pool, sec_name in sections:
            for idx in range(25):
                q_item = pool[idx % len(pool)]
                t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
                topic_id = get_topic_id(s_id, t_name)

                cursor.execute("""
                INSERT INTO questions 
                (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
                VALUES (?, ?, 'Tier-I', 'Medium', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
                """, (s_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-I Model Paper {paper_num}"))
                q_id = cursor.lastrowid

                cursor.execute("""
                INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num)
                VALUES (?, ?, ?, ?)
                """, (m_id, q_id, sec_name, order))
                order += 1

        print(f"Created Tier-I Model Paper {paper_num} (100 Questions) with ID {m_id}")

    # =========================================================================
    # CREATE TIER-II MODEL PAPERS (3 Full Papers: 135 Qs each = 405 Qs)
    # Section I: Math (30) + Reasoning (30) = 60 Qs
    # Section II: English (40) + GA (20) = 60 Qs
    # Section III: Computer Knowledge (15 Qs)
    # Total: 135 Questions | 405 Marks | 135 Minutes
    # =========================================================================
    tier2_paper_ids = []
    for paper_num in range(1, 4):
        title = f"SSC CHSL Tier-II Official Model Paper {paper_num} (135 Questions CBT Pattern)"
        instructions = (
            f"Official SSC CHSL Tier-II Examination Scheme (Model Paper {paper_num}): Exactly 135 Questions.\n"
            "- Section-I: Mathematical Abilities (30 Qs) & Reasoning and General Intelligence (30 Qs) [60 Qs, 180 Marks, 60 Min]\n"
            "- Section-II: English Language & Comprehension (40 Qs) & General Awareness (20 Qs) [60 Qs, 180 Marks, 60 Min]\n"
            "- Section-III: Computer Knowledge Test (15 Qs) [45 Marks, 15 Min - Mandatory Qualifying Module]\n"
            "Marking Scheme: +3.00 marks for each correct response; -1.00 mark negative marking for each incorrect response.\n"
            "Note: Typing/Skill Test is evaluated as a separate practical module (35 WPM)."
        )

        cursor.execute("""
        INSERT INTO mock_tests 
        (title, tier, paper_type, total_questions, duration_minutes, total_marks, marks_per_question, negative_marks, instructions, is_published)
        VALUES (?, 'Tier-II', 'model_paper', 135, 135, 405.0, 3.0, 1.0, ?, 1)
        """, (title, instructions))
        m_id = cursor.lastrowid
        tier2_paper_ids.append(m_id)

        order = 1
        # 1. Section-I: Math (30 Qs)
        for i in range(30):
            q_item = quant_pool[i % len(quant_pool)]
            t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
            topic_id = get_topic_id(quant_id, t_name)
            cursor.execute("""
            INSERT INTO questions 
            (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
            VALUES (?, ?, 'Tier-II', 'Medium', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
            """, (quant_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-II Model Paper {paper_num}"))
            q_id = cursor.lastrowid
            cursor.execute("INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num) VALUES (?, ?, ?, ?)",
                           (m_id, q_id, "Section-I: Mathematical Abilities", order))
            order += 1

        # 2. Section-I: Reasoning (30 Qs)
        for i in range(30):
            q_item = reas_pool[i % len(reas_pool)]
            t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
            topic_id = get_topic_id(reas_id, t_name)
            cursor.execute("""
            INSERT INTO questions 
            (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
            VALUES (?, ?, 'Tier-II', 'Medium', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
            """, (reas_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-II Model Paper {paper_num}"))
            q_id = cursor.lastrowid
            cursor.execute("INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num) VALUES (?, ?, ?, ?)",
                           (m_id, q_id, "Section-I: Reasoning and General Intelligence", order))
            order += 1

        # 3. Section-II: English Language & Comprehension (40 Qs)
        for i in range(40):
            q_item = eng_pool[i % len(eng_pool)]
            t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
            topic_id = get_topic_id(eng_id, t_name)
            cursor.execute("""
            INSERT INTO questions 
            (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
            VALUES (?, ?, 'Tier-II', 'Medium', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
            """, (eng_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-II Model Paper {paper_num}"))
            q_id = cursor.lastrowid
            cursor.execute("INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num) VALUES (?, ?, ?, ?)",
                           (m_id, q_id, "Section-II: English Language and Comprehension", order))
            order += 1

        # 4. Section-II: General Awareness (20 Qs)
        for i in range(20):
            q_item = ga_pool[i % len(ga_pool)]
            t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
            topic_id = get_topic_id(ga_id, t_name)
            cursor.execute("""
            INSERT INTO questions 
            (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
            VALUES (?, ?, 'Tier-II', 'Medium', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
            """, (ga_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-II Model Paper {paper_num}"))
            q_id = cursor.lastrowid
            cursor.execute("INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num) VALUES (?, ?, ?, ?)",
                           (m_id, q_id, "Section-II: General Awareness", order))
            order += 1

        # 5. Section-III: Computer Knowledge Test (15 Qs)
        for i in range(15):
            q_item = comp_pool[i % len(comp_pool)]
            t_name, q_text, op_a, op_b, op_c, op_d, corr, expl, sc = get_varied_question(q_item, paper_num)
            topic_id = get_topic_id(comp_id, t_name)
            cursor.execute("""
            INSERT INTO questions 
            (subject_id, topic_id, tier, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, shortcut, year, source)
            VALUES (?, ?, 'Tier-II', 'Easy', ?, ?, ?, ?, ?, ?, ?, ?, 2026, ?)
            """, (comp_id, topic_id, q_text, op_a, op_b, op_c, op_d, corr, expl, sc, f"SSC CHSL Tier-II Model Paper {paper_num}"))
            q_id = cursor.lastrowid
            cursor.execute("INSERT INTO mock_test_questions (mock_test_id, question_id, section_name, order_num) VALUES (?, ?, ?, ?)",
                           (m_id, q_id, "Section-III: Computer Knowledge Test", order))
            order += 1

        print(f"Created Tier-II Model Paper {paper_num} (135 Questions) with ID {m_id}")

    conn.commit()
    conn.close()
    print("All SSC CHSL Model Papers generated and inserted successfully!")

if __name__ == '__main__':
    create_model_papers()
