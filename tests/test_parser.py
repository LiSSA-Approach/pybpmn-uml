from pathlib import Path

from pybpmn.uml_parser import UmlParser


def test_parse_bpmn():
    resource_path = Path(__file__).resolve().parent / "resources"
    bpmn_path = resource_path / "umlDiagram.bpmn"
    img_path = resource_path / "umlDiagram.jpeg"

    parser = UmlParser()
    ai = parser.parse_bpmn_img(bpmn_path, img_path)
    assert len(ai.annotations) > 0
    assert ai.filename == img_path.name
