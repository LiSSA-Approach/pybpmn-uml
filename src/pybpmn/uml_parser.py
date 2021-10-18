import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

import numpy as np
import yamlu
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as Element
from yamlu.img import AnnotatedImage, Annotation, BoundingBox

from pybpmn import uml_syntax
from pybpmn.constants import (
    ARROW_NEXT_REL,
    ARROW_PREV_REL,
    ARROW_RELATIONS,
    BELONGS_TO_REL
)

from pybpmn.util import bounds_to_bb, to_int_or_float, get_omgdi_ns, parse_annotation_background_width

_logger = logging.getLogger(__name__)

BPMN_ATTRIB_TO_RELATION = {"sourceRef": ARROW_PREV_REL, "targetRef": ARROW_NEXT_REL}


def parse_bpmn_anns(bpmn_path: Path):
    return UmlParser().parse_bpmn_anns(bpmn_path)

# Slightly adjusted version of .parser.py to UML context
class UmlParser:
    def __init__(
            self,
            # TODO: These marker_min_widths need to be adjusted at some point
            marker_min_widths: dict = {
                uml_syntax.DEPENDENCY: 20,
                uml_syntax.EXTENSION: 20,
                uml_syntax.REALIZATION: 20,
                uml_syntax.ASSOCIATION: 20,
                uml_syntax.AGGREGATION: 50,
                uml_syntax.COMPOSITION: 50
            },
            img_max_size_ref: int = 1000,
            excluded_categories: Set[str] = None,
            link_belongs_rel_two_way: bool = False,
    ):
        """
        :param marker_min_widths: pad edge bounding boxes so that their w and h is at least marker_min_width of specific edge type
                             when the image is scaled to img_max_size_ref
        :param img_max_size_ref: reference image size to consider for marker_min_widths
        """
        self.marker_min_widths = marker_min_widths
        self.img_max_size_ref = img_max_size_ref
        self.excluded_categories = {} if excluded_categories is None else excluded_categories
        self.link_belongs_rel_two_way = link_belongs_rel_two_way

    def _is_included_ann(self, a: Annotation) -> bool:
        if a.category in self.excluded_categories:
            return False
        return True

    # noinspection PyPropertyAccess
    def parse_bpmn_img(self, bpmn_path: Path, img_path: Path) -> AnnotatedImage:
        """
        :param bpmn_path: path to the BPMN XML file
        :param img_path: path to the corresponding UML image
        """
        img = yamlu.read_img(img_path)
        img_w, img_h = img.size

        img_w_annotation = parse_annotation_background_width(bpmn_path)
        scale = img_w / img_w_annotation
        marker_min_widhts_scaled = {key: (value * max(img.size) / self.img_max_size_ref) for (key, value) in self.marker_min_widths.items()}

        try:
            anns = self.parse_bpmn_anns(bpmn_path)
            for a in anns:
                a.bb = a.bb.scale(scale)

                if a.category in uml_syntax.UML_EDGE_CATEGORIES:
                    marker_min_width = marker_min_widhts_scaled.get(a.category)
                    a.bb = a.bb.pad_min_size(
                        w_min=marker_min_width, h_min=marker_min_width
                    )

                if not a.bb.is_within_img(img_w, img_h):
                    _logger.debug(
                        "%s: clipping bb %s to img (%d,%d)",
                        bpmn_path.name,
                        a.bb,
                        img_w,
                        img_h,
                    )
                    a.bb = a.bb.clip_to_image(img_w, img_h)
            for a in anns:
                if "waypoints" in a:
                    a.waypoints = a.waypoints * scale

                    a.tail = a.waypoints[0]
                    a.head = a.waypoints[-1]
        except Exception as e:
            _logger.error("Error while processing: %s", bpmn_path)
            raise e

        anns = [a for a in anns if self._is_included_ann(a)]

        return AnnotatedImage(
            img_path.name,
            width=img.width,
            height=img.height,
            annotations=anns,
            img=img,
        )

    def parse_bpmn_anns(self, bpmn_path: Path) -> List[Annotation]:
        document = etree.parse(str(bpmn_path))
        root = document.getroot()

        id_to_obj = {}

        for collaboration in root.findall("collaboration", root.nsmap):
            id_to_obj.update(_create_id_to_obj_mapping(collaboration))

        for process in root.findall("process", root.nsmap):
            id_to_obj.update(_create_id_to_obj_mapping(process))

        diagram = root.find("bpmndi:BPMNDiagram", root.nsmap)
        plane = diagram[0]
        shapes = plane.findall("bpmndi:BPMNShape", plane.nsmap)
        shape_anns = yamlu.flatten(
            _shape_to_anns(shape, id_to_obj[shape.get("bpmnElement")])
            for shape in shapes
        )
        id_to_shape_ann = {a.id: a for a in shape_anns if a.category != uml_syntax.LABEL}

        edges = plane.findall("bpmndi:BPMNEdge", plane.nsmap)

        edge_anns = []
        for edge in edges:
            model_id = edge.get("bpmnElement")
            if model_id not in id_to_obj:
                raise ValueError(f"{bpmn_path}: {model_id} not in model element ids")
            edge_anns.append(_edge_to_anns(edge, id_to_obj[model_id], id_to_shape_ann))

        edge_anns = yamlu.flatten(edge_anns)

        anns = shape_anns + edge_anns
        self._link_belongs_rel_anns(anns)
        return anns

    def _link_belongs_rel_anns(self, anns):
        id_to_ann = {a.id: a for a in anns if a.category != uml_syntax.LABEL}

        belongs_anns = [a for a in anns if (a.category == uml_syntax.LABEL or a.category == uml_syntax.QUALIFIER)]

        for belongs_ann in belongs_anns:
            symb_ann = id_to_ann[belongs_ann.get(BELONGS_TO_REL)]
            belongs_ann.set(BELONGS_TO_REL, symb_ann)
            if self.link_belongs_rel_two_way:
                symb_ann.set(BELONGS_TO_REL, belongs_ann)


def get_tag_without_ns(element: Element):
    tag_str = element.tag
    return tag_str[tag_str.find("}") + 1:]


def get_category(bpmndi_element: Element, model_element: Element):
    """inverse operation of get_tag"""

    # remove namespace from tag
    category: str = get_tag_without_ns(model_element)

    assert category in uml_syntax.ALL_CATEGORIES, f"unknown category: {category}"

    return category


def _create_id_to_obj_mapping(element):
    id_to_obj = {}
    to_visit = [element]
    while len(to_visit) != 0:
        element = to_visit.pop()
        for child in element:
            to_visit.append(child)
            if child.get("id") is not None:
                id_to_obj[child.get("id")] = child
    return id_to_obj


def _edge_to_anns(edge: Element, model_element: Element, id_to_shape_ann: Dict[str, Annotation]):
    """
    Parses edges (see uml_syntax.BPMNDI_EDGE_CATEGORIES)
    :param edge the BPMNDI edge element
    :param model_element the corresponding model element
    (this is relevant for arrows where the waypoints don't include the width/height of the arrow head)
    Example edge:
     <bpmndi:BPMNEdge id="Association_04k7nxy_di" bpmnElement="Association_04k7nxy_di">
           <omgdi:waypoint x="380" y="120" />
           <omgdi:waypoint x="391" y="120" />
           <omgdi:waypoint x="391" y="124" />
           <omgdi:waypoint x="402" y="124" />
     </bpmndi:BPMNEdge>
     Examples model_element: see parse_edge_attribs()
    """
    category = get_category(edge, model_element)

    ns = get_omgdi_ns(edge)
    waypoints = np.array(
        [[to_int_or_float(wp.get("x")), to_int_or_float(wp.get("y"))] for wp in
         edge.findall(f"{ns}:waypoint", edge.nsmap)]
    )
    bb = BoundingBox.from_points(waypoints, allow_neg_coord=True)

    attrib = _parse_edge_attribs(model_element)
    # create Annotation links instead of linking through id
    for rel in ARROW_RELATIONS:
        attrib[rel] = id_to_shape_ann[attrib[rel]]
    anns = [Annotation(category, bb, waypoints=waypoints, **attrib)]

    return anns


def _shape_to_anns(shape: Element, model_element: Element) -> List[Annotation]:
    category = get_category(shape, model_element)

    shape_ann = Annotation(category, bb=_child_bounds_to_bb(shape), **model_element.attrib)
    if get_tag_without_ns(model_element) == uml_syntax.LABEL:
        text_el = model_element.find("text", model_element.nsmap)
        if text_el is not None:
            shape_ann.name = text_el.text

    anns = [shape_ann]

    return anns


def _parse_edge_attribs(model_element):
    attrib = dict(model_element.attrib)
    tag = get_tag_without_ns(model_element)

    if tag in uml_syntax.UML_EDGE_CATEGORIES:
        for old, new in BPMN_ATTRIB_TO_RELATION.items():
            attrib[new] = attrib.pop(old)
    else:
        raise ValueError(f"Unknown edge tag: {tag}")

    return attrib


def _child_bounds_to_bb(element: Element) -> BoundingBox:
    bounds = element.find("omgdc:Bounds", element.nsmap)
    return bounds_to_bb(bounds)