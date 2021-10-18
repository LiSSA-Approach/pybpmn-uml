from pybpmn.mode import Mode

VALID_SPLITS = ("train", "val", "test")

# --- Relations ---
ARROW_NEXT_REL = "arrow_next"
ARROW_PREV_REL = "arrow_prev"
TEXT_BELONGS_TO_REL = "text_belongs_to"
ARROW_KEYPOINT_FIELDS = ("tail", "head")
ARROW_RELATIONS = (ARROW_PREV_REL, ARROW_NEXT_REL)

# UML-Extension constants
DEFAULT_MODE = Mode.UML_CLASS
BELONGS_TO_REL = "belongs_to"

RELATIONS = (*ARROW_RELATIONS, TEXT_BELONGS_TO_REL, BELONGS_TO_REL)