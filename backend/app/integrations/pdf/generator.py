"""Gerador de PDF para provas e gabaritos."""

from datetime import datetime
from io import BytesIO
from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor, grey
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.app.models.exam import Exam, ExamCopy, ExamVersion


class PDFGenerator:
    """Gerador de PDFs para provas e gabaritos."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos customizados."""
        self.styles.add(ParagraphStyle(
            name='ExamTitle',
            parent=self.styles['Title'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=HexColor('#1a1a2e'),
        ))
        self.styles.add(ParagraphStyle(
            name='ExamSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=4,
            textColor=HexColor('#4a4a6a'),
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            leading=16,
            spaceBefore=12,
            spaceAfter=6,
            textColor=HexColor('#1a1a2e'),
            borderWidth=0,
            borderPadding=0,
        ))
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            name='AnswerOption',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=20,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name='AnswerLine',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name='FooterText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=grey,
        ))
        self.styles.add(ParagraphStyle(
            name='RubricCriteria',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            leftIndent=15,
            spaceAfter=3,
            textColor=HexColor('#333333'),
        ))

    def generate_student_exam(
        self,
        exam: Exam,
        version: ExamVersion,
        copy: ExamCopy,
        output_dir: str = "./storage/exams/pdfs",
    ) -> str:
        """Gera PDF da prova do aluno."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print_config = exam.print_config or {}
        pagesize = LETTER if print_config.get("page_size") == "LETTER" else A4

        filename = f"prova_{copy.copy_identifier}.pdf"
        filepath = Path(output_dir) / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=pagesize,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        story = []

        # Cabeçalho
        story.extend(self._build_header(
            exam,
            version,
            copy,
            include_student_identification=print_config.get(
                "include_student_identification", True
            ),
        ))
        story.append(Spacer(1, 12))

        # Instruções
        if version.instructions:
            story.append(Paragraph("Instruções", self.styles['SectionHeader']))
            story.append(Paragraph(version.instructions, self.styles['QuestionText']))
            story.append(Spacer(1, 12))

        # Questões
        for i, q_data in enumerate(version.questions_snapshot):
            story.extend(self._build_question(q_data, i + 1, show_answer=False))
            story.append(Spacer(1, 8))

        if print_config.get("include_qr_code", True):
            story.append(Spacer(1, 20))
            story.extend(self._build_footer_qr(copy))

        def page_callback(canvas, page_doc):
            if print_config.get("include_page_numbers", True):
                self._add_page_number(canvas, page_doc, pagesize)

        doc.build(story, onFirstPage=page_callback, onLaterPages=page_callback)
        return str(filepath)

    def generate_teacher_answer_key(
        self,
        exam: Exam,
        version: ExamVersion,
        output_dir: str = "./storage/exams/pdfs",
    ) -> str:
        """Gera PDF do gabarito do professor."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print_config = exam.print_config or {}
        pagesize = LETTER if print_config.get("page_size") == "LETTER" else A4

        filename = f"gabarito_{exam.id}_v{version.version_number}.pdf"
        filepath = Path(output_dir) / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=pagesize,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        story = []

        # Cabeçalho do gabarito
        story.append(Paragraph("GABARITO OFICIAL", self.styles['ExamTitle']))
        story.append(Paragraph(f"{exam.title} - Versão {version.version_number}", self.styles['ExamSubtitle']))
        story.append(Spacer(1, 8))

        # Info
        info_data = [
            ["Disciplina:", version.questions_snapshot[0].get('subject_name', 'N/A') if version.questions_snapshot else 'N/A'],
            ["Data:", datetime.now().strftime("%d/%m/%Y")],
            ["Pontuação Total:", str(version.total_score)],
        ]
        info_table = Table(info_data, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(info_table)
        story.append(HRFlowable(width="100%", thickness=1, color=grey, spaceAfter=12))

        # Gabarito por questão
        for i, q_data in enumerate(version.questions_snapshot):
            q_id = q_data['id']
            answer_key = version.answer_key_snapshot.get(q_id, {})
            rubric = version.rubrics_snapshot.get(q_id, {})

            story.extend(self._build_answer_key_question(q_data, i + 1, answer_key, rubric))
            story.append(Spacer(1, 10))

        def page_callback(canvas, page_doc):
            if print_config.get("include_page_numbers", True):
                self._add_page_number(canvas, page_doc, pagesize)

        doc.build(story, onFirstPage=page_callback, onLaterPages=page_callback)
        return str(filepath)

    def _build_header(
        self,
        exam: Exam,
        version: ExamVersion,
        copy: ExamCopy,
        include_student_identification: bool = True,
    ) -> list:
        """Constrói cabeçalho da prova."""
        elements = []

        # Linha superior com logo placeholder
        header_data = [
            ["INSTITUIÇÃO DE ENSINO", "", f"CÓPIA: {copy.copy_identifier}"],
            ["", "", f"QR: {copy.copy_identifier}"],
        ]
        header_table = Table(header_data, colWidths=[6*cm, 7*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#333333')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1a1a2e'), spaceAfter=8))

        # Título da prova
        elements.append(Paragraph(exam.title, self.styles['ExamTitle']))

        # Info da prova
        info_data = [
            ["Curso:", "Curso", "Disciplina:", "Disciplina"],
            ["Professor:", "Professor", "Turma:", "Turma"],
            ["Data:", "Data", "Duração:", f"{exam.duration_minutes} min"],
            ["Valor Total:", str(exam.total_score), "Versão:", str(version.version_number)],
        ]
        info_table = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, grey),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f8fc')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 8))

        if include_student_identification:
            id_data = [
                ["Nome do Aluno:", "_" * 50, "RA/RM:", "_" * 20],
                ["Assinatura:", "_" * 50, "Data:", "_" * 20],
            ]
            id_table = Table(id_data, colWidths=[3*cm, 7*cm, 2.5*cm, 4*cm])
            id_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(id_table)
            elements.append(Spacer(1, 12))

        return elements

    def _build_question(
        self,
        q_data: dict,
        number: int,
        show_answer: bool = False,
        answer_key: dict | None = None,
    ) -> list:
        """Constrói uma questão."""
        elements = []
        answer_key = answer_key or {}

        q_type = q_data.get('type', 'multiple_choice')
        statement = q_data.get('statement', '')
        score = q_data.get('score', 0)
        config = q_data.get('config', {})

        # Cabeçalho da questão
        header = f"Questão {number} ({q_type.replace('_', ' ').title()}) - {score} pontos"
        elements.append(Paragraph(header, self.styles['SectionHeader']))

        # Enunciado
        elements.append(Paragraph(statement, self.styles['QuestionText']))

        if q_type == 'multiple_choice':
            alternatives = config.get('alternatives', [])
            for j, alt in enumerate(alternatives):
                letter = chr(65 + j)  # A, B, C, D...
                if show_answer and answer_key.get('correct_answer') == letter:
                    text = f"<b>{letter}) {alt} ✓</b>"
                else:
                    text = f"{letter}) {alt}"
                elements.append(Paragraph(text, self.styles['AnswerOption']))

            # Linhas para resposta
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Resposta: ________", self.styles['AnswerLine']))

        elif q_type in ['essay', 'short_answer', 'calculation']:
            # Espaço para resposta discursiva
            lines = config.get('answer_lines', 10)
            for _ in range(lines):
                elements.append(Paragraph("_" * 90, self.styles['AnswerLine']))

        elif q_type == 'multi_criteria':
            criteria = config.get('criteria', [])
            for crit in criteria:
                elements.append(Paragraph(f"• {crit.get('name', 'Critério')} ({crit.get('points', 0)} pts)", self.styles['RubricCriteria']))
            elements.append(Spacer(1, 6))
            for _ in range(config.get('answer_lines', 8)):
                elements.append(Paragraph("_" * 90, self.styles['AnswerLine']))

        return elements

    def _build_answer_key_question(self, q_data: dict, number: int, answer_key: dict, rubric: dict) -> list:
        """Constrói questão do gabarito."""
        elements = []

        q_type = q_data.get('type', 'multiple_choice')
        statement = q_data.get('statement', '')
        score = q_data.get('score', 0)

        header = f"Questão {number} ({q_type.replace('_', ' ').title()}) - {score} pts"
        elements.append(Paragraph(header, self.styles['SectionHeader']))
        elements.append(Paragraph(statement, self.styles['QuestionText']))

        if q_type == 'multiple_choice':
            correct = answer_key.get('correct_answer', '')
            elements.append(Paragraph(f"<b>Resposta correta: {correct}</b>", self.styles['AnswerOption']))
            accepted = answer_key.get('accepted_alternatives', [])
            if accepted:
                elements.append(Paragraph(f"Alternativas aceitas: {', '.join(accepted)}", self.styles['AnswerOption']))

        elif q_type in ['essay', 'short_answer']:
            expected = answer_key.get('expected_answer', '')
            if expected:
                elements.append(Paragraph(f"<b>Resposta esperada:</b> {expected}", self.styles['AnswerOption']))
            keywords = answer_key.get('keywords', [])
            if keywords:
                elements.append(Paragraph(f"Palavras-chave: {', '.join(keywords)}", self.styles['AnswerOption']))
            concepts = answer_key.get('required_concepts', [])
            if concepts:
                elements.append(Paragraph(f"Conceitos obrigatórios: {', '.join(concepts)}", self.styles['AnswerOption']))

        elif q_type == 'calculation':
            expected = answer_key.get('expected_answer', '')
            if expected:
                elements.append(Paragraph(f"<b>Resultado esperado:</b> {expected}", self.styles['AnswerOption']))
            partial = answer_key.get('partial_scoring', {})
            if partial:
                elements.append(Paragraph(f"Pontuação parcial: {partial}", self.styles['AnswerOption']))

        # Rubrica
        if rubric:
            criteria = rubric.get('criteria', [])
            if criteria:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph("<b>Rubrica:</b>", self.styles['AnswerOption']))
                for crit in criteria:
                    elements.append(Paragraph(f"• {crit.get('name', 'Critério')}: {crit.get('description', '')} ({crit.get('points', 0)} pts)", self.styles['RubricCriteria']))

        justification = answer_key.get('justification', '')
        if justification:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(f"<b>Justificativa:</b> {justification}", self.styles['AnswerOption']))

        return elements

    def _build_footer_qr(self, copy: ExamCopy) -> list:
        """Constrói rodapé com QR Code."""
        elements = []
        elements.append(HRFlowable(width="100%", thickness=0.5, color=grey, spaceAfter=8))

        # Gera QR Code
        qr = qrcode.make(copy.qr_code_data)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_img = Image(qr_buffer, width=3*cm, height=3*cm)

        footer_data = [
            [Paragraph(f"Código: {copy.copy_identifier}", self.styles['FooterText']), qr_img, Paragraph("EduGrade", self.styles['FooterText'])],
        ]
        footer_table = Table(footer_data, colWidths=[6*cm, 3*cm, 6*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(footer_table)

        return elements

    def _add_page_number(self, canvas, doc, pagesize=A4):
        """Adiciona número da página."""
        canvas.saveState()
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(grey)
        canvas.drawCentredString(pagesize[0]/2, 15*mm, text)
        canvas.restoreState()
