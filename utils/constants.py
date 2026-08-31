"""Constants mirrored from the frontend's src/types.ts so both sides agree on
valid enum values without the backend needing to import TypeScript."""

BOARDS = ["CBSE", "ICSE", "ISC", "UK-Cambridge", "NCERT", "NEET", "IIT"]

CLASS_GRADES = [
    "Class 5", "Class 6", "Class 7", "Class 8",
    "Class 9", "Class 10", "Class 11", "Class 12",
]

SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Science",
    "Social Studies", "English", "Computer Science", "Logical Reasoning",
]

DIFFICULTIES = ["simple", "medium", "hard"]

QUESTION_TYPES = ["mcq", "objective", "numerical", "logical"]

PERFORMANCE_BANDS = [
    "Needs Foundation", "Developing", "Proficient", "Advanced Mastery", "Competitive Ready",
]

BADGE_IDS = {
    "PIONEER": "badge-pioneer",
    "PERFECT_10": "badge-perfect-10",
    "SPEED_DEMON": "badge-speed-demon",
    "STREAK_3": "badge-streak-3",
    "STREAK_7": "badge-streak-7",
    "OLYMPIAD_THINKER": "badge-olympiad-thinker",
}

DEFAULT_EXAM_QUESTION_COUNT = 10
DEFAULT_EXAM_TOTAL_MARKS = 10
DEFAULT_EXAM_TIME_LIMIT_MINUTES = 15
