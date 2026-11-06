from pathlib import Path
from types import SimpleNamespace

from backend.app.integrations.pdf.generator import PDFGenerator


def test_build_multiple_choice_question_marks_only_answer_key_choice():
    generator = PDFGenerator()
    elements = generator._build_question(
        {
            "type": "multiple_choice",
            "statement": "Which option is correct?",
            "score": 2,
            "config": {"alternatives": ["Wrong", "Correct", "Also wrong"]},
        },
        number=1,
        show_answer=True,
        answer_key={"correct_answer": "B"},
    )

    text = [element.getPlainText() for element in elements if hasattr(element, "getPlainText")]
    assert any("B) Correct" in item and "✓" in item for item in text)
    assert "A) Wrong" in text
    assert "C) Also wrong" in text


def test_build_question_discursive_and_multi_criteria_layouts():
    generator = PDFGenerator()
    essay = generator._build_question(
        {
            "type": "essay",
            "statement": "Explain.",
            "score": 4,
            "config": {"answer_lines": 2},
        },
        number=1,
    )
    rubric = generator._build_question(
        {
            "type": "multi_criteria",
            "statement": "Evaluate.",
            "score": 3,
            "config": {
                "criteria": [{"name": "Clarity", "points": 2}],
                "answer_lines": 1,
            },
        },
        number=2,
    )

    assert len(essay) == 4
    rubric_text = [element.getPlainText() for element in rubric if hasattr(element, "getPlainText")]
    assert any("Clarity (2 pts)" in text for text in rubric_text)
    assert len(rubric) == 5


def test_build_answer_key_question_formats_answers_rubric_and_justification():
    generator = PDFGenerator()
    elements = generator._build_answer_key_question(
        {
            "type": "essay",
            "statement": "Explain.",
            "score": 5,
        },
        number=1,
        answer_key={
            "expected_answer": "Expected",
            "keywords": ["one", "two"],
            "required_concepts": ["concept"],
            "justification": "Reason",
        },
        rubric={"criteria": [{"name": "Clarity", "description": "Clear response", "points": 2}]},
    )

    texts = [element.getPlainText() for element in elements if hasattr(element, "getPlainText")]
    assert any("Resposta esperada: Expected" in text for text in texts)
    assert any("Palavras-chave: one, two" in text for text in texts)
    assert any("Conceitos obrigatórios: concept" in text for text in texts)
    assert any("Clarity: Clear response (2 pts)" in text for text in texts)
    assert any("Justificativa: Reason" in text for text in texts)


def test_build_calculation_answer_key_includes_partial_scoring():
    elements = PDFGenerator()._build_answer_key_question(
        {"type": "calculation", "statement": "Compute.", "score": 3},
        number=1,
        answer_key={"expected_answer": "42", "partial_scoring": {"steps": 2}},
        rubric={},
    )

    texts = [element.getPlainText() for element in elements if hasattr(element, "getPlainText")]
    assert any("Resultado esperado: 42" in text for text in texts)
    assert any("Pontuação parcial:" in text for text in texts)


def test_generate_student_and_teacher_pdfs(tmp_path):
    generator = PDFGenerator()
    exam = SimpleNamespace(
        id="exam-id",
        title="Sample exam",
        total_score=2,
        duration_minutes=30,
        print_config={
            "include_student_identification": False,
            "include_qr_code": False,
            "include_page_numbers": False,
        },
    )
    version = SimpleNamespace(
        version_number=1,
        instructions="Read carefully.",
        total_score=2,
        questions_snapshot=[
            {
                "id": "q1",
                "type": "multiple_choice",
                "statement": "Choose one.",
                "score": 2,
                "subject_name": "Math",
                "config": {"alternatives": ["A", "B"]},
            }
        ],
        answer_key_snapshot={"q1": {"correct_answer": "A"}},
        rubrics_snapshot={},
    )
    copy = SimpleNamespace(copy_identifier="copy-1", qr_code_data="copy-1")

    student_path = generator.generate_student_exam(exam, version, copy, str(tmp_path))
    teacher_path = generator.generate_teacher_answer_key(exam, version, str(tmp_path))

    assert Path(student_path).read_bytes().startswith(b"%PDF")
    assert Path(teacher_path).read_bytes().startswith(b"%PDF")
