import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

import yamlu
from yamlu.coco import Dataset
from yamlu.img import AnnotatedImage

from pybpmn.constants import ARROW_KEYPOINT_FIELDS, RELATIONS, UNITE_CATEGORIES
from pybpmn.uml_parser import UmlParser
from pybpmn.uml_syntax import (
    UML_EDGE_CATEGORIES,
    CATEGORY_GROUPS,
    CATEGORY_TO_LONG_NAME,
    CATEGORY_TRANSLATE_DICT
)

_logger = logging.getLogger(__name__)

# Slightly adjusted version of .dataset.py to UML context
class UmlDataset(Dataset):
    def __init__(
            self,
            uml_dataset_root: Union[Path, str],
            coco_dataset_root: Union[Path, str],
            unite_categories: bool = UNITE_CATEGORIES,
            category_translate_dict: Dict[str, str] = CATEGORY_TRANSLATE_DICT,
            keypoint_fields: List[str] = ARROW_KEYPOINT_FIELDS,
            relation_fields: List[str] = RELATIONS,
            **parser_kwargs
    ):
        uml_dataset_root = Path(uml_dataset_root) if isinstance(uml_dataset_root, str) else uml_dataset_root
        assert uml_dataset_root.exists(), f"{uml_dataset_root} does not exist!"
        self.uml_dataset_root = uml_dataset_root.resolve() if not uml_dataset_root.is_absolute() else uml_dataset_root

        self.unite_categories = unite_categories
        self.category_translate_dict = category_translate_dict

        self.split_to_bpmn_paths = self.get_split_to_bpmn_paths()
        self.bpmn_parser = UmlParser(**parser_kwargs)
        super().__init__(
            dataset_path=coco_dataset_root,
            split_n_imgs={s: len(ps) for s, ps in self.split_to_bpmn_paths.items()},
            coco_categories=self._create_coco_categories(),
            keypoint_fields=keypoint_fields,
            relation_fields=relation_fields,
        )
        _logger.info(
            "Parsed UML dataset with %d images: %s",
            sum(self.split_n_imgs.values()),
            self.split_n_imgs,
        )

    def get_split_ann_img(self, split: str, idx: int) -> AnnotatedImage:
        bpmn_path = self.split_to_bpmn_paths[split][idx]

        img_path = self.get_img_path(bpmn_path.stem)
        ai = self.bpmn_parser.parse_bpmn_img(bpmn_path, img_path)

        # "id" is reserved in coco, therefore use other field name
        for a in ai.annotations:
            if "id" in a:
                a.bpmn_id = a.id
            # Unite categories defined in ./uml_syntax.py if Setting "UNITE_CATEGORIES" in ./constants.py is True
            if self.unite_categories and a.category in self.category_translate_dict.keys():
                a.category = self.category_translate_dict[a.category]

        return ai

    @property
    def annotations_root(self):
        return self.uml_dataset_root / "data" / "annotations"

    @property
    def images_root(self):
        return self.uml_dataset_root / "data" / "images"

    def get_img_path(self, img_id: str):
        img_paths = yamlu.glob(self.images_root, f"{img_id}.*")
        assert len(img_paths) == 1, f"{img_id}: {img_paths}"
        return img_paths[0]

    def _get_all_bpmn_paths(self) -> List[Path]:
        bpmn_paths = yamlu.glob(self.annotations_root, "**/*.bpmn")
        assert len(bpmn_paths) > 0, f"Found no bpmn files under {self.annotations_root}"

        return bpmn_paths

    # UML-Extension: Difference to normal hdBpmn Dataset => only split by filename, not by writer
    def _parse_filename_to_split(self) -> Dict[str, str]:
        csv_path = self.uml_dataset_root / "data" / "filename_split.csv"

        with csv_path.open() as f:
            # noinspection PyTypeChecker
            filename_to_split = dict(line.rstrip().split(",") for line in f)

        # delete header row
        del filename_to_split["filename"]

        return filename_to_split

    def get_split_to_bpmn_paths(self) -> Dict[str, List[Path]]:
        filename_to_split = self._parse_filename_to_split()

        split_to_bpmn_paths = defaultdict(list)
        bpmn_paths = self._get_all_bpmn_paths()
        for bpmn_path in bpmn_paths:
            split = filename_to_split[bpmn_path.stem]
            split_to_bpmn_paths[split].append(bpmn_path)

        return split_to_bpmn_paths

    def _create_coco_categories(self):
        seen_cats = set()

        i = 0
        coco_categories = []
        for supercategory, categories in CATEGORY_GROUPS.items():
            for category in categories:
                if category in self.bpmn_parser.excluded_categories:
                    continue
                if self.unite_categories:
                    category = self.category_translate_dict.get(category, category)
                if category in seen_cats:
                    continue
                seen_cats.add(category)

                coco_cat = {
                    "supercategory": supercategory,
                    "id": i,
                    "name": category,
                    "longname": CATEGORY_TO_LONG_NAME[category],
                }
                if category in UML_EDGE_CATEGORIES:
                    coco_cat["keypoints"] = ["head", "tail"]
                coco_categories.append(coco_cat)
                i += 1

        return coco_categories