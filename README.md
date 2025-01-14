![run_tests workflow](https://github.com/dwslab/pybpmn/actions/workflows/run_tests.yaml/badge.svg)

# pybpmn-uml 

This fork aims to extend [pybpmn](https://github.com/dwslab/pybpmn) to handle UML class diagram images annotated with the [uml-image-annotator](https://github.com/LiSSA-Approach/uml-image-annotator) and to convert them into a [COCO] dataset.

This repository also provides an [example dataset](./example-dataset) consisting of 1 hand-sketched UML class diagram and its corresponding BPMN XML file to showcase how to be converted UML data needs to be structured.
In this example, they are used for training, test and validation at the same time. 

The [demo.ipynb](./notebooks/demo.ipynb) Jupyter notebook can still be used to visualize the extracted bounding boxes over a hand-sketched UML class diagram.

You can convert the example dataset into a [COCO] dataset by executing the [dump_coco.py](./scripts/dump_coco.py) script with the following command:
```shell
python scripts/dump_coco.py ./example-dataset/uml-dataset ./example-dataset/coco
```

It is also still possible to convert the [hdBPMN] dataset into a [COCO] dataset with the following command:
```shell
python scripts/dump_coco.py path/to/hdBPMN path/to/target/coco/directory/hdbpmn --mode=bpmn
```

[Installation](#installation), [Development](#development) and [Dependency Management](#dependency-management) hasn't changed.

## README of original repository - pybpmn

Starter code for using the [hdBPMN] dataset for diagram recognition research.

The [dump_coco.py](./scripts/dump_coco.py) script can be used to convert the images and BPMN XMLs into a [COCO] dataset.
COCO is a common format used in computer vision research to annotate the objects and keypoints in images.
```shell
python scripts/dump_coco.py path/to/hdBPMN path/to/target/coco/directory/hdbpmn
```

Moreover, the [demo.ipynb](./notebooks/demo.ipynb) Jupyter notebook can be used to visualize
(1) the extracted bounding boxes, keypoints, and relations,
and (2) the annotated BPMN diagram overlayed over the hand-drawn image.
Note that the latter requires the [bpmn-to-image] tool, which in turn requires a nodejs installation.

### Installation

In order to set up the necessary environment:

1. create an environment `pybpmn` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate pybpmn
   ```

### Development

> **_NOTE:_**  The conda environment will have pybpmn installed in editable mode.
> Some changes, e.g. in `setup.cfg`, might require you to run `pip install -e .` again.


Optional and needed only once after `git clone`:

1. install JupyterLab kernel
   ```
   python -m ipykernel install --user --name "${CONDA_DEFAULT_ENV}" --display-name "$(python -V) (${CONDA_DEFAULT_ENV})"
   ```

2. install several [pre-commit] git hooks with:
   ```bash
   pre-commit install
   # You might also want to run `pre-commit autoupdate`
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

<a name="dependency-management"></a>
### Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yml` for the exact reproduction of your
   environment with:
   ```bash
   conda env export -n pybpmn -f environment.lock.yml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yml` using:
   ```bash
   conda env update -f environment.lock.yml --prune
   ```
### Project Organization

```
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build system configuration. Do not change!
├── scripts                 <- Analysis and production scripts which import the
│                              actual Python package, e.g. train_model.py.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- Use `pip install -e .` to install for development or
│                              or create a distribution with `tox -e build`.
├── src
│   └── pybpmn              <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `py.test`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

### Note

This project has been set up using [PyScaffold] 4.0.1 and the [dsproject extension] 0.6.1.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
[bpmn-to-image]: https://github.com/bpmn-io/bpmn-to-image
[COCO]: https://cocodataset.org/#format-data
[hdBPMN]: https://github.com/dwslab/hdBPMN
