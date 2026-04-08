"""Evaluation routes for the API."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse

from backend.app.schemas import EvaluationRequest, EvaluationResponse, RubricConfig
from backend.app.services import EvaluatorService
from backend.core.services.evaluation_store import save_evaluation_batch, get_all_evaluations
from utils.llm_service import LLMService

router = APIRouter(prefix="/api", tags=["evaluation"])

@router.get("/download/{filename}")
def download_csv(filename: str):
    """Download exported CSV file."""
    # Ensure filename is safe (basic check)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(400, "Invalid filename")
    
    file_path = Path("outputs") / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
        
    return FileResponse(file_path, media_type="text/csv", filename=filename)


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(
    assignment_type: str = Form(
        ...,
        description="Type of assignment: code, content, or mixed",
    ),
    problem_statement: Optional[str] = Form(
        None,
        description="Problem statement for code assignments",
    ),
    ideal_reference: Optional[str] = Form(
        None,
        description="Reference content for content assignments",
    ),
    rubric_content: Optional[str] = Form(
        None,
        description="Custom rubric as plain text or JSON string (optional)",
    ),
    topic: Optional[str] = Form(
        None,
        description="Topic tag for student progress tracking",
    ),
    test_cases: Optional[str] = Form(
        None,
        description="JSON string of test cases: '[{\"stdin\": \"5\\n3\", \"expected_output\": \"8\"}]'",
    ),
    files: List[UploadFile] = File(
        ...,
        description="Student submission files",
    ),
) -> EvaluationResponse:
    """
    Evaluate student submissions.

    Accepts multipart form data with:
    - **assignment_type**: Type of assignment (code, content, or mixed)
    - **problem_statement**: Problem description for code assignments
    - **ideal_reference**: Reference content for content assignments
    - **rubric_content**: Custom rubric as text or JSON (optional, uses default if not provided)
    - **topic**: Topic tag for student progress tracking (e.g., 'sorting', 'graphs')
    - **test_cases**: JSON string of test cases: '[{"stdin": "5\\n3", "expected_output": "8"}]'
    - **files**: Student submission files (.py, .cpp, .cc, .cxx, .h, .hpp, .txt, .pdf)

    Returns evaluation results with scores, feedback, and CSV export paths.

    Example usage:
    ```python
    files = [
        ("files", open("submission1.py", "rb")),
        ("files", open("submission2.py", "rb")),
    ]
    data = {
        "assignment_type": "code",
        "problem_statement": "Write a factorial function",
    }
    response = requests.post("http://localhost:8000/api/evaluate", files=files, data=data)
    ```
    """
    # Validate file types
    ALLOWED_EXTENSIONS = {".py", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".txt", ".pdf"}
    for file in files:
        ext = "." + file.filename.lower().split(".")[-1] if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Allowed: .py, .cpp, .cc, .cxx, .h, .hpp, .txt, .pdf"
            )

    # Content inspection is deferred to evaluation agents to avoid duplication.

    # Create temporary directory for submissions
    temp_dir = tempfile.mkdtemp(prefix="submissions_")

    try:
        # Save uploaded files to temp directory
        for file in files:
            file_path = Path(temp_dir) / file.filename
            with open(file_path, "wb") as f:
                f.write(file.file.read())

        # Parse custom rubric if provided
        rubric = None
        rubric_warning = None
        if rubric_content:
            try:
                # Try strict JSON parsing first
                rubric_dict = json.loads(rubric_content)
                rubric = RubricConfig(**rubric_dict)
            except (json.JSONDecodeError, ValueError):
                # If not JSON or invalid JSON structure, treat as plain text and use LLM
                print("Rubric JSON parse failed, attempting LLM parsing of text rubric...")
                try:
                    llm_service = LLMService()
                    parsed_dict = llm_service.parse_rubric_text(rubric_content)
                    if parsed_dict:
                        rubric = RubricConfig(**parsed_dict)
                    else:
                        rubric_warning = "Failed to parse text rubric via LLM (returned None). Using default rubric."
                except Exception as e:
                    rubric_warning = f"Error during LLM rubric parsing: {e}. Using default rubric."
                    print(rubric_warning)

        # Parse test cases if provided as a standalone field
        if test_cases:
            try:
                from backend.app.schemas import TestCase
                tc_list = json.loads(test_cases)
                if not isinstance(tc_list, list):
                    tc_list = [tc_list]
                # Use from_flexible to handle both {stdin,expected_output} and {input,output}
                parsed_test_cases = [TestCase.from_flexible(tc) for tc in tc_list]
                # Filter out empty test cases
                parsed_test_cases = [tc for tc in parsed_test_cases if tc.stdin or tc.expected_output]
                
                if parsed_test_cases:
                    # If no rubric provided, use an empty one to hold test cases
                    if not rubric:
                        rubric = RubricConfig()
                    
                    # Attach parsed test cases to rubric
                    rubric.test_cases = parsed_test_cases
                    print(f"✓ Parsed {len(parsed_test_cases)} test cases")
                else:
                    rubric_warning = "Test cases parsed but none had valid stdin/expected_output."
            except (json.JSONDecodeError, ValueError) as e:
                rubric_warning = f"Failed to parse 'test_cases' JSON: {e}"
                print(rubric_warning)

        # Create evaluation request
        request = EvaluationRequest(
            assignment_type=assignment_type,
            submission_folder=temp_dir,
            problem_statement=problem_statement,
            ideal_reference=ideal_reference,
            rubric=rubric,
            topic_tag=topic,
        )

        # Evaluate via service layer
        service = EvaluatorService()
        response = service.evaluate(request)

        # Convert local file paths to download URLs
        # Assuming frontend is on same host/port for relative links, or construct full URL
        # For simplicity, we'll return full URLs assuming localhost:8000 for now, 
        # but in prod this should be dynamic.
        base_url = "http://localhost:8000/api/download"
        
        if response.csv_output_path:
            filename = Path(response.csv_output_path).name
            response.csv_output_path = f"{base_url}/{filename}"
            
        if response.csv_detailed_output_path:
            filename = Path(response.csv_detailed_output_path).name
            response.csv_detailed_output_path = f"{base_url}/{filename}"

        if rubric_warning:
            response.message += f" | Warning: {rubric_warning}"

        # Persist results to database
        if response.status == "success" and response.results:
            try:
                result_dicts = [r.model_dump() for r in response.results]
                save_evaluation_batch(
                    results=result_dicts,
                    summary=response.summary,
                    csv_output_path=response.csv_output_path,
                    csv_detailed_output_path=response.csv_detailed_output_path,
                )
            except Exception as persist_err:
                print(f"Evaluation persistence failed (non-fatal): {persist_err}")

        return response

    except Exception as e:
        return EvaluationResponse(
            status="error",
            message="Evaluation failed",
            error_message=str(e),
        )

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.get("/evaluations/history")
def evaluation_history():
    """Retrieve all past evaluation results from the database."""
    data = get_all_evaluations(limit=200)
    return {"status": "success", **data}


@router.delete("/evaluations/cleanup")
def cleanup_evaluations(below_score: float = 10.0):
    """
    Remove evaluation results with scores below a threshold.
    
    Useful for cleaning up broken evaluation results (e.g., old 2.2 scores).
    
    Query params:
    - below_score: Remove results with percentage below this value (default: 10.0)
    """
    from backend.core.services.database import get_db
    
    db = get_db()
    if not db.available:
        raise HTTPException(503, "Database unavailable")
    
    try:
        # Count affected rows first
        count_row = db.execute_one(
            "SELECT COUNT(*) as cnt FROM evaluation_results WHERE percentage < %s",
            [below_score],
        )
        count = count_row["cnt"] if count_row else 0
        
        # Delete the results
        db.execute(
            "DELETE FROM evaluation_results WHERE percentage < %s",
            [below_score],
        )
        
        # Clean up orphaned batches
        db.execute(
            """
            DELETE FROM evaluation_batches
            WHERE batch_id NOT IN (
                SELECT DISTINCT batch_id FROM evaluation_results WHERE batch_id IS NOT NULL
            )
            """
        )
        
        return {
            "status": "success",
            "message": f"Removed {count} evaluation results with score below {below_score}",
            "removed_count": count,
        }
    except Exception as e:
        raise HTTPException(500, f"Cleanup failed: {e}")

