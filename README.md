# SKILLCRAWL 
### *Crawler written using the esco_skill_extractor (PetraSkill) library for identifying relevant skills in university lessons, printing URLs and skill keywords*

### Not implemented: Compatibility with other syllabus outside EU.

## Running the crawler:
```
python skillcrawl.py
```
This brings you to the main menu, used as a guide to understand what this crawler can do!

<img width="842" alt="image" src="https://github.com/user-attachments/assets/97377236-db57-4357-8060-87beb3201d2e" />

Despite the existence of a menu, you can run the program directly from cmd, such as:
```
python skillcrawl.py skills algorithms
```
<img width="773" alt="image" src="https://github.com/user-attachments/assets/eaaf7994-837b-40cb-a691-c47cbe3ecbde" />

Furthermore, it bypasses the need to only have URLs as a mean to access skills, as it can directly print them.

<img width="562" alt="image" src="https://github.com/user-attachments/assets/7b6b3edd-85bc-4ee5-b780-62d7eaaab58c" />

------------------------------------------------------------------
# OLD GUIDE - Old Documentation! See above for latest change ⚠️
### Crawler Setup on Kali Linux using `nesta ojd_daps_skills` Library ⭐

> ⚠️ **Warning:**
> 
> This version (and the ojd_daps_skills==1.0.2) is incompatible with Python 3.11 and 3.12.

~~This crawler version (0.1.0) is incomplete and will be improved in the way it handles regex!~~
> ⚠️ Crawler v0.2.0 now handles regex correctly!
> [LATEST] Crawler v0.3.0 now shows descriptions for each lesson

## Running the crawler:
```
python test_analyzer.py
```
This method should be used mainly for finding if the crawler splits the information correctly!
Any skill matching will be done by using ```poetry run pytest test_analyzer.py``` *(implemented in the next version)*

### IMPORTANT Compatibility Note: Problems with PyDantic and SpaCy!
- If you encounter compatibility errors, downgrade to Python 3.10, which has no issues. I discovered that after realizing the problem it has with ImpImporter!

## What does it do?
This script (for now) is designed to find and retrieve a PDF by link, extract text from the PDF, split the content by semesters and lessons and then identify relevant skills mentioned in each lesson in a university setting.

### Functions
> - extract_text_from_pdf(pdf_file_path: str) -> str : Extracts and returns the text from a given PDF file or from a UR
> - split_by_semester(text: str) -> List[str]: Splits the text into semesters based on semester headings (example. 1st Semester") The function assumes that a "Course Outlines" (based on the provided pdf it was based on) exists and starts splitting after this section is found.
> - split_by_lessons(semester_text: str) -> Dict[str, str] : Splits text into lessons (regex is still in development!)
> - extract_skills_for_lessons(lessons: Dict[str, str], skills_extractor: ExtractSkills) -> Dict[str, List[Dict]]: Uses the ExtractSkills class to extract skills from the text of each lesson.

## Installation Guide for Python 3.10 (Recommended for version 1.0.2)

> ⚠️ **Warning:**
> Ensure first that pipx and pip is installed!

Begin with these commands:
```
pipx install poetry
poetry shell
poetry install
pip install ojd-daps-skills
python -m spacy download en_core_web_sm
```
Choose a folder to begin creating your Poetry project and run this command:
```
poetry init
```
It will guide you through the process of building your first project. 
-- When the option to type in the Python version appears, type 3.10 !

Continue with installing pytest:
```
pip install pytest
```

Put all your test_xxxx.py or xxxx_test.py files in the test folder inside your project

Execute your tests by using this command:
```
poetry run pytest tests/
```

- Make sure it meets [these dependencies](#Library-Dependencies)!
> ⚠️ **HINT:**
> In case you are having issues with the library dependencies, install pipdeptree and check the dependencies.
> Otherwise, by running pip check or poetry show <library-name>, see what problems are occuring.

------------------------------

# NOT RECOMMENDED!

## Installation Guide for Python 3.12 - 3.11 (Note: Not compatible with version 1.0.2!)

### Step 1: Install pipx
- Begin by installing pipx to manage your Python packages.

### Step 2: Install Required Packages
- Run the necessary installation commands as per your environment setup.
- Ensure compatibility between SpaCy and Pydantic by using SpaCy 3.4 with the latest Pydantic.

### Step 3: Install NLTK
- Install NLTK to handle natural language processing tasks.

### Step 4: Resolve WordNet Issues
- NLTK's WordNet data might present issues when installed with `--user` in a virtual environment managed by Poetry. To resolve this, remove any existing NLTK data:

```bash
rm -rf /home/mfol/nltk_data
```

### Step 5: Reinstall NLTK
- If you encounter issues, reinstall NLTK using Poetry:

```bash
poetry run pip uninstall nltk
poetry run pip install nltk
```

### Step 6: Manually Download WordNet Data
- Manually download and install the WordNet data to avoid dependency issues:

```bash
wget https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
```

- Extract the WordNet data to your `nltk_data` directory:

```bash
mkdir -p /home/mfol/nltk_data/corpora
unzip wordnet.zip -d /home/mfol/nltk_data/corpora/
```

### Step 7: Verify Installation
- Ensure everything is working by running the Python shell and testing WordNet:

```bash
poetry run python
```

- In the Python shell:

```python
import nltk
nltk.data.path.append('/home/mfol/nltk_data')
from nltk.corpus import wordnet as wn
wn.synsets('dog')
```
### After these steps, ensure to continue the installation like in the above Python 3.10 tutorial!

-------------------------------------

# Library Dependencies 
## for Python 3.10
```
* ojd_daps_skills==1.0.2
 - tqdm [required: ==4.64.0, installed: 4.66.5]
------------------------------------------------------------------------
crawler==0.1.0
└── nltk [required: >=3.9,<4.0, installed: 3.9]
    ├── click [required: Any, installed: 8.1.7]
    ├── joblib [required: Any, installed: 1.4.2]
    ├── regex [required: >=2021.8.3, installed: 2024.7.24]
    └── tqdm [required: Any, installed: 4.66.5]
en-core-web-sm==3.4.1
└── spacy [required: >=3.4.0,<3.5.0, installed: 3.4.0]
    ├── catalogue [required: >=2.0.6,<2.1.0, installed: 2.0.10]
    ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
    ├── Jinja2 [required: Any, installed: 3.1.4]
    │   └── MarkupSafe [required: >=2.0, installed: 2.1.5]
    ├── langcodes [required: >=3.2.0,<4.0.0, installed: 3.4.0]
    │   └── language_data [required: >=1.2, installed: 1.2.0]
    │       └── marisa-trie [required: >=0.7.7, installed: 1.2.0]
    │           └── setuptools [required: Any, installed: 72.2.0]
    ├── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
    ├── numpy [required: >=1.15.0, installed: 1.24.4]
    ├── packaging [required: >=20.0, installed: 24.1]
    ├── pathy [required: >=0.3.5, installed: 0.11.0]
    │   ├── pathlib_abc [required: ==0.1.1, installed: 0.1.1]
    │   ├── smart-open [required: >=5.2.1,<7.0.0, installed: 6.4.0]
    │   └── typer [required: >=0.3.0,<1.0.0, installed: 0.4.1]
    │       └── click [required: >=7.1.1,<9.0.0, installed: 8.1.7]
    ├── preshed [required: >=3.0.2,<3.1.0, installed: 3.0.9]
    │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
    │   └── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
    ├── pydantic [required: >=1.7.4,<1.10.0,!=1.8.1,!=1.8, installed: 1.9.2]
    │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
    ├── requests [required: >=2.13.0,<3.0.0, installed: 2.32.3]
    │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
    │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
    │   ├── idna [required: >=2.5,<4, installed: 3.7]
    │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
    ├── setuptools [required: Any, installed: 72.2.0]
    ├── spacy-legacy [required: >=3.0.9,<3.1.0, installed: 3.0.12]
    ├── spacy-loggers [required: >=1.0.0,<2.0.0, installed: 1.0.5]
    ├── srsly [required: >=2.4.3,<3.0.0, installed: 2.4.8]
    │   └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
    ├── thinc [required: >=8.1.0,<8.2.0, installed: 8.1.12]
    │   ├── blis [required: >=0.7.8,<0.8.0, installed: 0.7.11]
    │   │   └── numpy [required: >=1.19.0, installed: 1.24.4]
    │   ├── catalogue [required: >=2.0.4,<2.1.0, installed: 2.0.10]
    │   ├── confection [required: >=0.0.1,<1.0.0, installed: 0.1.5]
    │   │   ├── pydantic [required: >=1.7.4,<3.0.0,!=1.8.1,!=1.8, installed: 1.9.2]
    │   │   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
    │   │   └── srsly [required: >=2.4.0,<3.0.0, installed: 2.4.8]
    │   │       └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
    │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
    │   ├── murmurhash [required: >=1.0.2,<1.1.0, installed: 1.0.10]
    │   ├── numpy [required: >=1.19.0, installed: 1.24.4]
    │   ├── packaging [required: >=20.0, installed: 24.1]
    │   ├── preshed [required: >=3.0.2,<3.1.0, installed: 3.0.9]
    │   │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
    │   │   └── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
    │   ├── pydantic [required: >=1.7.4,<3.0.0,!=1.8.1,!=1.8, installed: 1.9.2]
    │   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
    │   ├── setuptools [required: Any, installed: 72.2.0]
    │   ├── srsly [required: >=2.4.0,<3.0.0, installed: 2.4.8]
    │   │   └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
    │   └── wasabi [required: >=0.8.1,<1.2.0, installed: 0.10.1]
    ├── tqdm [required: >=4.38.0,<5.0.0, installed: 4.66.5]
    ├── typer [required: >=0.3.0,<0.5.0, installed: 0.4.1]
    │   └── click [required: >=7.1.1,<9.0.0, installed: 8.1.7]
    └── wasabi [required: >=0.9.1,<1.1.0, installed: 0.10.1]
ojd_daps_skills==1.0.2
├── boto3 [required: ==1.21.21, installed: 1.21.21]
│   ├── botocore [required: >=1.24.21,<1.25.0, installed: 1.24.21]
│   │   ├── jmespath [required: >=0.7.1,<2.0.0, installed: 1.0.1]
│   │   ├── python-dateutil [required: >=2.1,<3.0.0, installed: 2.9.0.post0]
│   │   │   └── six [required: >=1.5, installed: 1.16.0]
│   │   └── urllib3 [required: >=1.25.4,<1.27, installed: 1.26.19]
│   ├── jmespath [required: >=0.7.1,<2.0.0, installed: 1.0.1]
│   └── s3transfer [required: >=0.5.0,<0.6.0, installed: 0.5.2]
│       └── botocore [required: >=1.12.36,<2.0a.0, installed: 1.24.21]
│           ├── jmespath [required: >=0.7.1,<2.0.0, installed: 1.0.1]
│           ├── python-dateutil [required: >=2.1,<3.0.0, installed: 2.9.0.post0]
│           │   └── six [required: >=1.5, installed: 1.16.0]
│           └── urllib3 [required: >=1.25.4,<1.27, installed: 1.26.19]
├── filelock [required: ==3.7.1, installed: 3.7.1]
├── nervaluate [required: ==0.1.8, installed: 0.1.8]
├── numpy [required: ==1.24.4, installed: 1.24.4]
├── pandas [required: ==1.3.5, installed: 1.3.5]
│   ├── numpy [required: >=1.21.0, installed: 1.24.4]
│   ├── python-dateutil [required: >=2.7.3, installed: 2.9.0.post0]
│   │   └── six [required: >=1.5, installed: 1.16.0]
│   └── pytz [required: >=2017.3, installed: 2024.1]
├── s3fs [required: ==2022.5.0, installed: 2022.5.0]
│   ├── aiobotocore [required: ~=2.3.0, installed: 2.3.4]
│   │   ├── aiohttp [required: >=3.3.1, installed: 3.10.4]
│   │   │   ├── aiohappyeyeballs [required: >=2.3.0, installed: 2.3.7]
│   │   │   ├── aiosignal [required: >=1.1.2, installed: 1.3.1]
│   │   │   │   └── frozenlist [required: >=1.1.0, installed: 1.4.1]
│   │   │   ├── async-timeout [required: >=4.0,<5.0, installed: 4.0.3]
│   │   │   ├── attrs [required: >=17.3.0, installed: 24.2.0]
│   │   │   ├── frozenlist [required: >=1.1.1, installed: 1.4.1]
│   │   │   ├── multidict [required: >=4.5,<7.0, installed: 6.0.5]
│   │   │   └── yarl [required: >=1.0,<2.0, installed: 1.9.4]
│   │   │       ├── idna [required: >=2.0, installed: 3.7]
│   │   │       └── multidict [required: >=4.0, installed: 6.0.5]
│   │   ├── aioitertools [required: >=0.5.1, installed: 0.11.0]
│   │   ├── botocore [required: >=1.24.21,<1.24.22, installed: 1.24.21]
│   │   │   ├── jmespath [required: >=0.7.1,<2.0.0, installed: 1.0.1]
│   │   │   ├── python-dateutil [required: >=2.1,<3.0.0, installed: 2.9.0.post0]
│   │   │   │   └── six [required: >=1.5, installed: 1.16.0]
│   │   │   └── urllib3 [required: >=1.25.4,<1.27, installed: 1.26.19]
│   │   └── wrapt [required: >=1.10.10, installed: 1.16.0]
│   ├── aiohttp [required: <=4, installed: 3.10.4]
│   │   ├── aiohappyeyeballs [required: >=2.3.0, installed: 2.3.7]
│   │   ├── aiosignal [required: >=1.1.2, installed: 1.3.1]
│   │   │   └── frozenlist [required: >=1.1.0, installed: 1.4.1]
│   │   ├── async-timeout [required: >=4.0,<5.0, installed: 4.0.3]
│   │   ├── attrs [required: >=17.3.0, installed: 24.2.0]
│   │   ├── frozenlist [required: >=1.1.1, installed: 1.4.1]
│   │   ├── multidict [required: >=4.5,<7.0, installed: 6.0.5]
│   │   └── yarl [required: >=1.0,<2.0, installed: 1.9.4]
│   │       ├── idna [required: >=2.0, installed: 3.7]
│   │       └── multidict [required: >=4.0, installed: 6.0.5]
│   └── fsspec [required: ==2022.5.0, installed: 2022.5.0]
├── scikit-learn [required: ==1.3.1, installed: 1.3.1]
│   ├── joblib [required: >=1.1.1, installed: 1.4.2]
│   ├── numpy [required: >=1.17.3,<2.0, installed: 1.24.4]
│   ├── scipy [required: >=1.5.0, installed: 1.10.1]
│   │   └── numpy [required: >=1.19.5,<1.27.0, installed: 1.24.4]
│   └── threadpoolctl [required: >=2.0.0, installed: 3.5.0]
├── scipy [required: ==1.10.1, installed: 1.10.1]
│   └── numpy [required: >=1.19.5,<1.27.0, installed: 1.24.4]
├── sentence-transformers [required: ==2.2.2, installed: 2.2.2]
│   ├── huggingface-hub [required: >=0.4.0, installed: 0.17.3]
│   │   ├── filelock [required: Any, installed: 3.7.1]
│   │   ├── fsspec [required: Any, installed: 2022.5.0]
│   │   ├── packaging [required: >=20.9, installed: 24.1]
│   │   ├── PyYAML [required: >=5.1, installed: 6.0.2]
│   │   ├── requests [required: Any, installed: 2.32.3]
│   │   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│   │   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│   │   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│   │   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│   │   ├── tqdm [required: >=4.42.1, installed: 4.66.5]
│   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│   ├── nltk [required: Any, installed: 3.9]
│   │   ├── click [required: Any, installed: 8.1.7]
│   │   ├── joblib [required: Any, installed: 1.4.2]
│   │   ├── regex [required: >=2021.8.3, installed: 2024.7.24]
│   │   └── tqdm [required: Any, installed: 4.66.5]
│   ├── numpy [required: Any, installed: 1.24.4]
│   ├── scikit-learn [required: Any, installed: 1.3.1]
│   │   ├── joblib [required: >=1.1.1, installed: 1.4.2]
│   │   ├── numpy [required: >=1.17.3,<2.0, installed: 1.24.4]
│   │   ├── scipy [required: >=1.5.0, installed: 1.10.1]
│   │   │   └── numpy [required: >=1.19.5,<1.27.0, installed: 1.24.4]
│   │   └── threadpoolctl [required: >=2.0.0, installed: 3.5.0]
│   ├── scipy [required: Any, installed: 1.10.1]
│   │   └── numpy [required: >=1.19.5,<1.27.0, installed: 1.24.4]
│   ├── sentencepiece [required: Any, installed: 0.2.0]
│   ├── torch [required: >=1.6.0, installed: 2.1.2]
│   │   ├── filelock [required: Any, installed: 3.7.1]
│   │   ├── fsspec [required: Any, installed: 2022.5.0]
│   │   ├── Jinja2 [required: Any, installed: 3.1.4]
│   │   │   └── MarkupSafe [required: >=2.0, installed: 2.1.5]
│   │   ├── networkx [required: Any, installed: 3.3]
│   │   ├── nvidia-cublas-cu12 [required: ==12.1.3.1, installed: 12.1.3.1]
│   │   ├── nvidia-cuda-cupti-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │   ├── nvidia-cuda-nvrtc-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │   ├── nvidia-cuda-runtime-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │   ├── nvidia-cudnn-cu12 [required: ==8.9.2.26, installed: 8.9.2.26]
│   │   │   └── nvidia-cublas-cu12 [required: Any, installed: 12.1.3.1]
│   │   ├── nvidia-cufft-cu12 [required: ==11.0.2.54, installed: 11.0.2.54]
│   │   ├── nvidia-curand-cu12 [required: ==10.3.2.106, installed: 10.3.2.106]
│   │   ├── nvidia-cusolver-cu12 [required: ==11.4.5.107, installed: 11.4.5.107]
│   │   │   ├── nvidia-cublas-cu12 [required: Any, installed: 12.1.3.1]
│   │   │   ├── nvidia-cusparse-cu12 [required: Any, installed: 12.1.0.106]
│   │   │   │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │   │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │   ├── nvidia-cusparse-cu12 [required: ==12.1.0.106, installed: 12.1.0.106]
│   │   │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │   ├── nvidia-nccl-cu12 [required: ==2.18.1, installed: 2.18.1]
│   │   ├── nvidia-nvtx-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │   ├── sympy [required: Any, installed: 1.13.2]
│   │   │   └── mpmath [required: >=1.1.0,<1.4, installed: 1.3.0]
│   │   ├── triton [required: ==2.1.0, installed: 2.1.0]
│   │   │   └── filelock [required: Any, installed: 3.7.1]
│   │   └── typing_extensions [required: Any, installed: 4.5.0]
│   ├── torchvision [required: Any, installed: 0.16.2]
│   │   ├── numpy [required: Any, installed: 1.24.4]
│   │   ├── pillow [required: >=5.3.0,!=8.3.*, installed: 10.4.0]
│   │   ├── requests [required: Any, installed: 2.32.3]
│   │   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│   │   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│   │   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│   │   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│   │   └── torch [required: ==2.1.2, installed: 2.1.2]
│   │       ├── filelock [required: Any, installed: 3.7.1]
│   │       ├── fsspec [required: Any, installed: 2022.5.0]
│   │       ├── Jinja2 [required: Any, installed: 3.1.4]
│   │       │   └── MarkupSafe [required: >=2.0, installed: 2.1.5]
│   │       ├── networkx [required: Any, installed: 3.3]
│   │       ├── nvidia-cublas-cu12 [required: ==12.1.3.1, installed: 12.1.3.1]
│   │       ├── nvidia-cuda-cupti-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │       ├── nvidia-cuda-nvrtc-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │       ├── nvidia-cuda-runtime-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │       ├── nvidia-cudnn-cu12 [required: ==8.9.2.26, installed: 8.9.2.26]
│   │       │   └── nvidia-cublas-cu12 [required: Any, installed: 12.1.3.1]
│   │       ├── nvidia-cufft-cu12 [required: ==11.0.2.54, installed: 11.0.2.54]
│   │       ├── nvidia-curand-cu12 [required: ==10.3.2.106, installed: 10.3.2.106]
│   │       ├── nvidia-cusolver-cu12 [required: ==11.4.5.107, installed: 11.4.5.107]
│   │       │   ├── nvidia-cublas-cu12 [required: Any, installed: 12.1.3.1]
│   │       │   ├── nvidia-cusparse-cu12 [required: Any, installed: 12.1.0.106]
│   │       │   │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │       │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │       ├── nvidia-cusparse-cu12 [required: ==12.1.0.106, installed: 12.1.0.106]
│   │       │   └── nvidia-nvjitlink-cu12 [required: Any, installed: 12.6.20]
│   │       ├── nvidia-nccl-cu12 [required: ==2.18.1, installed: 2.18.1]
│   │       ├── nvidia-nvtx-cu12 [required: ==12.1.105, installed: 12.1.105]
│   │       ├── sympy [required: Any, installed: 1.13.2]
│   │       │   └── mpmath [required: >=1.1.0,<1.4, installed: 1.3.0]
│   │       ├── triton [required: ==2.1.0, installed: 2.1.0]
│   │       │   └── filelock [required: Any, installed: 3.7.1]
│   │       └── typing_extensions [required: Any, installed: 4.5.0]
│   ├── tqdm [required: Any, installed: 4.66.5]
│   └── transformers [required: >=4.6.0,<5.0.0, installed: 4.33.3]
│       ├── filelock [required: Any, installed: 3.7.1]
│       ├── huggingface-hub [required: >=0.15.1,<1.0, installed: 0.17.3]
│       │   ├── filelock [required: Any, installed: 3.7.1]
│       │   ├── fsspec [required: Any, installed: 2022.5.0]
│       │   ├── packaging [required: >=20.9, installed: 24.1]
│       │   ├── PyYAML [required: >=5.1, installed: 6.0.2]
│       │   ├── requests [required: Any, installed: 2.32.3]
│       │   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│       │   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│       │   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│       │   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│       │   ├── tqdm [required: >=4.42.1, installed: 4.66.5]
│       │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│       ├── numpy [required: >=1.17, installed: 1.24.4]
│       ├── packaging [required: >=20.0, installed: 24.1]
│       ├── PyYAML [required: >=5.1, installed: 6.0.2]
│       ├── regex [required: !=2019.12.17, installed: 2024.7.24]
│       ├── requests [required: Any, installed: 2.32.3]
│       │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│       │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│       │   ├── idna [required: >=2.5,<4, installed: 3.7]
│       │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│       ├── safetensors [required: >=0.3.1, installed: 0.4.4]
│       ├── tokenizers [required: >=0.11.1,<0.14,!=0.11.3, installed: 0.12.1]
│       └── tqdm [required: >=4.27, installed: 4.66.5]
├── sh [required: ==1.14.2, installed: 1.14.2]
├── spacy [required: ==3.4.0, installed: 3.4.0]
│   ├── catalogue [required: >=2.0.6,<2.1.0, installed: 2.0.10]
│   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
│   ├── Jinja2 [required: Any, installed: 3.1.4]
│   │   └── MarkupSafe [required: >=2.0, installed: 2.1.5]
│   ├── langcodes [required: >=3.2.0,<4.0.0, installed: 3.4.0]
│   │   └── language_data [required: >=1.2, installed: 1.2.0]
│   │       └── marisa-trie [required: >=0.7.7, installed: 1.2.0]
│   │           └── setuptools [required: Any, installed: 72.2.0]
│   ├── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
│   ├── numpy [required: >=1.15.0, installed: 1.24.4]
│   ├── packaging [required: >=20.0, installed: 24.1]
│   ├── pathy [required: >=0.3.5, installed: 0.11.0]
│   │   ├── pathlib_abc [required: ==0.1.1, installed: 0.1.1]
│   │   ├── smart-open [required: >=5.2.1,<7.0.0, installed: 6.4.0]
│   │   └── typer [required: >=0.3.0,<1.0.0, installed: 0.4.1]
│   │       └── click [required: >=7.1.1,<9.0.0, installed: 8.1.7]
│   ├── preshed [required: >=3.0.2,<3.1.0, installed: 3.0.9]
│   │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
│   │   └── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
│   ├── pydantic [required: >=1.7.4,<1.10.0,!=1.8.1,!=1.8, installed: 1.9.2]
│   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│   ├── requests [required: >=2.13.0,<3.0.0, installed: 2.32.3]
│   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│   ├── setuptools [required: Any, installed: 72.2.0]
│   ├── spacy-legacy [required: >=3.0.9,<3.1.0, installed: 3.0.12]
│   ├── spacy-loggers [required: >=1.0.0,<2.0.0, installed: 1.0.5]
│   ├── srsly [required: >=2.4.3,<3.0.0, installed: 2.4.8]
│   │   └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
│   ├── thinc [required: >=8.1.0,<8.2.0, installed: 8.1.12]
│   │   ├── blis [required: >=0.7.8,<0.8.0, installed: 0.7.11]
│   │   │   └── numpy [required: >=1.19.0, installed: 1.24.4]
│   │   ├── catalogue [required: >=2.0.4,<2.1.0, installed: 2.0.10]
│   │   ├── confection [required: >=0.0.1,<1.0.0, installed: 0.1.5]
│   │   │   ├── pydantic [required: >=1.7.4,<3.0.0,!=1.8.1,!=1.8, installed: 1.9.2]
│   │   │   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│   │   │   └── srsly [required: >=2.4.0,<3.0.0, installed: 2.4.8]
│   │   │       └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
│   │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
│   │   ├── murmurhash [required: >=1.0.2,<1.1.0, installed: 1.0.10]
│   │   ├── numpy [required: >=1.19.0, installed: 1.24.4]
│   │   ├── packaging [required: >=20.0, installed: 24.1]
│   │   ├── preshed [required: >=3.0.2,<3.1.0, installed: 3.0.9]
│   │   │   ├── cymem [required: >=2.0.2,<2.1.0, installed: 2.0.8]
│   │   │   └── murmurhash [required: >=0.28.0,<1.1.0, installed: 1.0.10]
│   │   ├── pydantic [required: >=1.7.4,<3.0.0,!=1.8.1,!=1.8, installed: 1.9.2]
│   │   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│   │   ├── setuptools [required: Any, installed: 72.2.0]
│   │   ├── srsly [required: >=2.4.0,<3.0.0, installed: 2.4.8]
│   │   │   └── catalogue [required: >=2.0.3,<2.1.0, installed: 2.0.10]
│   │   └── wasabi [required: >=0.8.1,<1.2.0, installed: 0.10.1]
│   ├── tqdm [required: >=4.38.0,<5.0.0, installed: 4.66.5]
│   ├── typer [required: >=0.3.0,<0.5.0, installed: 0.4.1]
│   │   └── click [required: >=7.1.1,<9.0.0, installed: 8.1.7]
│   └── wasabi [required: >=0.9.1,<1.1.0, installed: 0.10.1]
├── toolz [required: ==0.12.0, installed: 0.12.0]
├── tqdm [required: ==4.64.0, installed: 4.66.5]
├── transformers [required: ==4.33.3, installed: 4.33.3]
│   ├── filelock [required: Any, installed: 3.7.1]
│   ├── huggingface-hub [required: >=0.15.1,<1.0, installed: 0.17.3]
│   │   ├── filelock [required: Any, installed: 3.7.1]
│   │   ├── fsspec [required: Any, installed: 2022.5.0]
│   │   ├── packaging [required: >=20.9, installed: 24.1]
│   │   ├── PyYAML [required: >=5.1, installed: 6.0.2]
│   │   ├── requests [required: Any, installed: 2.32.3]
│   │   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│   │   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│   │   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│   │   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│   │   ├── tqdm [required: >=4.42.1, installed: 4.66.5]
│   │   └── typing_extensions [required: >=3.7.4.3, installed: 4.5.0]
│   ├── numpy [required: >=1.17, installed: 1.24.4]
│   ├── packaging [required: >=20.0, installed: 24.1]
│   ├── PyYAML [required: >=5.1, installed: 6.0.2]
│   ├── regex [required: !=2019.12.17, installed: 2024.7.24]
│   ├── requests [required: Any, installed: 2.32.3]
│   │   ├── certifi [required: >=2017.4.17, installed: 2024.7.4]
│   │   ├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
│   │   ├── idna [required: >=2.5,<4, installed: 3.7]
│   │   └── urllib3 [required: >=1.21.1,<3, installed: 1.26.19]
│   ├── safetensors [required: >=0.3.1, installed: 0.4.4]
│   ├── tokenizers [required: >=0.11.1,<0.14,!=0.11.3, installed: 0.12.1]
│   └── tqdm [required: >=4.27, installed: 4.66.5]
├── typer [required: ==0.4.1, installed: 0.4.1]
│   └── click [required: >=7.1.1,<9.0.0, installed: 8.1.7]
└── typing_extensions [required: <4.6.0, installed: 4.5.0]
pipdeptree==2.23.1
├── packaging [required: >=23.1, installed: 24.1]
└── pip [required: >=23.1.2, installed: 24.1]
pypdf==4.3.1
└── typing_extensions [required: >=4.0, installed: 4.5.0]
pytest==8.3.2
├── exceptiongroup [required: >=1.0.0rc8, installed: 1.2.2]
├── iniconfig [required: Any, installed: 2.0.0]
├── packaging [required: Any, installed: 24.1]
├── pluggy [required: >=1.5,<2, installed: 1.5.0]
└── tomli [required: >=1, installed: 2.0.1]
```
