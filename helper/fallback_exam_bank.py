"""Deterministic fallback question bank, ported from the frontend's original
server.ts `generateFallbackExam`. Used when Mistral is unavailable or returns
invalid content, so the app never crashes or silently fabricates an
"AI-generated" label for content the AI didn't actually produce
(master prompt §50)."""


def build_fallback_questions(board: str, subject: str, difficulty: str, ref_links: list[dict]) -> list[dict]:
    return [
        {
            "questionNumber": 1, "type": "mcq",
            "questionText": f"[{board} Standard] In {subject}, which fundamental property applies to standard equilibrium or conservation laws?",
            "options": [
                "A) Total energy in an isolated system remains constant",
                "B) Energy is created during rapid chemical state changes",
                "C) Resistance increases with cross-sectional area directly",
                "D) Velocity is independent of displacement in uniform acceleration",
            ],
            "correctAnswer": "A",
            "explanation": "By the First Law of Thermodynamics and the Law of Conservation of Energy, energy can neither be created nor destroyed in an isolated system.",
            "topic": "Conservation Laws", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 2, "type": "numerical",
            "questionText": "A body accelerates uniformly from rest at 2 m/s² for 5 seconds. Calculate the final velocity in m/s.",
            "correctAnswer": "10",
            "explanation": "v = u + at = 0 + (2)(5) = 10 m/s.",
            "topic": "Kinematics", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 3, "type": "objective",
            "questionText": "State the SI unit of electrical resistance.",
            "correctAnswer": "Ohm",
            "explanation": "Resistance is measured in Ohms (Ω), defined by V = IR.",
            "topic": "Electricity Fundamentals", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 4, "type": "mcq",
            "questionText": "Which of the following is an example of a non-contact force?",
            "options": ["A) Friction", "B) Normal force", "C) Gravitational force", "D) Applied push force"],
            "correctAnswer": "C",
            "explanation": "Gravitational force acts at a distance without physical contact between objects.",
            "topic": "Forces", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 5, "type": "mcq",
            "questionText": "For a quadratic equation with discriminant D = 0, the roots are:",
            "options": ["A) Two distinct real roots", "B) Two equal real roots", "C) No real roots", "D) Three real roots"],
            "correctAnswer": "B",
            "explanation": "When discriminant D = b² - 4ac = 0, the quadratic formula yields two coincident (equal) real roots x = -b/(2a).",
            "topic": "Discriminant Analysis", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 6, "type": "numerical",
            "questionText": "If a lens of focal length +0.20 m is placed in contact with another lens of focal length -0.50 m, calculate the combined power in Dioptres:",
            "correctAnswer": "+3",
            "explanation": "P1 = 1/0.20 = +5 D; P2 = 1/(-0.50) = -2 D. Total power P = P1 + P2 = +5 + (-2) = +3 D.",
            "topic": "Lens Combinations & Power", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 7, "type": "mcq",
            "questionText": "In genetic inheritance (Mendelian monohybrid cross), what is the phenotypic ratio in the F2 generation between two heterozygous parents (Aa x Aa)?",
            "options": ["A) 1:2:1", "B) 3:1", "C) 9:3:3:1", "D) 1:1"],
            "correctAnswer": "B",
            "explanation": "The phenotypic ratio is 3 Dominant : 1 Recessive. The genotypic ratio is 1 AA : 2 Aa : 1 aa.",
            "topic": "Mendelian Genetics", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 8, "type": "objective",
            "questionText": "What term defines the phenomenon where light traveling from an optically denser to rarer medium is completely reflected at an incident angle greater than the critical angle?",
            "correctAnswer": "Total Internal Reflection",
            "explanation": "Total Internal Reflection (TIR) occurs when light strikes the interface from a denser to rarer medium at an angle exceeding the critical angle.",
            "topic": "Optics & Wave Phenomena", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 9, "type": "logical",
            "questionText": "Assertion (A): Liquid pressure increases with depth.\nReason (R): Pressure exerted by a liquid column is given by P = h · ρ · g where h is depth, ρ is density, and g is acceleration due to gravity.",
            "options": [
                "A) Both A and R are true and R is the correct explanation of A",
                "B) Both A and R are true but R is NOT the correct explanation of A",
                "C) A is true but R is false",
                "D) A is false but R is true",
            ],
            "correctAnswer": "A",
            "explanation": "Because P = h · ρ · g, as depth h increases, the column weight above increases proportionally, raising fluid pressure.",
            "topic": "Fluid Pressure Logic", "difficulty": difficulty, "marks": 1,
        },
        {
            "questionNumber": 10, "type": "mcq",
            "questionText": "According to De Morgan's Theorem in Boolean Logic, (A + B)' is equivalent to:",
            "options": ["A) A' + B'", "B) A' · B'", "C) (A · B)'", "D) A · B"],
            "correctAnswer": "B",
            "explanation": "De Morgan's First Law states that the complement of a logical sum equals the product of individual complements: (A + B)' = A' · B'.",
            "topic": "Boolean Algebra", "difficulty": difficulty, "marks": 1,
        },
    ]
