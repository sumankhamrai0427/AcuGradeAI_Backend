"""Deterministic fallback question bank.
Used when DB or AI models need supplementary curriculum questions or offline generation,
so the app always generates age-appropriate, subject-specific questions for any grade and question count.
"""

KIDS_QUESTION_BANKS = {
    "computer science": [
        {
            "type": "mcq",
            "questionText": "Which part of a computer looks like a TV screen and displays our work? 🖥️",
            "options": ["A) Monitor", "B) Keyboard", "C) Mouse", "D) CPU"],
            "correctAnswer": "A",
            "explanation": "A Monitor is the visual display unit that shows pictures, text, and videos on the computer.",
            "topic": "Parts of a Computer",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which key is the longest key on the keyboard and is used to give spaces between words? ⌨️",
            "options": ["A) Enter Key", "B) Spacebar", "C) Shift Key", "D) Backspace"],
            "correctAnswer": "B",
            "explanation": "The Spacebar is the longest horizontal key on the keyboard used to insert space between words.",
            "topic": "Keyboard Skills",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which device is known as the 'Brain of the Computer'? 🧠",
            "options": ["A) Mouse", "B) Monitor", "C) CPU", "D) Printer"],
            "correctAnswer": "C",
            "explanation": "CPU (Central Processing Unit) performs all calculations and controls all parts of the computer.",
            "topic": "Computer Fundamentals",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What hand-held device has 2 buttons and a scroll wheel to point and click on items? 🖱️",
            "options": ["A) Mouse", "B) Microphone", "C) Speaker", "D) Scanner"],
            "correctAnswer": "A",
            "explanation": "A computer mouse is a pointing device used to click, double click, and drag items.",
            "topic": "Input Devices",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which key do we press to start typing on a new line? ↵",
            "options": ["A) Caps Lock", "B) Enter Key", "C) Escape Key", "D) Delete Key"],
            "correctAnswer": "B",
            "explanation": "The Enter key moves the cursor to the beginning of the next line.",
            "topic": "Keyboard Skills",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which output device is used to print our drawings and stories on paper? 🖨️",
            "options": ["A) Printer", "B) Webcam", "C) Keyboard", "D) Joystick"],
            "correctAnswer": "A",
            "explanation": "A printer produces a paper copy (hard copy) of documents stored in the computer.",
            "topic": "Output Devices",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What software program is used to draw and color digital pictures on the computer? 🎨",
            "options": ["A) MS Paint", "B) Calculator", "C) Notepad", "D) Media Player"],
            "correctAnswer": "A",
            "explanation": "MS Paint is a simple graphics painting program included with Microsoft Windows.",
            "topic": "Fun Tools & Paint",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which key turns on CAPITAL letters when you type words? 🔠",
            "options": ["A) Caps Lock", "B) Spacebar", "C) Backspace", "D) Arrow Key"],
            "correctAnswer": "A",
            "explanation": "Pressing the Caps Lock key allows all typed letters to appear in UPPERCASE.",
            "topic": "Keyboard Skills",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which device helps us listen to music and games from our computer? 🔊",
            "options": ["A) Speakers", "B) Scanner", "C) Keyboard", "D) Mouse"],
            "correctAnswer": "A",
            "explanation": "Speakers output audio sound signals so we can hear songs, voices, and game effects.",
            "topic": "Output Devices",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which tool in Paint allows you to fill a whole shape with your favorite color? 🪣",
            "options": ["A) Fill with Color (Bucket)", "B) Pencil Tool", "C) Eraser Tool", "D) Magnifier"],
            "correctAnswer": "A",
            "explanation": "The 'Fill with Color' bucket tool floods any closed boundary or shape with color.",
            "topic": "Fun Tools & Paint",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "A small blinking vertical line on the monitor that shows where you will type next is called: ✍️",
            "options": ["A) Cursor", "B) Icon", "C) Desktop", "D) Taskbar"],
            "correctAnswer": "A",
            "explanation": "The Cursor is the blinking mark that indicates your current typing position.",
            "topic": "Typing Basics",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which portable computer can easily sit on your lap and run on battery? 💻",
            "options": ["A) Laptop", "B) Supercomputer", "C) Mainframe", "D) Server Tower"],
            "correctAnswer": "A",
            "explanation": "A laptop is a compact, portable computer that you can carry and use anywhere.",
            "topic": "Types of Computers",
            "marks": 1,
        },
    ],
    "mathematics": [
        {
            "type": "mcq",
            "questionText": "What is the sum of 25 + 15? ➕",
            "options": ["A) 40", "B) 35", "C) 50", "D) 45"],
            "correctAnswer": "A",
            "explanation": "25 + 15 = 40.",
            "topic": "Addition",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "How many sides does a triangle have? 🔺",
            "options": ["A) 3", "B) 4", "C) 5", "D) 2"],
            "correctAnswer": "A",
            "explanation": "A triangle is a closed geometric shape with exactly 3 straight sides and 3 angles.",
            "topic": "Basic 2D Shapes",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is 7 multiplied by 4 (7 × 4)? ✖️",
            "options": ["A) 28", "B) 24", "C) 32", "D) 21"],
            "correctAnswer": "A",
            "explanation": "7 × 4 = 28.",
            "topic": "Multiplication Tables",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "If you have 50 rupees and buy a chocolate for 20 rupees, how much money is left? 🍫",
            "options": ["A) 30 Rupees", "B) 25 Rupees", "C) 35 Rupees", "D) 20 Rupees"],
            "correctAnswer": "A",
            "explanation": "50 - 20 = 30 rupees remaining.",
            "topic": "Money & Subtraction",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which of these numbers is an EVEN number? 🔢",
            "options": ["A) 18", "B) 15", "C) 21", "D) 9"],
            "correctAnswer": "A",
            "explanation": "Even numbers are cleanly divisible by 2 and end in 0, 2, 4, 6, or 8. 18 is even.",
            "topic": "Odd & Even Numbers",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the place value of 6 in the number 462? 🎯",
            "options": ["A) 60 (Tens)", "B) 600 (Hundreds)", "C) 6 (Ones)", "D) 6000 (Thousands)"],
            "correctAnswer": "A",
            "explanation": "In 462, 4 is hundreds (400), 6 is tens (60), and 2 is ones (2).",
            "topic": "Place Value",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "How many minutes are there in ONE full hour? ⏱️",
            "options": ["A) 60 minutes", "B) 100 minutes", "C) 30 minutes", "D) 24 minutes"],
            "correctAnswer": "A",
            "explanation": "There are 60 minutes in 1 hour.",
            "topic": "Time Measurement",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is 80 minus 35 (80 - 35)? ➖",
            "options": ["A) 45", "B) 55", "C) 40", "D) 50"],
            "correctAnswer": "A",
            "explanation": "80 - 35 = 45.",
            "topic": "Subtraction",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "A square has how many equal sides? 🔲",
            "options": ["A) 4 equal sides", "B) 3 sides", "C) 5 sides", "D) 0 sides"],
            "correctAnswer": "A",
            "explanation": "A square has 4 straight sides of equal length and 4 right angles.",
            "topic": "Basic 2D Shapes",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is 9 × 5? 🌟",
            "options": ["A) 45", "B) 40", "C) 54", "D) 36"],
            "correctAnswer": "A",
            "explanation": "9 × 5 = 45.",
            "topic": "Multiplication Tables",
            "marks": 1,
        },
    ],
    "science": [
        {
            "type": "mcq",
            "questionText": "What part of a plant absorbs water and minerals from deep under the soil? 🌱",
            "options": ["A) Roots", "B) Flower", "C) Leaves", "D) Fruit"],
            "correctAnswer": "A",
            "explanation": "Roots hold the plant firmly in the soil and absorb water and essential nutrients.",
            "topic": "Plants Around Us",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which animal is famous as the 'Ship of the Desert'? 🐪",
            "options": ["A) Camel", "B) Elephant", "C) Lion", "D) Horse"],
            "correctAnswer": "A",
            "explanation": "Camels can survive for weeks without water and walk effortlessly across sandy dunes.",
            "topic": "Animal Habitats",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Ice is which physical state of water? 🧊",
            "options": ["A) Solid", "B) Liquid", "C) Gas", "D) Plasma"],
            "correctAnswer": "A",
            "explanation": "Water freezes into ice at 0°C, turning into a solid state.",
            "topic": "States of Matter",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which human sense organ helps us hear songs and sounds? 👂",
            "options": ["A) Ears", "B) Eyes", "C) Nose", "D) Tongue"],
            "correctAnswer": "A",
            "explanation": "Our ears receive sound vibrations allowing us to hear.",
            "topic": "Our Sense Organs",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What gives green color to the leaves of plants? 🍃",
            "options": ["A) Chlorophyll", "B) Sunlight", "C) Carbon", "D) Sugar"],
            "correctAnswer": "A",
            "explanation": "Chlorophyll is the green pigment in leaves that captures sunlight for photosynthesis.",
            "topic": "Plant Life",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "The Earth gets heat and light energy naturally from the: ☀️",
            "options": ["A) Sun", "B) Moon", "C) Stars", "D) Wind"],
            "correctAnswer": "A",
            "explanation": "The Sun is our closest star and the primary source of light and heat for Earth.",
            "topic": "Solar System & Space",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Animals that eat ONLY plants and grass are called: 🌿",
            "options": ["A) Herbivores", "B) Carnivores", "C) Omnivores", "D) Predators"],
            "correctAnswer": "A",
            "explanation": "Herbivores (like cows, deer, and rabbits) feed only on plant matter.",
            "topic": "Animal Diets",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Water boiling in a kettle turns into water vapor. This process is called: 💨",
            "options": ["A) Evaporation", "B) Freezing", "C) Melting", "D) Condensation"],
            "correctAnswer": "A",
            "explanation": "Evaporation is the phase change from liquid to gas (water vapor).",
            "topic": "Water Cycle",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "How many bones make up an adult human skeleton? 🦴",
            "options": ["A) 206", "B) 150", "C) 300", "D) 100"],
            "correctAnswer": "A",
            "explanation": "An adult human body has 206 bones in the skeletal system.",
            "topic": "Human Body",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which gas do human beings breathe IN to stay alive? 🌬️",
            "options": ["A) Oxygen", "B) Carbon Dioxide", "C) Nitrogen", "D) Helium"],
            "correctAnswer": "A",
            "explanation": "Humans inhale Oxygen for cellular respiration and exhale Carbon Dioxide.",
            "topic": "Living Things",
            "marks": 1,
        },
    ],
    "english": [
        {
            "type": "mcq",
            "questionText": "Which of the following words is a NOUN (naming word)? 📚",
            "options": ["A) School", "B) Quickly", "C) Sing", "D) Beautiful"],
            "correctAnswer": "A",
            "explanation": "A noun is the name of a person, place, or thing. 'School' is a place.",
            "topic": "Nouns & Parts of Speech",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Choose the correct article: 'Anjali eats ___ apple every morning.' 🍎",
            "options": ["A) an", "B) a", "C) the", "D) no article"],
            "correctAnswer": "A",
            "explanation": "We use 'an' before words beginning with a vowel sound (a, e, i, o, u).",
            "topic": "Articles (A, An, The)",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the plural form of the word 'Child'? 🧒",
            "options": ["A) Children", "B) Childs", "C) Childrens", "D) Childes"],
            "correctAnswer": "A",
            "explanation": "The irregular plural form of child is 'children'.",
            "topic": "Plurals",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the OPPOSITE (antonym) of the word 'Happy'? 😢",
            "options": ["A) Sad", "B) Joyful", "C) Glad", "D) Excited"],
            "correctAnswer": "A",
            "explanation": "'Sad' is the antonym of happy.",
            "topic": "Antonyms & Synonyms",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Find the ACTION word (verb) in this sentence: 'Birds fly in the blue sky.' 🕊️",
            "options": ["A) Fly", "B) Birds", "C) Sky", "D) Blue"],
            "correctAnswer": "A",
            "explanation": "'Fly' is an action verb describing what the birds are doing.",
            "topic": "Verbs & Actions",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which punctuation mark comes at the end of a question? ❓",
            "options": ["A) Question mark (?)", "B) Full stop (.)", "C) Comma (,)", "D) Exclamation mark (!)"],
            "correctAnswer": "A",
            "explanation": "A question mark (?) is placed at the end of an interrogative sentence.",
            "topic": "Punctuation",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Choose the correct spelling: 🎨",
            "options": ["A) Beautiful", "B) Beautifull", "C) Beatiful", "D) Beauteful"],
            "correctAnswer": "A",
            "explanation": "The correct spelling is 'Beautiful'.",
            "topic": "Spelling Mastery",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the past tense of the verb 'Go'? 🚶",
            "options": ["A) Went", "B) Gone", "C) Goes", "D) Going"],
            "correctAnswer": "A",
            "explanation": "The past simple form of 'go' is 'went'.",
            "topic": "Tenses",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "A word that describes a noun (like 'A red car') is called: 🚗",
            "options": ["A) Adjective", "B) Verb", "C) Pronoun", "D) Conjunction"],
            "correctAnswer": "A",
            "explanation": "An adjective describes qualities of a noun (color, size, texture).",
            "topic": "Adjectives",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the synonym (similar meaning) of the word 'Large'? 🐘",
            "options": ["A) Big", "B) Tiny", "C) Short", "D) Narrow"],
            "correctAnswer": "A",
            "explanation": "'Big' means the same as large.",
            "topic": "Synonyms",
            "marks": 1,
        },
    ]
}

# Standard Secondary / Senior Curriculum Bank (Class 5-12)
SECONDARY_QUESTION_BANKS = {
    "computer science": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "Which data structure follows the LIFO (Last In First Out) principle?",
            "options": ["A) Stack", "B) Queue", "C) Linked List", "D) Binary Tree"],
            "correctAnswer": "A",
            "explanation": "In a Stack, the element added last is the first one to be removed (LIFO).",
            "topic": "Data Structures",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "In Python, which keyword is used to define an anonymous or inline function?",
            "options": ["A) lambda", "B) def", "C) inline", "D) func"],
            "correctAnswer": "A",
            "explanation": "The 'lambda' keyword defines small anonymous functions in Python.",
            "topic": "Python Programming",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the binary representation of the decimal number 13?",
            "options": ["A) 1101", "B) 1011", "C) 1110", "D) 1001"],
            "correctAnswer": "A",
            "explanation": "13 in binary is 8 + 4 + 0 + 1 = 1101.",
            "topic": "Number Systems",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "In SQL, which clause is used to filter groups created by the GROUP BY clause?",
            "options": ["A) HAVING", "B) WHERE", "C) ORDER BY", "D) LIMIT"],
            "correctAnswer": "A",
            "explanation": "HAVING filters aggregated groups, whereas WHERE filters individual table rows.",
            "topic": "Relational Databases",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the worst-case time complexity of Binary Search on a sorted array of size n?",
            "options": ["A) O(log n)", "B) O(n)", "C) O(n log n)", "D) O(1)"],
            "correctAnswer": "A",
            "explanation": "Binary search divides the search space in half at each step, giving O(log n) time.",
            "topic": "Algorithms",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "State De Morgan's Laws in Boolean Logic and write the algebraic equations for both laws.",
            "options": None,
            "correctAnswer": "(A + B)' = A' · B' and (A · B)' = A' + B'",
            "explanation": "De Morgan's First Law: The complement of a logical sum equals the product of individual complements (A + B)' = A' · B'. Second Law: The complement of a product equals the sum of complements (A · B)' = A' + B'.",
            "topic": "Boolean Algebra",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the difference between mutable and immutable data types in Python with one example for each.",
            "options": None,
            "correctAnswer": "Mutable types (e.g. lists, dicts) can be modified in-place; immutable types (e.g. tuples, strings, integers) cannot have their state altered after creation.",
            "explanation": "Mutable objects allow modifying element values without changing object identity (e.g., list.append()). Immutable objects generate new memory instances when modified.",
            "topic": "Python Programming",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "What is the CSS Box Model? Name its four constituent layers from inside to outside.",
            "options": None,
            "correctAnswer": "Content, Padding, Border, Margin",
            "explanation": "The CSS Box Model represents the rectangular space occupied by HTML elements, consisting of: Content (inner area), Padding (transparent inner space), Border (surrounding outline), and Margin (outer spacing).",
            "topic": "Web Technologies",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the concept of Encapsulation in Object-Oriented Programming and state one practical advantage.",
            "options": None,
            "correctAnswer": "Encapsulation is bundling data and methods into a single class unit, restricting direct access using access modifiers for data hiding and integrity.",
            "explanation": "Encapsulation safeguards internal object state from unauthorized external manipulation and decouples interface definition from implementation details.",
            "topic": "OOP Principles",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the primary differences between TCP (Transmission Control Protocol) and UDP (User Datagram Protocol).",
            "options": None,
            "correctAnswer": "TCP is connection-oriented, reliable with error checking (e.g., HTTP/FTP); UDP is connectionless and faster without delivery guarantees (e.g., video streaming/DNS).",
            "explanation": "TCP uses a three-way handshake ensuring in-order packet delivery. UDP sends packets with lower overhead, prioritizing speed over reliability.",
            "topic": "Computer Networks",
            "marks": 2,
        },
    ],
    "mathematics": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "For a quadratic equation ax² + bx + c = 0 with discriminant D = 0, the roots are:",
            "options": ["A) Two equal real roots", "B) Two distinct real roots", "C) Imaginary roots", "D) Three real roots"],
            "correctAnswer": "A",
            "explanation": "When discriminant D = b² - 4ac = 0, roots are coincident and real: x = -b/(2a).",
            "topic": "Quadratic Equations",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Find the 10th term of the Arithmetic Progression: 2, 5, 8, 11...",
            "options": ["A) 29", "B) 32", "C) 27", "D) 30"],
            "correctAnswer": "A",
            "explanation": "a = 2, d = 3. a_10 = a + (10 - 1)d = 2 + (9)(3) = 29.",
            "topic": "Arithmetic Progression",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the value of sin²(30°) + cos²(30°)?",
            "options": ["A) 1", "B) 0", "C) 1/2", "D) √3/2"],
            "correctAnswer": "A",
            "explanation": "By the Pythagorean trigonometric identity, sin²(θ) + cos²(θ) = 1 for any angle θ.",
            "topic": "Trigonometry",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "If the radius of a circle is 7 cm, calculate its circumference in cm (use π = 22/7):",
            "options": ["A) 44 cm", "B) 22 cm", "C) 88 cm", "D) 154 cm"],
            "correctAnswer": "A",
            "explanation": "Circumference = 2πr = 2 * (22/7) * 7 = 44 cm.",
            "topic": "Mensuration",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "If a fair die is rolled once, what is the probability of rolling a prime number?",
            "options": ["A) 1/2", "B) 1/3", "C) 2/3", "D) 1/6"],
            "correctAnswer": "A",
            "explanation": "Prime outcomes on a die are {2, 3, 5} -> 3 favorable out of 6 total = 3/6 = 1/2.",
            "topic": "Probability",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "Find the slope (gradient) of the line passing through the points (2, 3) and (6, 11). Show all calculation steps.",
            "options": None,
            "correctAnswer": "m = (11 - 3)/(6 - 2) = 8/4 = 2",
            "explanation": "Slope m = (y₂ - y₁) / (x₂ - x₁). Substituting coordinates: m = (11 - 3) / (6 - 2) = 8 / 4 = 2.",
            "topic": "Coordinate Geometry",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "The volume of a cube is 125 cm³. Calculate: (i) the edge length, and (ii) the total surface area of the cube.",
            "options": None,
            "correctAnswer": "Edge = 5 cm; Total Surface Area = 6 × a² = 6 × 25 = 150 cm²",
            "explanation": "Volume V = a³ = 125 ⟹ a = 5 cm. Total Surface Area = 6a² = 6 × (5)² = 150 cm².",
            "topic": "Mensuration",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Calculate the arithmetic mean of the numbers: 4, 8, 12, 16, and 20. Show the formula and step-by-step calculation.",
            "options": None,
            "correctAnswer": "Mean = Sum / Count = (4 + 8 + 12 + 16 + 20) / 5 = 60 / 5 = 12",
            "explanation": "Mean x̄ = (∑x) / n. Sum = 4 + 8 + 12 + 16 + 20 = 60. Count n = 5. Mean = 60 / 5 = 12.",
            "topic": "Statistics",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Solve the linear equation for x: 3x - 7 = 14. Show all algebraic transposition steps.",
            "options": None,
            "correctAnswer": "3x = 14 + 7 ⟹ 3x = 21 ⟹ x = 7",
            "explanation": "Add 7 to both sides: 3x = 21. Divide by 3: x = 21 / 3 = 7.",
            "topic": "Linear Equations",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "State Pythagoras Theorem and calculate the length of the hypotenuse in a right triangle with perpendicular sides 6 cm and 8 cm.",
            "options": None,
            "correctAnswer": "Hypotenuse = √(6² + 8²) = √(36 + 64) = √100 = 10 cm",
            "explanation": "Pythagoras Theorem: In a right triangle, h² = p² + b². h = √(6² + 8²) = √100 = 10 cm.",
            "topic": "Pythagoras Theorem",
            "marks": 2,
        },
    ],
    "english": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "Identify the passive voice for: 'The chef prepared a magnificent dinner.'",
            "options": [
                "A) A magnificent dinner was prepared by the chef.",
                "B) A magnificent dinner is being prepared by the chef.",
                "C) The chef was preparing dinner.",
                "D) Dinner has been prepared by chef."
            ],
            "correctAnswer": "A",
            "explanation": "Simple past active 'prepared' transforms to 'was prepared' in passive voice.",
            "topic": "Active and Passive Voice",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which of the following is a complex sentence?",
            "options": [
                "A) Although it was raining, we decided to play outside.",
                "B) She bought apples and oranges from the grocery store.",
                "C) The train arrived on time.",
                "D) He worked hard, so he passed the exam."
            ],
            "correctAnswer": "A",
            "explanation": "A complex sentence contains one independent clause and at least one dependent clause introduced by a subordinating conjunction ('Although').",
            "topic": "Sentence Structures",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Choose the correct indirect speech for: He said, 'I am reading a novel.'",
            "options": [
                "A) He said that he was reading a novel.",
                "B) He says that he is reading a novel.",
                "C) He said that he read a novel.",
                "D) He told that he had read a novel."
            ],
            "correctAnswer": "A",
            "explanation": "Present continuous 'am reading' shifts to past continuous 'was reading' in reported speech.",
            "topic": "Direct & Indirect Speech",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What figure of speech is used in: 'The classroom was a zoo during the break'?",
            "options": ["A) Metaphor", "B) Simile", "C) Personification", "D) Hyperbole"],
            "correctAnswer": "A",
            "explanation": "A metaphor directly equates one thing to another without using 'like' or 'as'.",
            "topic": "Figures of Speech",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Select the antonym for the word 'Candid':",
            "options": ["A) Deceitful", "B) Honest", "C) Frank", "D) Sincere"],
            "correctAnswer": "A",
            "explanation": "'Candid' means truthful and straightforward; its antonym is 'Deceitful'.",
            "topic": "Vocabulary & Antonyms",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "Explain the meaning of the idiom 'Bite the bullet' and write a meaningful sentence using it.",
            "options": None,
            "correctAnswer": "Meaning: To face a difficult or unpleasant situation with courage. Example: She decided to bite the bullet and apologize for her mistake.",
            "explanation": "'Bite the bullet' originated from soldiers biting on lead bullets during surgery without anesthesia. It signifies confronting unavoidable hardship bravely.",
            "topic": "Idioms and Phrases",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the difference in usage between the modal auxiliary verbs 'Must' and 'Might' with one example for each.",
            "options": None,
            "correctAnswer": "'Must' indicates strong obligation, necessity, or certainty (e.g., 'You must wear a seatbelt'). 'Might' indicates weak possibility or uncertainty (e.g., 'It might rain today').",
            "explanation": "'Must' expresses mandatory rules or high probability, whereas 'Might' expresses tentative possibilities.",
            "topic": "Modal Auxiliaries",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Identify the complete Subject and Predicate in the inverted sentence: 'Under the old wooden bridge lives a family of otters.'",
            "options": None,
            "correctAnswer": "Subject: 'A family of otters'; Predicate: 'lives under the old wooden bridge'",
            "explanation": "In inverted sentences, the entity performing the verb action ('a family of otters') is the subject, while the prepositional phrase and verb form the predicate.",
            "topic": "Subject-Verb Agreement",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain how the negative prefixes 'Il-', 'Im-', and 'Un-' change the meaning of root words, giving one example for each.",
            "options": None,
            "correctAnswer": "They create antonyms by denoting negation/absence: 'Il-' + Legible = Illegible; 'Im-' + Possible = Impossible; 'Un-' + Happy = Unhappy.",
            "explanation": "Prefixes modify word polarity: 'Il-' applies before 'l', 'Im-' before 'm'/'p', and 'Un-' as a general English negation prefix.",
            "topic": "Prefixes & Suffixes",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Define an Adjective Clause and write a sentence that contains an adjective clause qualifying a noun.",
            "options": None,
            "correctAnswer": "Definition: A dependent clause that modifies a noun or pronoun. Example: 'The student who worked diligently scored highest in the exam.'",
            "explanation": "Adjective clauses are introduced by relative pronouns (who, which, that, whose) and describe attributes of an antecedent noun.",
            "topic": "Clauses and Grammar",
            "marks": 2,
        },
    ],
    "science": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "Which cell organelle is commonly referred to as the 'Powerhouse of the Cell'?",
            "options": ["A) Mitochondria", "B) Ribosome", "C) Golgi Apparatus", "D) Nucleus"],
            "correctAnswer": "A",
            "explanation": "Mitochondria generate cellular energy in the form of ATP through cellular respiration.",
            "topic": "Cell Biology",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "What is the chemical formula of common baking soda?",
            "options": ["A) NaHCO₃", "B) Na₂CO₃", "C) NaCl", "D) NaOH"],
            "correctAnswer": "A",
            "explanation": "Sodium hydrogen carbonate (Sodium Bicarbonate, NaHCO₃) is baking soda.",
            "topic": "Acids, Bases & Salts",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which law of motion gives the fundamental definition of Force as F = ma?",
            "options": [
                "A) Newton's Second Law",
                "B) Newton's First Law",
                "C) Newton's Third Law",
                "D) Law of Gravitation"
            ],
            "correctAnswer": "A",
            "explanation": "Newton's Second Law states that the rate of change of momentum is proportional to applied force (F = ma).",
            "topic": "Laws of Motion",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which metal remains in liquid state at standard room temperature?",
            "options": ["A) Mercury (Hg)", "B) Sodium (Na)", "C) Lead (Pb)", "D) Gallium (Ga)"],
            "correctAnswer": "A",
            "explanation": "Mercury is the only elemental metal that is liquid at standard room temperature (25°C).",
            "topic": "Metals and Non-Metals",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "The phenomenon of splitting white light into its component colors through a prism is called:",
            "options": ["A) Dispersion", "B) Refraction", "C) Total Internal Reflection", "D) Diffraction"],
            "correctAnswer": "A",
            "explanation": "Dispersion is the separation of white light into its spectrum of colors due to varying wavelengths.",
            "topic": "Light and Optics",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "Explain why the pH of pure distilled water is 7.0 at 25°C and state what happens to the ion product of water (Kw) when temperature increases.",
            "options": None,
            "correctAnswer": "In pure water at 25°C, [H⁺] = [OH⁻] = 1.0 × 10⁻⁷ M, hence pH = -log(10⁻⁷) = 7.0 (neutral). As temperature increases, auto-ionization of water is endothermic, so Kw increases.",
            "explanation": "Water self-ionizes: H₂O ⇌ H⁺ + OH⁻. At 25°C, equal concentrations yield neutral pH 7. Increasing temperature shifts equilibrium rightward, increasing Kw.",
            "topic": "Chemical Equilibrium",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Why is blood group O-negative termed the 'Universal Donor'? Explain with respect to RBC surface antigens and transfusion compatibility.",
            "options": None,
            "correctAnswer": "O-negative red blood cells lack A, B, and Rh (D) surface antigens, so recipient antibodies will not trigger agglutination/immune rejection.",
            "explanation": "Because O- RBCs carry no A, B, or Rh surface agglutinogens, they can safely be transfused into any ABO/Rh blood group recipient in emergencies.",
            "topic": "Circulatory System",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "State the working principle of an Ammeter and explain why it must always be connected in series in an electric circuit.",
            "options": None,
            "correctAnswer": "An ammeter measures electric current and has very low internal resistance. It is connected in series so the full circuit current passes through it without significantly reducing current flow.",
            "explanation": "If connected in parallel, its low resistance would create a short circuit and draw excessive current, potentially damaging the circuit.",
            "topic": "Electricity & Magnetism",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain why the combustion of methane gas (CH₄) is classified as an exothermic chemical reaction. Write the balanced chemical equation.",
            "options": None,
            "correctAnswer": "Equation: CH₄(g) + 2O₂(g) ⟶ CO₂(g) + 2H₂O(g) + Heat. It is exothermic because energy released in bond formation in products exceeds energy needed to break reactant bonds.",
            "explanation": "Combustion releases thermal and radiant energy to the surroundings (negative ΔH), characterizing exothermic reactions.",
            "topic": "Chemical Reactions",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Describe the biological significance of the Ozone Layer (O₃) in the Stratosphere and state two consequences of ozone depletion on human health.",
            "options": None,
            "correctAnswer": "Significance: Absorbs harmful high-energy solar UV-B radiation. Consequences: Increased incidence of skin cancers/melanoma and cataracts/eye damage.",
            "explanation": "Stratospheric ozone shields terrestrial organisms from lethal UV-B radiation. Depletion impairs cellular DNA in biological tissues.",
            "topic": "Environmental Science",
            "marks": 2,
        },
    ],
    "social studies": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "Who is revered as the 'Father of the Indian Constitution'?",
            "options": ["A) Dr. B.R. Ambedkar", "B) Mahatma Gandhi", "C) Jawaharlal Nehru", "D) Sardar Vallabhbhai Patel"],
            "correctAnswer": "A",
            "explanation": "Dr. Bhimrao Ramji Ambedkar served as the Chairman of the Drafting Committee of the Constitution of India.",
            "topic": "Indian Polity & Constitution",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which imaginary line divides the Earth into the Northern and Southern Hemispheres?",
            "options": ["A) Equator (0° Latitude)", "B) Prime Meridian (0° Longitude)", "C) Tropic of Cancer", "D) Tropic of Capricorn"],
            "correctAnswer": "A",
            "explanation": "The Equator is the 0° parallel of latitude dividing Earth into Northern and Southern halves.",
            "topic": "Physical Geography",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "In which year did the historic Revolt of 1857 (Sepoy Mutiny) break out in India?",
            "options": ["A) 1857", "B) 1757", "C) 1947", "D) 1885"],
            "correctAnswer": "A",
            "explanation": "The first major armed uprising against British East India Company rule began in 1857 at Meerut.",
            "topic": "Modern Indian History",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which tier of government in India operates at the local village grassroots level?",
            "options": ["A) Gram Panchayat (Panchayati Raj)", "B) Municipal Corporation", "C) State Legislature", "D) Parliament"],
            "correctAnswer": "A",
            "explanation": "The 73rd Constitutional Amendment Act established the 3-tier Panchayati Raj system with Gram Panchayat at the village base.",
            "topic": "Local Self Government",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Which is the longest river in peninsular India?",
            "options": ["A) Godavari", "B) Krishna", "C) Narmada", "D) Kaveri"],
            "correctAnswer": "A",
            "explanation": "The Godavari River is known as 'Dakshin Ganga' and is the longest peninsular river in India (approx 1,465 km).",
            "topic": "Drainage Systems",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "Explain the significance of Fundamental Rights enshrined in Part III of the Indian Constitution.",
            "options": None,
            "correctAnswer": "Fundamental Rights (Articles 12-35) protect individual liberties, equality, and dignity against arbitrary state action, enforceable via High Courts and Supreme Court (Article 32).",
            "explanation": "They guarantee civil liberties such as Equality, Freedom of Speech, Protection from Exploitation, and Constitutional Remedies for democratic justice.",
            "topic": "Indian Civics",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "State two major geographical and economic factors that led to the onset of the Industrial Revolution in 18th-century Britain.",
            "options": None,
            "correctAnswer": "1. Abundant coal and iron ore deposits close to water transport routes. 2. Technological innovations (steam engine, spinning jenny) coupled with capital from colonial trade.",
            "explanation": "Britain possessed natural resources, capital wealth, naval dominance, and a stable patent legal system accelerating mechanization.",
            "topic": "World History",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain why Black Soil (Regur Soil) of the Deccan Plateau is ideal for cotton cultivation.",
            "options": None,
            "correctAnswer": "Black soil is fine-textured, clayey, rich in calcium carbonate, magnesium, and potash, with exceptional moisture-retention capacity essential for cotton maturation.",
            "explanation": "Originating from volcanic lava weathering, its moisture-holding and deep cracking properties aerate the soil, providing ideal conditions for cotton crops.",
            "topic": "Resources & Agriculture",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the administrative and strategic role of Chanakya (Kautilya) in the establishment of the Maurya Empire.",
            "options": None,
            "correctAnswer": "Chanakya mentored Chandragupta Maurya, devised political alliances to overthrow the Nanda Dynasty, and authored the Arthashastra establishing statecraft governance.",
            "explanation": "Chanakya's economic treaties, espionage networks, and military diplomacy laid the institutional foundation of India's first unified empire.",
            "topic": "Ancient History",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "What is the importance of Universal Adult Suffrage in a democratic nation like India?",
            "options": None,
            "correctAnswer": "It grants every citizen aged 18+ the right to vote without discrimination of caste, religion, gender, or wealth, upholding political equality and people's sovereignty.",
            "explanation": "Guaranteed under Article 326 of the Constitution, it ensures representative democracy and accountability of elected governments.",
            "topic": "Elections & Democracy",
            "marks": 2,
        },
    ],
    "logical reasoning": [
        # 1-5: MCQs (1 Mark each)
        {
            "type": "mcq",
            "questionText": "Find the next number in the series: 3, 6, 12, 24, 48, ___",
            "options": ["A) 96", "B) 72", "C) 84", "D) 100"],
            "correctAnswer": "A",
            "explanation": "Each number is multiplied by 2. 48 × 2 = 96.",
            "topic": "Number Series",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "If BOOK is coded as 43, what is the code for PEN (P=16, E=5, N=14)?",
            "options": ["A) 35", "B) 32", "C) 40", "D) 30"],
            "correctAnswer": "A",
            "explanation": "Sum of alphabetical positions: 16 + 5 + 14 = 35.",
            "topic": "Coding-Decoding",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Pointing to a photograph, Rohit said, 'She is the mother of my father's only son.' Who is she to Rohit?",
            "options": ["A) Mother", "B) Sister", "C) Aunt", "D) Grandmother"],
            "correctAnswer": "A",
            "explanation": "Rohit's father's only son is Rohit himself. Her mother is Rohit's mother.",
            "topic": "Blood Relations",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "A clock shows 3:00. What is the angle between the hour hand and the minute hand?",
            "options": ["A) 90°", "B) 60°", "C) 120°", "D) 45°"],
            "correctAnswer": "A",
            "explanation": "At 3:00, the minute hand is at 12 and the hour hand is at 3, creating a 90° right angle.",
            "topic": "Clock Problems",
            "marks": 1,
        },
        {
            "type": "mcq",
            "questionText": "Choose the odd one out:",
            "options": ["A) Triangle", "B) Square", "C) Rectangle", "D) Circle"],
            "correctAnswer": "D",
            "explanation": "Circle is curved, while Triangle, Square, and Rectangle are polygons made of straight line segments.",
            "topic": "Classification",
            "marks": 1,
        },
        # 6-10: SAQs (2 Marks each)
        {
            "type": "saq",
            "questionText": "If South-East becomes North, and North-East becomes West, explain what direction 'West' will become. Show your angle rotation deduction.",
            "options": None,
            "correctAnswer": "West becomes South-East. Deduction: The compass shifts 135° clockwise. Rotating West by 135° clockwise yields South-East.",
            "explanation": "Angle between South-East and North is 135° clockwise. Applying a 135° clockwise rotation to West leads to South-East.",
            "topic": "Direction Sense",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "In a class row of 25 students, Priya ranks 10th from the left end. Calculate her rank from the right end and show the ranking formula.",
            "options": None,
            "correctAnswer": "Rank from Right = (Total Students - Rank from Left) + 1 = (25 - 10) + 1 = 16th",
            "explanation": "Formula: Total = Left_Rank + Right_Rank - 1 ⟹ Right_Rank = 25 - 10 + 1 = 16th.",
            "topic": "Order & Ranking",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Explain the semantic relationship in the analogy 'Doctor : Hospital :: Teacher : School' and formulate another pair with the same relationship.",
            "options": None,
            "correctAnswer": "Relationship: Professional to their primary Workplace. New example: 'Judge : Court' or 'Scientist : Laboratory'.",
            "explanation": "The analogy represents Person : Place of Work. Doctors practice in hospitals, and teachers instruct in schools.",
            "topic": "Analogies",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "Given Premises: (1) All squares are rectangles. (2) All rectangles are quadrilaterals. State the logical deductive conclusion regarding squares and explain why.",
            "options": None,
            "correctAnswer": "Conclusion: All squares are quadrilaterals. Reason: By the transitive property of categorical syllogisms (A ⊆ B and B ⊆ C ⟹ A ⊆ C).",
            "explanation": "Since the subset of squares is entirely contained within rectangles, and rectangles within quadrilaterals, every square is necessarily a quadrilateral.",
            "topic": "Syllogisms & Logic",
            "marks": 2,
        },
        {
            "type": "saq",
            "questionText": "If arithmetic operator symbols are coded as '+' means '×', '×' means '÷', and '÷' means '+', evaluate the expression: 8 + 4 ÷ 6 × 2. Show step-by-step BODMAS evaluation.",
            "options": None,
            "correctAnswer": "Replaced expression: 8 × 4 + (6 ÷ 2) = 32 + 3 = 35",
            "explanation": "Substituting operators gives 8 × 4 + 6 ÷ 2. By BODMAS order: 6 ÷ 2 = 3; 8 × 4 = 32; 32 + 3 = 35.",
            "topic": "Mathematical Operations",
            "marks": 2,
        },
    ],
}


def build_fallback_questions(
    board: str,
    subject: str,
    difficulty: str,
    ref_links: list[dict] | None = None,
    class_grade: str = "Class 3",
    limit: int = 5,
    force_mcq: bool = False,
) -> list[dict]:
    """Generates deterministic, grade-appropriate, subject-matched curriculum questions
    matching the exact question count requested.
    """
    clean_subj = (subject or "General Assessment").lower().strip()
    clean_grade = (class_grade or "").lower().strip()
    is_kid = any(k in clean_grade for k in ["class 1", "class 2", "class 3", "class 4"])

    # Determine bank category
    bank_map = KIDS_QUESTION_BANKS if is_kid else SECONDARY_QUESTION_BANKS
    matched_questions: list[dict] = []

    if "comput" in clean_subj or "code" in clean_subj or "it" in clean_subj or "ai" in clean_subj:
        matched_questions = bank_map.get("computer science", [])
    elif "math" in clean_subj or "algebra" in clean_subj or "calculus" in clean_subj:
        matched_questions = bank_map.get("mathematics", [])
    elif "eng" in clean_subj or "gramm" in clean_subj:
        matched_questions = bank_map.get("english", [])
    elif "logic" in clean_subj or "reason" in clean_subj or "aptitude" in clean_subj:
        matched_questions = bank_map.get("logical reasoning", bank_map.get("mathematics", []))
    elif "social" in clean_subj or "hist" in clean_subj or "civic" in clean_subj or "geog" in clean_subj or "sst" in clean_subj:
        matched_questions = bank_map.get("social studies", bank_map.get("science" if is_kid else "physics", []))
    elif "sci" in clean_subj or "phys" in clean_subj or "chem" in clean_subj or "bio" in clean_subj or "evs" in clean_subj:
        matched_questions = bank_map.get("science" if is_kid else "science", bank_map.get("physics", []))
    else:
        # Fallback to subject list or combine
        matched_questions = bank_map.get("computer science" if "comp" in clean_subj else "science" if is_kid else "mathematics", [])

    if not matched_questions:
        matched_questions = KIDS_QUESTION_BANKS["science"] if is_kid else SECONDARY_QUESTION_BANKS["computer science"]

    # Assemble questions up to limit
    result = []
    pool = list(matched_questions)
    
    # If limit is larger than pool, cycle or generate parametric variants
    while len(result) < limit:
        for idx, item in enumerate(pool):
            if len(result) >= limit:
                break
            q_copy = dict(item)
            q_num = len(result) + 1
            q_copy["questionNumber"] = q_num
            q_copy["difficulty"] = difficulty
            if force_mcq:
                q_copy["type"] = "mcq"
                q_copy["marks"] = 1
                if not q_copy.get("options") or len(q_copy.get("options", [])) < 2:
                    corr = q_copy.get("correctAnswer", "A")
                    q_copy["options"] = [f"A) {corr}", "B) Alternative Option B", "C) Alternative Option C", "D) Alternative Option D"]
                    q_copy["correctAnswer"] = "A"
            elif is_kid:
                q_copy["type"] = "mcq"
                q_copy["marks"] = 1
            elif any(k in clean_grade for k in ["class 11", "class 12", "neet", "iit"]):
                q_copy["marks"] = 2
            else:
                # Class 5 to 10: 5 MCQs (1 mark) + 5 SAQs (2 marks)
                if len(result) < 5:
                    q_copy["type"] = "mcq"
                    q_copy["marks"] = 1
                else:
                    q_copy["type"] = "saq"
                    q_copy["marks"] = 2
            result.append(q_copy)
        if not pool:
            break

    return result
