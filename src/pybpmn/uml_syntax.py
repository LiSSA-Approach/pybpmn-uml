import yamlu

# UML class diagram extension

# All available UML node categories
CLASS = "Class"
INTERFACE = "Interface"
ENUMERATION = "Enumeration"
ABSTRACT_CLASS = "AbstractClass"
QUALIFIER = "Qualifier"
N_ARY_ASSO_DIA = "NAryAssociationDiamond"
UML_NODE_CATEGORIES = [CLASS, INTERFACE, ENUMERATION, ABSTRACT_CLASS, QUALIFIER, N_ARY_ASSO_DIA]

# All available UML label categories
LABEL = "Label"
UML_LABEL_CATEGORIES = [LABEL]

# All available UML edge categories
ASSOCIATION = "Association"
AGGREGATION = "Aggregation"
COMPOSITION = "Composition"
EXTENSION = "Extension"
DEPENDENCY = "Dependency"
REALIZATION = "Realization"
UML_EDGE_CATEGORIES = [ASSOCIATION, AGGREGATION, COMPOSITION, EXTENSION, DEPENDENCY, REALIZATION]

# All available UML category groups
CATEGORY_GROUPS = {
    "Shape": UML_NODE_CATEGORIES,
    "Edge": UML_EDGE_CATEGORIES,
    "Label": UML_LABEL_CATEGORIES
}

# Long names of all categories, needed for COCO
CATEGORY_TO_LONG_NAME = {
    CLASS: "Class",
    INTERFACE: "Interface",
    ENUMERATION: "Enumeration",
    ABSTRACT_CLASS: "Abstract Class",
    QUALIFIER: "Qualifier",
    N_ARY_ASSO_DIA: "N-Ary Association Diamond",
    LABEL: "Label",
    ASSOCIATION: "Association",
    AGGREGATION: "Aggregation",
    COMPOSITION: "Composition",
    EXTENSION: "Extension",
    DEPENDENCY: "Dependency",
    REALIZATION: "Realization"
}

ALL_CATEGORIES = yamlu.flatten(CATEGORY_GROUPS.values())

def _check_inconsistencies():
    n = (
            len(UML_NODE_CATEGORIES)
            + len(UML_EDGE_CATEGORIES)
            + len(UML_LABEL_CATEGORIES)
    )
    n_cats = sum(len(g) for g in CATEGORY_GROUPS.values())
    assert n == n_cats, f"{n}, {n_cats}"

    long_cat_names = set(CATEGORY_TO_LONG_NAME.keys())
    all_cats = set(yamlu.flatten(CATEGORY_GROUPS.values()))
    diff = all_cats.difference(long_cat_names)
    assert len(diff) == 0, diff


_check_inconsistencies()