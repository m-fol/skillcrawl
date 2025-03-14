from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from database import write_to_database, is_database_connected
from skills import get_skills_for_lesson, search_courses_by_skill, search_courses_by_skill_database, extract_and_get_title, search_courses_by_skill_url
from pdf_utils import extract_text_from_pdf, split_by_semester, process_pages_by_lesson, extract_text_after_marker
from config import DB_CONFIG
from collections import Counter, defaultdict
import os
import json
from helpers import find_possible_university, load_from_cache, save_to_cache, load_university_cache, save_cache
from skillcrawl import get_university_country
from typing import List
from fuzzywuzzy import process
from fastapi import UploadFile
from esco_skill_extractor import SkillExtractor
from typing import Dict, Optional
import re
from crawler import UniversityCrawler
from collections import OrderedDict
import psycopg2
import mysql.connector
from concurrent.futures import ThreadPoolExecutor
import requests

skill_extractor = SkillExtractor()

UNI_FILE = "university_cache.json"

if os.path.exists(UNI_FILE):
    with open(UNI_FILE, "r") as f:
        university_cache = json.load(f)
else:
    university_cache = {}

app = FastAPI(title="SkillCrawl API", description="API for skill extraction and course search.")


class CrawlRequest(BaseModel):
    url: str

class SkillListRequest(BaseModel):
    skills: List[str]

class PDFProcessingRequest(BaseModel):
    pdf_name: str

class SkillSearchRequest(BaseModel):
    skill: str
    university: str = None 

class SkillSearchURLRequest(BaseModel):
    skill_url: str
    university: str = None 

class LessonRequest(BaseModel):
    university_name: str
    lesson_name: str

class TopSkillsAllRequest(BaseModel):
    top_n: Optional[int] = 20

class TopSkillsRequest(BaseModel):
    university_name: str
    top_n: Optional[int] = 20

@app.get("/health")
def health_check():
    return {"status": "running"}

@app.get("/list_pdfs")
def list_pdfs():

    university_cache = load_university_cache()
    curriculum_folder = "curriculum"
    if not os.path.exists(curriculum_folder):
        os.makedirs(curriculum_folder) 
    
    pdf_files = []
    
    for f in os.listdir(curriculum_folder):
        if f.endswith(".pdf"):
            cached_data = load_from_cache(f) or {}

            university_name = cached_data.get("university_name", "").strip()
            university_country = cached_data.get("university_country", "").strip()

            if not university_name or "unknown" in university_name.lower():
                filename = f.replace(".pdf", "")
                university_name = re.sub(r"[_\W]+", " ", filename).strip()
                print(f"Extracted university name from filename in /list_pdfs: {university_name}") 

            university_country = get_university_country(university_name) if university_name else "Unknown"

            pdf_files.append({
                "filename": f,
                "university_name": university_name,
                "university_country": university_country
            })

            university_cache[university_name] = {
                "name": university_name,
                "country": university_country,
                "pdf_file": f
            }
            save_cache()
    
    return {"pdf_files": pdf_files}

@app.post("/process_pdf")
def process_pdf(request: PDFProcessingRequest):

    university_cache = load_university_cache()
    print(f"Received request to process PDF: {request.pdf_name}")
    
    curriculum_folder = "curriculum"
    os.makedirs(curriculum_folder, exist_ok=True)

    matching_files = [f for f in os.listdir(curriculum_folder) if f.endswith(".pdf") and request.pdf_name in f]
    if not matching_files:
        raise HTTPException(404, f"No PDF matching '{request.pdf_name}' found in 'curriculum/'.")

    pdf_path = os.path.join(curriculum_folder, matching_files[0])
    pages = extract_text_from_pdf(pdf_path)

    cached_data = load_from_cache(pdf_path) or {}
    university_name = cached_data.get("university_name", "").strip()
    university_country = cached_data.get("university_country", "").strip()

    if not university_name or "unknown" in university_name.lower():
        university_name = re.sub(r"[_\W]+", " ", os.path.basename(pdf_path).replace(".pdf", "")).strip()
        print(f"✅ Extracted university name: {university_name}")
        save_cache()


    university_cache = load_university_cache()
    if university_name not in university_cache or university_country not in university_cache:
        university_country = get_university_country(university_name) if university_name else "Unknown"
        university_cache[university_name] = {"name": university_name, "country": university_country}



    marker = ['Course Outlines', 'Course Content']
    text_after_marker = extract_text_after_marker(pages, marker)
    semesters = split_by_semester(text_after_marker)
    all_data = {}

    if semesters:
        for i, semester_text in enumerate(semesters, 1):
            lessons = process_pages_by_lesson([page for page in pages if page in semester_text])
            all_data[f"Semester {i} ({len(lessons)} lessons)"] = {
                lesson: {"description": desc, "skills": list({s for skill_set in skill_extractor.get_skills([desc]) for s in skill_set})}
                for lesson, desc in lessons.items()
            }
    else:
        lessons = process_pages_by_lesson(pages)
        all_data["Lessons Only"] = {
            lesson: {"description": desc, "skills": list({s for skill_set in skill_extractor.get_skills([desc]) for s in skill_set})}
            for lesson, desc in lessons.items()
        }

    university_country = get_university_country(university_name) if university_name else "Unknown"

    all_data.update({"university_name": university_name, "university_country": university_country})
    save_cache()
    save_to_cache(university_name, all_data)

    return {"message": "PDF processed successfully.", "data": all_data}


CACHE_DIR = "cache"  

def load_all_cached_data():
    """
    Searches through the cache folder and loads data for all universities.
    Returns a dictionary where keys are university names, and values are their cached lessons.
    """
    all_data = {}

    if not os.path.exists(CACHE_DIR):
        print("⚠️ Cache directory does not exist.")
        return {}

    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"): 
            university_name = filename.replace(".json", "")
            try:
                with open(os.path.join(CACHE_DIR, filename), "r", encoding="utf-8") as file:
                    all_data[university_name] = json.load(file)
            except json.JSONDecodeError:
                print(f"❌ Failed to load cache for {university_name}. Skipping...")
    
    return all_data 

@app.post("/filter_skillnames")
def get_skills(request: LessonRequest):
    """
    API endpoint to get skill names based on university and lesson name.
    - First checks cache.
    - If not in cache, searches the database.
    - If missing in database, writes from cache to the database.
    """


    if request.university_name:
        all_data = load_from_cache(request.university_name)
    else:
        all_data = load_all_cached_data() 


    skills = get_skills_for_lesson(request.university_name, all_data, request.lesson_name, skillname=True, db_config=DB_CONFIG)

    return {"Data": skills or []} 



@app.post("/calculate_skillnames")
def calculate_skillnames(university_name: str, lesson_name: Optional[str] = None):
    all_cached_data = load_all_cached_data()
    university_names = [name.replace("_cache", "").strip() for name in all_cached_data.keys()]

    if not university_names:
        raise HTTPException(status_code=404, detail="No universities found in cache.")

    best_match, score = process.extractOne(university_name, university_names)

    if score < 70:
        raise HTTPException(status_code=404, detail=f"No close match found for university '{university_name}'.")

    print(f"[INFO] Matched university '{university_name}' -> '{best_match}' with score {score}")

    university_key = next((key for key in all_cached_data.keys() if best_match in key), best_match)
    cached_data = all_cached_data[university_key]
    extracted_skills = {}

    university_name = university_key.replace("_cache", "").strip()

    # Skillab Tracker API endpoint
    skillab_tracker_url = "https://skillab-tracker.csd.auth.gr/api/track_skills"


    def process_lesson(semester, lesson, lesson_data):
        """ Extracts skills for a lesson using Skillab Tracker API """
        try:
            print(f"[INFO] Processing skills for: {lesson} in {semester}")

            lesson_cache = cached_data.get(semester, {}).get(lesson, {})
            cached_skill_names = lesson_cache.get("skill_names", [])
            cached_skills = lesson_cache.get("skills", [])

            lesson_description = lesson_data.get("description", "")
            if isinstance(lesson_description, dict):
                lesson_description = lesson_description.get("text", "")
            if not isinstance(lesson_description, str) or not lesson_description.strip():
                print(f"[WARNING] No valid description for {lesson}. Skipping skill extraction.")
                return lesson, cached_skill_names

            # 🔵 Extract skills using skill extractor
            skills_list = skill_extractor.get_skills([lesson_description])
            skill_urls = set()

            for skill_set in skills_list:
                for skill_url in skill_set:
                    skill_urls.add(skill_url)

            if not skill_urls:
                print(f"[WARNING] No skills found for {lesson}. Skipping API call.")
                return lesson, cached_skill_names

            # 🔵 Convert skill URLs into URL-encoded format for API call
            skill_params = "&".join([f"ids={requests.utils.quote(skill_url)}" for skill_url in skill_urls])

            # 🔵 Make the POST request in the required format
            skillab_tracker_url = "https://skillab-tracker.csd.auth.gr/api/skills?page=1"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = requests.post(skillab_tracker_url, headers=headers, data=skill_params, verify=False)

            if response.status_code != 200:
                print(f"[ERROR] Skillab API failed for {lesson}. Response: {response.status_code} - {response.text}")
                return lesson, cached_skill_names

            # 🔵 Extract skill names from API response
            skill_data = response.json()
            new_skills = OrderedDict()

            for skill in skill_data.get("items", []):
                skill_url = skill.get("id")
                skill_name = skill.get("label") or (skill.get("alternative_labels")[0] if skill.get("alternative_labels") else "Unknown Skill")

                new_skills[skill_url] = skill_name

            sorted_skills = OrderedDict(sorted(new_skills.items(), key=lambda x: x[1]))

            for skill_url, skill_name in sorted_skills.items():
                if skill_name not in cached_skill_names:
                    cached_skill_names.append(skill_name)
                if skill_url not in cached_skills:
                    cached_skills.append(skill_url)

            cached_data[semester][lesson]["skill_connect"] = sorted_skills
            cached_data[semester][lesson]["skills"] = cached_skills
            cached_data[semester][lesson]["skill_names"] = cached_skill_names

            print(f"[INFO] Successfully extracted {len(sorted_skills)} skills for {lesson}")
            return lesson, cached_skill_names

        except Exception as e:
            print(f"[ERROR] Failed to process lesson '{lesson}' in '{semester}': {e}")
            return lesson, []


    lesson_tasks = []

    with ThreadPoolExecutor() as executor:
        for semester, lessons in cached_data.items():
            if semester in ["university_name", "university_country"]:
                continue

            if lesson_name:
                best_lesson_match, lesson_score = process.extractOne(lesson_name, list(lessons.keys()))

                if lesson_score < 80:
                    raise HTTPException(status_code=404, detail=f"No close match found for lesson '{lesson_name}'.")

                print(f"[INFO] Matched lesson '{lesson_name}' -> '{best_lesson_match}' with score {lesson_score}")

                selected_lessons = {best_lesson_match: lessons[best_lesson_match]}
            else:
                selected_lessons = lessons  # Preserve all lessons if no specific one is given

            for lesson, lesson_data in selected_lessons.items():
                lesson_tasks.append(executor.submit(process_lesson, semester, lesson, lesson_data))

    for future in lesson_tasks:
        lesson, skills = future.result()
        extracted_skills[lesson] = skills

    save_to_cache(university_name, cached_data)

    return {"university_name": university_name, "skills": extracted_skills}



@app.post("/search_skill")
def search_skill(request: SkillSearchRequest):
    """
    You can search if a skill exists in the database.
    In return:
    - University name(s) the skill is in
    - Lesson(s) the skill is in
    - And frequency of appearance
    """
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")
    
    results = search_courses_by_skill_database(request.skill, DB_CONFIG, request.university)
    return {"results": results}


@app.post("/search_skill_by_URL")
def search_skill_url(request: SkillSearchURLRequest):
    """
    You can search if a skill exists in the database.
    In return:
    - University name(s) the skill is in
    - Lesson(s) the skill is in
    - And frequency of appearance
    """
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")
    
    results = search_courses_by_skill_url(request.skill_url, DB_CONFIG, request.university)
    return {"results": results}


@app.post("/get_universities_by_skills")
def get_universities_by_skills(request: SkillListRequest):
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")
    
    query = """
        SELECT u.university_name, l.lesson_name, s.skill_name 
        FROM Skills s
        JOIN Lessons l ON s.lesson_id = l.lesson_id
        JOIN University u ON l.university_id = u.university_id
        WHERE s.skill_name IN (%s)
    """
    
    skill_placeholders = ', '.join(['%s'] * len(request.skills))
    formatted_query = query.replace("%s", skill_placeholders)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(formatted_query, tuple(request.skills))
        results = cursor.fetchall()
    
        university_skill_counts = {}
        university_courses = {}
        
        for row in results:
            uni = row["university_name"]
            lesson = row["lesson_name"]
            skill = row["skill_name"]
            
            if uni not in university_skill_counts:
                university_skill_counts[uni] = set()
            university_skill_counts[uni].add(skill)
            
            if uni not in university_courses:
                university_courses[uni] = {}
            if lesson not in university_courses[uni]:
                university_courses[uni][lesson] = []
            university_courses[uni][lesson].append(skill)
        
        # Filter universities that have all required skills
        filtered_universities = {
            uni: courses for uni, courses in university_courses.items()
            if len(university_skill_counts[uni]) == len(request.skills)
        }
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return filtered_universities

@app.post("/get_top_skills")
def get_top_skills(request: TopSkillsRequest):
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")
    
    query = """
        SELECT s.skill_name 
        FROM Skills s
        JOIN Lessons l ON s.lesson_id = l.lesson_id
        JOIN University u ON l.university_id = u.university_id
        WHERE u.university_name = %s
    """
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (request.university_name,))
        results = cursor.fetchall()
        
        skill_counter = Counter(row["skill_name"] for row in results)
        top_skills = [{"skill": skill, "frequency": count} for skill, count in skill_counter.most_common(request.top_n)]
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return {"university_name": request.university_name, "top_skills": top_skills}


@app.post("/get_top_skills_all")
def get_top_skills_all(request: TopSkillsAllRequest):
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")
    
    query = """
        SELECT s.skill_name, u.university_name
        FROM Skills s
        JOIN Lessons l ON s.lesson_id = l.lesson_id
        JOIN University u ON l.university_id = u.university_id
    """
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        
        skill_counter = Counter(row["skill_name"] for row in results)
        university_skill_map = defaultdict(set)
        
        for row in results:
            university_skill_map[row["skill_name"].lower()].add(row["university_name"])
        
        top_skills = [{"skill": skill, "frequency": count, "universities": list(university_skill_map[skill.lower()])} 
                      for skill, count in skill_counter.most_common(request.top_n)]
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return {"top_skills": top_skills}


@app.get("/search_json_in_cache")
def search_json_in_cache(university_name: str):
    """
    Searches for a cached JSON file based on a fuzzy match of the university name.
    """
    cache_folder = "cache"
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder) 
    
    json_files = [f for f in os.listdir(cache_folder) if f.endswith(".json")]
    
    if not json_files:
        raise HTTPException(status_code=404, detail="No cached files found.")

    best_match, score = process.extractOne(university_name, json_files)

    if score < 60: 
        raise HTTPException(status_code=404, detail=f"No close match found for university: {university_name}")

    file_path = os.path.join(cache_folder, best_match)
    with open(file_path, "r", encoding="utf-8") as file:
        cached_data = json.load(file)

    return {
        "message": "Cached file found.",
        "matched_file": best_match,
        "match_score": score,
        "data": cached_data
    }


@app.post("/save_to_db")
def save_to_db(university_name: str):
    """
    Searches for a cached JSON file using fuzzy matching and saves its data to the database.
    """

    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")

    cache_folder = "cache"
    
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    
    json_files = [f for f in os.listdir(cache_folder) if f.endswith(".json")]
    
    if not json_files:
        raise HTTPException(status_code=404, detail="No cached files found.")

    print(f"Available cached files: {json_files}")

    best_match, score = process.extractOne(university_name, json_files)

    print(f"Fuzzy match result: {best_match} (score: {score})") 

    if score < 60: 
        raise HTTPException(status_code=404, detail=f"No close match found for university: {university_name}")

    file_path = os.path.join(cache_folder, best_match)
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"Corrupted or invalid JSON file: {best_match}")

    university_name = data.get("university_name", "").strip()
    university_country = data.get("university_country", "").strip()
    number_of_semesters = len(data) - 2 

    if not university_name or not university_country:
        raise HTTPException(status_code=400, detail="Missing university name or country in the cached data.")
    
    write_to_database(data, DB_CONFIG, university_name, university_country, number_of_semesters)

    return {
        "message": "Data saved to database successfully.",
        "matched_file": best_match,
        "match_score": score
    }

CACHE_FOLDER = "cache"

@app.get("/all_university_data")
def get_all_data(university_name: str):
    """
    Fetch all university-related data, including lessons and skills, from the MySQL database.
    If the database is offline, raise an error immediately.
    """
    if not is_database_connected(DB_CONFIG):  # Check connection before proceeding
        raise HTTPException(status_code=500, detail="Database connection failed.")

    query = """
    SELECT 
        u.university_name,
        u.country,
        u.number_of_semesters,
        l.lesson_name,
        l.semester,
        l.description,
        s.skill_name,
        s.skill_url
    FROM University u
    LEFT JOIN Lessons l ON u.university_id = l.university_id
    LEFT JOIN Skills s ON l.lesson_id = s.lesson_id
    WHERE u.university_name LIKE %s
    """

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)  

    try:
        cursor.execute(query, (f"%{university_name}%",))
        results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail=f"No data found for university: {university_name}")

        university_data = {
            "university_name": results[0]["university_name"],
            "country": results[0]["country"],
            "number_of_semesters": results[0]["number_of_semesters"],
            "semesters": {}
        }

        for row in results:
            semester = row["semester"]
            lesson_name = row["lesson_name"]
            description = row["description"]
            skill_name = row["skill_name"]
            skill_url = row["skill_url"]

            if semester:
                if semester not in university_data["semesters"]:
                    university_data["semesters"][semester] = {}

                if lesson_name:
                    if lesson_name not in university_data["semesters"][semester]:
                        university_data["semesters"][semester][lesson_name] = {
                            "description": description,
                            "skills": []
                        }

                    if skill_name:
                        university_data["semesters"][semester][lesson_name]["skills"].append(
                            {"name": skill_name, "url": skill_url}
                        )

        return university_data

    finally:
        cursor.close()
        conn.close()



@app.post("/save_all_to_db")
def save_all_to_db():
    """
    Dynamically finds JSON files in the cache folder and saves their contents to the database.
    Process is sped up with Cache files.
    """
    if not is_database_connected(DB_CONFIG):
        raise HTTPException(status_code=500, detail="Database connection failed.")

    json_files = [f for f in os.listdir(CACHE_FOLDER) if f.endswith(".json") and f != "pdf_cache.json"]

    if not json_files:
        raise HTTPException(status_code=404, detail="No valid university data found in cache.")

    for json_file in json_files:
        json_path = os.path.join(CACHE_FOLDER, json_file)

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            university_name = data.get("university_name", "").replace("_cache", "").strip()
            university_country = data.get("university_country", "")
            number_of_semesters = len([key for key in data.keys() if key not in ["university_name", "university_country"]])

            if not university_name or not university_country:
                print(f"[WARNING] Skipping {json_file}: Missing university name or country.")
                continue  

            write_to_database(data, DB_CONFIG, university_name, university_country, number_of_semesters)
            print(f"[INFO] Saved {university_name} to database.")

        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse {json_file}. Skipping.")
            continue

    return {"message": "All valid university data saved to the database successfully."}

@app.post("/crawl", summary="Start a web crawl")
def crawl_university(request: CrawlRequest):
    """
    [Warning] A very primitive version of the crawler, for accessing university sites and extracting lesson data automatically.
    - Requires a URL, preferrably on the curriculum page 
    """
    url = request.url
    
    crawler = UniversityCrawler(url)
    course_info = crawler.crawl()
    
    return {"university": crawler.university_name, "courses": course_info.semesters}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
