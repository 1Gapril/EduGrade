"""
Script de geração da Apresentação Executiva em PowerPoint (PPTX) do Projeto EduGrade.
Trabalho Prático A3 - Gestão e Qualidade de Software (GQS).
"""
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- PALETA DE CORES PROFISSIONAL ---
C_DARK_BG = RGBColor(15, 23, 42)        # Slate 900
C_DARK_CARD = RGBColor(30, 41, 59)      # Slate 800
C_DARK_BORDER = RGBColor(51, 65, 85)    # Slate 700

C_LIGHT_BG = RGBColor(248, 250, 252)    # Slate 50
C_LIGHT_CARD = RGBColor(255, 255, 255)  # Branco
C_LIGHT_BORDER = RGBColor(226, 232, 240)# Slate 200

C_PRIMARY = RGBColor(37, 99, 235)       # Azul Royal (Blue 600)
C_PRIMARY_DARK = RGBColor(29, 78, 216)  # Blue 700
C_ACCENT_CYAN = RGBColor(14, 165, 233)  # Sky 500
C_ACCENT_TEAL = RGBColor(20, 184, 166)  # Teal 500
C_SUCCESS = RGBColor(16, 185, 129)      # Emerald 500
C_WARNING = RGBColor(245, 158, 11)      # Amber 500
C_DANGER = RGBColor(239, 68, 68)        # Red 500

C_TEXT_DARK = RGBColor(15, 23, 42)      # Slate 900
C_TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
C_TEXT_LIGHT = RGBColor(248, 250, 252)  # Slate 50
C_TEXT_LIGHT_MUTED = RGBColor(148, 163, 184) # Slate 400

FONT_NAME = "Calibri"

def set_slide_background(slide, prs, color):
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, title_text, category="EDUGRADE • SISTEMA ACADÊMICO COM IA", is_dark=False):
    # Category Pill / Tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(10), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.name = FONT_NAME
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = C_ACCENT_CYAN if is_dark else C_PRIMARY

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_NAME
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_LIGHT if is_dark else C_TEXT_DARK

    # Subtle separator line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = C_DARK_BORDER if is_dark else C_LIGHT_BORDER
    line.line.fill.background()

def create_card(slide, left, top, width, height, is_dark=False, accent_top_color=None):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_DARK_CARD if is_dark else C_LIGHT_CARD
    card.line.color.rgb = C_DARK_BORDER if is_dark else C_LIGHT_BORDER
    card.line.width = Pt(1.2)
    
    if accent_top_color:
        top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = accent_top_color
        top_bar.line.fill.background()
    return card

def add_bullet_points(text_frame, items, is_dark=False, font_size=13, space_after=10):
    for i, item in enumerate(items):
        if i == 0 and len(text_frame.paragraphs[0].text) == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.text = item
        p.font.name = FONT_NAME
        p.font.size = Pt(font_size)
        p.font.color.rgb = C_TEXT_LIGHT_MUTED if is_dark else C_TEXT_DARK
        p.space_after = Pt(space_after)
        p.level = 0

def add_stat_card(slide, left, top, width, height, number_text, label_text, color=C_PRIMARY, is_dark=False):
    create_card(slide, left, top, width, height, is_dark=is_dark, accent_top_color=color)
    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    
    p1 = tf.paragraphs[0]
    p1.text = number_text
    p1.font.name = FONT_NAME
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = color
    p1.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = label_text
    p2.font.name = FONT_NAME
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_LIGHT_MUTED if is_dark else C_TEXT_MUTED
    p2.alignment = PP_ALIGN.CENTER

def add_table_custom(slide, left, top, width, height, headers, rows, col_widths=None, is_dark=False):
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(num_rows, num_cols, left, top, width, height)
    tbl = table_shape.table
    
    if col_widths and len(col_widths) == num_cols:
        for idx, w in enumerate(col_widths):
            tbl.columns[idx].width = w
            
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY_DARK if is_dark else C_PRIMARY
        tf = cell.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.1)
        tf.margin_top = tf.margin_bottom = Inches(0.08)
        p = tf.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_NAME
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_LIGHT
        p.alignment = PP_ALIGN.CENTER
        
    # Rows
    for r_idx, row in enumerate(rows):
        bg = C_DARK_CARD if is_dark else (C_LIGHT_CARD if r_idx % 2 == 0 else RGBColor(241, 245, 249))
        for c_idx, cell_value in enumerate(row):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.1)
            tf.margin_top = tf.margin_bottom = Inches(0.08)
            p = tf.paragraphs[0]
            p.text = str(cell_value)
            p.font.name = FONT_NAME
            p.font.size = Pt(12)
            p.font.color.rgb = C_TEXT_LIGHT if is_dark else C_TEXT_DARK
            if c_idx == 0:
                p.font.bold = True
                
    return table_shape

def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank
    
    # -------------------------------------------------------------
    # SLIDE 1: CAPA EXECUTIVA (DARK)
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, prs, C_DARK_BG)
    
    # Top Tag
    tag_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.4))
    tf_tag = tag_box.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "TRABALHO PRÁTICO A3 • GESTÃO E QUALIDADE DE SOFTWARE (GQS)"
    p_tag.font.name = FONT_NAME
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_ACCENT_CYAN
    
    # Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.3), Inches(1.2))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = "EduGrade"
    p_t.font.name = FONT_NAME
    p_t.font.size = Pt(54)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_LIGHT
    
    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.6), Inches(11.3), Inches(0.9))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Sistema Full Stack de Gestão Acadêmica e Desempenho com Inteligência Artificial para Correção de Provas Presenciais"
    p_sub.font.name = FONT_NAME
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = C_TEXT_LIGHT_MUTED
    
    # Badges Row (ODS 4 & Professor)
    badge1 = create_card(s1, Inches(1.0), Inches(3.7), Inches(4.5), Inches(0.8), is_dark=True, accent_top_color=C_SUCCESS)
    b1_tf = s1.shapes.add_textbox(Inches(1.15), Inches(3.8), Inches(4.2), Inches(0.6)).text_frame
    p_b1_1 = b1_tf.paragraphs[0]
    p_b1_1.text = "Alinhamento Estratégico: ODS 4"
    p_b1_1.font.name = FONT_NAME
    p_b1_1.font.bold = True
    p_b1_1.font.size = Pt(13)
    p_b1_1.font.color.rgb = C_SUCCESS
    p_b1_2 = b1_tf.add_paragraph()
    p_b1_2.text = "Educação Inclusiva, Equitativa e de Qualidade"
    p_b1_2.font.size = Pt(11)
    p_b1_2.font.color.rgb = C_TEXT_LIGHT_MUTED
    
    badge2 = create_card(s1, Inches(5.8), Inches(3.7), Inches(4.5), Inches(0.8), is_dark=True, accent_top_color=C_PRIMARY)
    b2_tf = s1.shapes.add_textbox(Inches(5.95), Inches(3.8), Inches(4.2), Inches(0.6)).text_frame
    p_b2_1 = b2_tf.paragraphs[0]
    p_b2_1.text = "Orientador Acadêmico"
    p_b2_1.font.name = FONT_NAME
    p_b2_1.font.bold = True
    p_b2_1.font.size = Pt(13)
    p_b2_1.font.color.rgb = C_PRIMARY
    p_b2_2 = b2_tf.add_paragraph()
    p_b2_2.text = "Prof. Daniel Henrique Matos de Paiva"
    p_b2_2.font.size = Pt(11)
    p_b2_2.font.color.rgb = C_TEXT_LIGHT_MUTED
    
    # Team Card
    create_card(s1, Inches(1.0), Inches(4.8), Inches(11.3), Inches(1.9), is_dark=True, accent_top_color=C_ACCENT_CYAN)
    team_tb = s1.shapes.add_textbox(Inches(1.2), Inches(4.95), Inches(10.9), Inches(1.6))
    team_tf = team_tb.text_frame
    p_team_h = team_tf.paragraphs[0]
    p_team_h.text = "EQUIPE DE DESENVOLVIMENTO & ENGENHARIA DE SOFTWARE"
    p_team_h.font.name = FONT_NAME
    p_team_h.font.size = Pt(12)
    p_team_h.font.bold = True
    p_team_h.font.color.rgb = C_ACCENT_CYAN
    p_team_h.space_after = Pt(8)
    
    membros = [
        ("Gabriel Ferreira (RA 325140970)", "GitHub, Gestão de Versionamento (GitFlow), CI/CD DevOps e Apresentação"),
        ("Fernando Almeida (RA 326132695)", "Desenvolvimento Backend (FastAPI), Arquitetura Frontend e Testes Unitários"),
        ("Lucas Henrique Miranda (RA 325131396)", "Garantia da Qualidade (QA), Matriz de Testes e Documentação Técnica"),
        ("Caio Durães (RA 325132875)", "Inteligência Artificial, Visão Computacional (OCR), Modelos LLM e Integrações")
    ]
    for nome, papel in membros:
        p_m = team_tf.add_paragraph()
        p_m.text = f"• {nome}  —  {papel}"
        p_m.font.name = FONT_NAME
        p_m.font.size = Pt(11)
        p_m.font.color.rgb = C_TEXT_LIGHT
        p_m.space_after = Pt(3)
        
    # -------------------------------------------------------------
    # SLIDE 2: O PROBLEMA DA AVALIAÇÃO TRADICIONAL
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, prs, C_LIGHT_BG)
    add_header(s2, "O Desafio da Avaliação de Aprendizagem em Larga Escala", "CONTEXTO E MOTIVAÇÃO")
    
    col_w = Inches(3.64)
    gap = Inches(0.38)
    left_start = Inches(0.8)
    top_pos = Inches(1.8)
    h_card = Inches(4.0)
    
    # Card 1: Sobrecarga
    create_card(s2, left_start, top_pos, col_w, h_card, accent_top_color=C_DANGER)
    tb = s2.shapes.add_textbox(left_start + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_card - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Sobrecarga Docente"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_DANGER
    p.space_after = Pt(12)
    add_bullet_points(tf, [
        "A correção manual de provas em papel (especialmente discursivas) consome dezenas de horas repetitivas.",
        "Professor sobrecarregado com digitação manual de notas em diários e planilhas paralelas.",
        "Redução do tempo disponível para planejamento pedagógico e mentoria individualizada."
    ], space_after=8)
    
    # Card 2: Inconsistência
    create_card(s2, left_start + col_w + gap, top_pos, col_w, h_card, accent_top_color=C_WARNING)
    tb = s2.shapes.add_textbox(left_start + col_w + gap + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_card - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Risco de Inconsistência"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_WARNING
    p.space_after = Pt(12)
    add_bullet_points(tf, [
        "Fadiga humana provoca variação nos critérios de correção entre o início e o fim de um lote de provas.",
        "Erros frequentes na soma de notas parciais e cálculo incorreto de pontuações de questões.",
        "Dificuldade de manter padrão rigoroso em turmas numerosas com múltiplos avaliadores."
    ], space_after=8)
    
    # Card 3: Rastreabilidade
    create_card(s2, left_start + (col_w + gap) * 2, top_pos, col_w, h_card, accent_top_color=C_PRIMARY)
    tb = s2.shapes.add_textbox(left_start + (col_w + gap) * 2 + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_card - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Falta de Rastreabilidade"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(12)
    add_bullet_points(tf, [
        "Demora semanas até que o estudante receba feedback qualitativo sobre seus acertos e falhas.",
        "Ausência de histórico auditável quando uma nota é contestada (qual versão de gabarito foi usada?).",
        "Notas lançadas sem memória de cálculo associada à folha de resposta do aluno."
    ], space_after=8)
    
    # Bottom callout
    bot_card = create_card(s2, left_start, Inches(6.05), Inches(11.73), Inches(0.9), accent_top_color=C_ACCENT_TEAL)
    bot_tb = s2.shapes.add_textbox(left_start + Inches(0.2), Inches(6.15), Inches(11.33), Inches(0.7))
    bot_tf = bot_tb.text_frame
    bot_tf.word_wrap = True
    p_bot = bot_tf.paragraphs[0]
    p_bot.text = "Premissa Fundamental: O EduGrade NÃO elimina a prova em papel. A avaliação segue presencial e física! O sistema digitaliza e automatiza a infraestrutura de apoio ao redor (criação, impressão, leitura e correção assistida)."
    p_bot.font.name = FONT_NAME
    p_bot.font.size = Pt(12)
    p_bot.font.bold = True
    p_bot.font.color.rgb = C_PRIMARY_DARK
    
    # -------------------------------------------------------------
    # SLIDE 3: OBJETIVOS E ODS 4
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, prs, C_LIGHT_BG)
    add_header(s3, "Objetivo Geral e Alinhamento com a ODS 4 (ONU)", "PROPÓSITO & IMPACTO")
    
    # Box Objetivo Geral
    create_card(s3, Inches(0.8), Inches(1.8), Inches(11.73), Inches(1.4), accent_top_color=C_PRIMARY)
    obj_tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.33), Inches(1.1))
    obj_tf = obj_tb.text_frame
    obj_tf.word_wrap = True
    p_obj_h = obj_tf.paragraphs[0]
    p_obj_h.text = "OBJETIVO GERAL DO PROJETO"
    p_obj_h.font.name = FONT_NAME
    p_obj_h.font.size = Pt(12)
    p_obj_h.font.bold = True
    p_obj_h.font.color.rgb = C_PRIMARY
    p_obj_h.space_after = Pt(4)
    p_obj_c = obj_tf.add_paragraph()
    p_obj_c.text = "Desenvolver e documentar uma plataforma acadêmica integrada (Full Stack) que permita ao professor criar, imprimir e corrigir provas presenciais com apoio de Inteligência Artificial e OCR, garantindo aos alunos transparência e aos gestores conformidade, com qualidade de software comprovada por testes automatizados (cobertura ≥ 80%) e pipeline CI/CD."
    p_obj_c.font.name = FONT_NAME
    p_obj_c.font.size = Pt(13)
    p_obj_c.font.color.rgb = C_TEXT_DARK
    
    # 3 Pilares
    p_w = Inches(3.64)
    p_top = Inches(3.45)
    p_h = Inches(3.5)
    
    # Pilar 1
    create_card(s3, Inches(0.8), p_top, p_w, p_h, accent_top_color=C_ACCENT_CYAN)
    tb1 = s3.shapes.add_textbox(Inches(1.0), p_top + Inches(0.15), p_w - Inches(0.4), p_h - Inches(0.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "1. Eficiência Operacional"
    p1.font.name = FONT_NAME
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = C_PRIMARY_DARK
    p1.space_after = Pt(10)
    add_bullet_points(tf1, [
        "Redução de até 75% no tempo de correção física de provas.",
        "Leitura automática de respostas discursivas via OCR e interpretação semântica com LLMs.",
        "Lançamento automático de notas no diário após homologação docente com 1 clique."
    ], space_after=8)
    
    # Pilar 2
    create_card(s3, Inches(0.8 + 3.64 + 0.38), p_top, p_w, p_h, accent_top_color=C_SUCCESS)
    tb2 = s3.shapes.add_textbox(Inches(0.8 + 3.64 + 0.38 + 0.2), p_top + Inches(0.15), p_w - Inches(0.4), p_h - Inches(0.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "2. ODS 4 — Qualidade"
    p2.font.name = FONT_NAME
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = C_SUCCESS
    p2.space_after = Pt(10)
    add_bullet_points(tf2, [
        "Feedback detalhado: critérios atendidos, erros conceituais e justificativa pedagógica.",
        "Equidade na avaliação: aplicação uniforme de rubricas e gabaritos oficiais.",
        "Redução da evasão por acompanhamento preditivo de notas e frequência do estudante."
    ], space_after=8)
    
    # Pilar 3
    create_card(s3, Inches(0.8 + (3.64 + 0.38) * 2), p_top, p_w, p_h, accent_top_color=C_WARNING)
    tb3 = s3.shapes.add_textbox(Inches(0.8 + (3.64 + 0.38) * 2 + 0.2), p_top + Inches(0.15), p_w - Inches(0.4), p_h - Inches(0.3))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "3. Governança & LGPD"
    p3.font.name = FONT_NAME
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = C_WARNING
    p3.space_after = Pt(10)
    add_bullet_points(tf3, [
        "Trilhas de auditoria imutáveis para qualquer modificação ou consulta de nota.",
        "Suporte a modelos de IA 100% locais (Ollama) para proteção de dados sensíveis.",
        "Controle de acesso por contexto (turma x disciplina x período letivo)."
    ], space_after=8)
    
    # -------------------------------------------------------------
    # SLIDE 4: PÚBLICO-ALVO E MATRIZ DE PERFIS (RBAC)
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, prs, C_LIGHT_BG)
    add_header(s4, "Público-Alvo e Matriz de Controle de Acesso Baseado em Papéis", "RBAC & GOVERNANÇA")
    
    card_w = Inches(3.64)
    card_gap = Inches(0.38)
    c_top = Inches(1.8)
    c_h = Inches(4.3)
    
    # Perfil Aluno
    create_card(s4, Inches(0.8), c_top, card_w, c_h, accent_top_color=C_ACCENT_CYAN)
    tb = s4.shapes.add_textbox(Inches(1.0), c_top + Inches(0.2), card_w - Inches(0.4), c_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Portal do Aluno"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY_DARK
    p.space_after = Pt(10)
    add_bullet_points(tf, [
        "Acesso restrito exclusivamente aos seus próprios dados acadêmicos.",
        "Visualização de notas e médias (somente após homologação do professor).",
        "Acompanhamento de frequência e faltas por matéria.",
        "Grade horária semanal de aulas.",
        "Download de materiais didáticos disponibilizados.",
        "NÃO realiza prova online (prova é física)."
    ], space_after=6)
    
    # Perfil Professor
    create_card(s4, Inches(0.8 + 3.64 + 0.38), c_top, card_w, c_h, accent_top_color=C_PRIMARY)
    tb = s4.shapes.add_textbox(Inches(0.8 + 3.64 + 0.38 + 0.2), c_top + Inches(0.2), card_w - Inches(0.4), c_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Portal do Professor"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    add_bullet_points(tf, [
        "Acesso restrito às turmas sob sua atribuição letiva direta.",
        "Criação e edição de provas com gabaritos estruturados e rubricas.",
        "Exportação de PDFs e impressão individual ou em lote com QR Code.",
        "Upload de arquivos de provas digitalizadas (PDF ou fotos).",
        "Revisão obrigatória das sugestões de nota geradas por IA.",
        "Lançamento e publicação de notas oficiais no diário."
    ], space_after=6)
    
    # Perfil Administrador
    create_card(s4, Inches(0.8 + (3.64 + 0.38) * 2), c_top, card_w, c_h, accent_top_color=C_DARK_BG)
    tb = s4.shapes.add_textbox(Inches(0.8 + (3.64 + 0.38) * 2 + 0.2), c_top + Inches(0.2), card_w - Inches(0.4), c_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Administrador Geral"
    p.font.name = FONT_NAME
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BG
    p.space_after = Pt(10)
    add_bullet_points(tf, [
        "Governança estrutural: cursos, disciplinas, turmas e períodos.",
        "Gestão de usuários, senhas e chamados de acesso.",
        "Atribuição formal de docentes às respectivas turmas.",
        "Configuração da Central de IA (chaves criptografadas e modelos).",
        "Monitoramento de storage e logs de auditoria corporativa.",
        "Painel de Qualidade: execução de testes e relatório HTML."
    ], space_after=6)
    
    # Bottom Alert / Rule
    bot_card = create_card(s4, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7), accent_top_color=C_DANGER)
    bot_tb = s4.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.33), Inches(0.55))
    bot_tf = bot_tb.text_frame
    bot_tf.word_wrap = True
    p_b = bot_tf.paragraphs[0]
    p_b.text = "Regra de Isolamento Absoluto: Nenhum perfil herda permissões de outro. O Administrador NÃO lança notas nem altera avaliações. O Aluno NUNCA tem visibilidade de gabaritos ou notas antes da publicação formal."
    p_b.font.name = FONT_NAME
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_DANGER
    
    # -------------------------------------------------------------
    # SLIDE 5: VISÃO GERAL DA SOLUÇÃO (FLUXO EM 8 ETAPAS)
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, prs, C_LIGHT_BG)
    add_header(s5, "O Ciclo Operacional da Avaliação em 8 Etapas", "FLUXO PONTA A PONTA")
    
    steps = [
        ("1. Criação da Prova", "Professor cadastra questões (objetivas e discursivas), rubricas e pontuação total validada."),
        ("2. Versionamento", "Sistema valida a soma dos pontos e congela uma versão imutável do exame no banco."),
        ("3. Geração de PDF & QR", "Geração de PDFs padronizados com QR Code exclusivo para identificação de cada aluno."),
        ("4. Aplicação Presencial", "Aplicação tradicional em sala de aula; estudantes respondem na folha física de papel."),
        ("5. Digitalização & Upload", "Folhas respondidas são escaneadas ou fotografadas e enviadas ao sistema pelo docente."),
        ("6. OCR & Análise por IA", "OpenCV/Tesseract extraem texto; LLM compara com gabarito e sugere nota + justificativa."),
        ("7. Revisão Docente", "Revisão humana obrigatória: professor confere, ajusta pontuação ou aprova com 1 clique."),
        ("8. Publicação das Notas", "Notas são salvas no diário oficial e liberadas imediatamente no Portal do Aluno.")
    ]
    
    step_w = Inches(2.7)
    step_h = Inches(2.25)
    
    for idx, (title_st, desc_st) in enumerate(steps):
        row = idx // 4
        col = idx % 4
        l_pos = Inches(0.8) + col * Inches(2.98)
        t_pos = Inches(1.8) + row * Inches(2.55)
        
        acc_c = C_PRIMARY if idx < 3 else (C_WARNING if idx == 3 else (C_ACCENT_TEAL if idx < 6 else C_SUCCESS))
        create_card(s5, l_pos, t_pos, step_w, step_h, accent_top_color=acc_c)
        
        tb = s5.shapes.add_textbox(l_pos + Inches(0.15), t_pos + Inches(0.15), step_w - Inches(0.3), step_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title_st
        p_t.font.name = FONT_NAME
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = acc_c
        p_t.space_after = Pt(8)
        
        p_d = tf.add_paragraph()
        p_d.text = desc_st
        p_d.font.name = FONT_NAME
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_TEXT_DARK
        
    # -------------------------------------------------------------
    # SLIDE 6: ARQUITETURA DO SISTEMA (MODULAR EM CAMADAS)
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, prs, C_DARK_BG)
    add_header(s6, "Arquitetura Modular em Camadas e Desacoplamento", "ENGENHARIA DE SOFTWARE", is_dark=True)
    
    layers = [
        ("Camada de Apresentação (Frontend)", "Interface web estática servida pelo FastAPI. Portais especializados (Aluno, Professor, Admin). HTML5 semântico, CSS3 com Design System institucional, Vanilla JS ES2020 e telemetria reativa.", C_ACCENT_CYAN),
        ("Camada de API & Controle (FastAPI)", "Servidor ASGI assíncrono (Uvicorn). Endpoints REST organizados por domínio (Auth, Acadêmico, Provas, Correção, Auditoria). Validação estrita de contratos via Pydantic v2 e segurança JWT.", C_PRIMARY),
        ("Camada de Domínio & Negócio (Services)", "Regras de negócio isoladas (RN01 a RN45). Validação de gabaritos, cálculo de médias, verificação de atribuições docentes, pipelines de auditoria e orquestração de tarefas assíncronas.", C_ACCENT_TEAL),
        ("Camada de Dados & Persistência (ORM)", "SQLAlchemy 2.0 com Repositórios desacoplados. Migrações automáticas via Alembic. Suporte híbrido transparente: SQLite para desenvolvimento local e PostgreSQL corporativo em produção.", C_WARNING),
        ("Camada de Visão Computacional & IA", "Pipelines de OCR com OpenCV (alinhamento/binarização) e PyTesseract/PyMuPDF. Gateway plugável de IA: Ollama (LLM local sem custos), Claude via FCC, NVIDIA NIM e MockProvider de testes.", C_SUCCESS)
    ]
    
    l_top = Inches(1.8)
    l_h = Inches(0.96)
    l_gap = Inches(0.12)
    
    for idx, (l_title, l_desc, l_color) in enumerate(layers):
        pos_y = l_top + idx * (l_h + l_gap)
        create_card(s6, Inches(0.8), pos_y, Inches(11.73), l_h, is_dark=True, accent_top_color=l_color)
        
        tb = s6.shapes.add_textbox(Inches(1.0), pos_y + Inches(0.1), Inches(11.33), l_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = l_title
        p.font.name = FONT_NAME
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = l_color
        p.space_after = Pt(2)
        
        p_d = tf.add_paragraph()
        p_d.text = l_desc
        p_d.font.name = FONT_NAME
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_TEXT_LIGHT_MUTED
        
    # -------------------------------------------------------------
    # SLIDE 7: STACK TECNOLÓGICA COMPLETA
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, prs, C_LIGHT_BG)
    add_header(s7, "Stack Tecnológica e Ferramentas Utilizadas", "TECNOLOGIAS & FERRAMENTAS")
    
    cols_tech = [
        ("Backend & API", C_PRIMARY, [
            "Python 3.12 (Linguagem Principal)",
            "FastAPI + Uvicorn (Framework REST ASGI)",
            "Pydantic v2 (Validação de Schemas)",
            "SQLAlchemy 2.0 (ORM Relacional)",
            "Alembic (Migrações Versionadas)",
            "Passlib + Argon2id (Hash de Senhas)",
            "python-jose (Autenticação JWT)"
        ]),
        ("Frontend & UX", C_ACCENT_TEAL, [
            "HTML5 Semântico & Acessível",
            "CSS3 (Design System próprio, Flex/Grid)",
            "JavaScript Vanilla ES2020 (Sem dependências)",
            "Fetch API + XMLHttpRequest (Upload)",
            "Server-Side Asset Versioning (Anti-Cache)",
            "Componentes Reativos de Progresso",
            "Suporte Completo a Dispositivos Móveis"
        ]),
        ("IA & Visão", C_WARNING, [
            "Tesseract OCR (Reconhecimento de Texto)",
            "OpenCV (Processamento e Rotação)",
            "PyMuPDF / ReportLab (Manipulação PDF)",
            "qrcode + Pillow (Geração de QR Codes)",
            "Ollama (LLM Local Gratuito)",
            "FCC / Anthropic Claude / NVIDIA NIM",
            "MockProvider (Testes Determinísticos)"
        ]),
        ("DevOps & QA", C_SUCCESS, [
            "Git & GitHub (Controle de Versão)",
            "GitFlow (main, develop, feature/*)",
            "GitHub Actions (Pipeline de CI/CD)",
            "Pytest + Pytest-Asyncio + Pytest-Mock",
            "Pytest-Cov (Cobertura de Código)",
            "Ruff (Linter e Formatador Estático)",
            "Relatórios de QA em HTML e XML/JUnit"
        ])
    ]
    
    col_w = Inches(2.76)
    col_gap = Inches(0.23)
    c_top = Inches(1.8)
    c_h = Inches(5.1)
    
    for idx, (t_name, t_color, t_items) in enumerate(cols_tech):
        l_pos = Inches(0.8) + idx * (col_w + col_gap)
        create_card(s7, l_pos, c_top, col_w, c_h, accent_top_color=t_color)
        
        tb = s7.shapes.add_textbox(l_pos + Inches(0.15), c_top + Inches(0.15), col_w - Inches(0.3), c_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = t_name
        p.font.name = FONT_NAME
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = t_color
        p.space_after = Pt(12)
        
        add_bullet_points(tf, t_items, font_size=11, space_after=8)
        
    # -------------------------------------------------------------
    # SLIDE 8: BANCO DE DADOS E MODELO ER
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, prs, C_LIGHT_BG)
    add_header(s8, "Engenharia de Dados: Persistência, Integridade e Migrações", "BANCO DE DADOS & MODELAGEM")
    
    # Left Column: Structure Cards
    left_w = Inches(6.8)
    create_card(s8, Inches(0.8), Inches(1.8), left_w, Inches(5.1), accent_top_color=C_PRIMARY)
    tb_er = s8.shapes.add_textbox(Inches(1.0), Inches(1.95), left_w - Inches(0.4), Inches(4.8))
    tf_er = tb_er.text_frame
    tf_er.word_wrap = True
    
    p = tf_er.paragraphs[0]
    p.text = "Estrutura do Modelo Entidade-Relacionamento (+40 Tabelas)"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_er, [
        "Usuários & Autenticação: Users, Roles, RefreshTokens, UserSessions.",
        "Estrutura Acadêmica: Courses, Subjects, Classes, Students, AcademicTerms, AcademicAssignments (docentes vinculados à turma/disciplina).",
        "Avaliações & Imutabilidade: Exams, ExamVersions (gabarito congelado pós-publicação), Questions, Rubrics, QuestionCriteria.",
        "Impressão & Rastreabilidade: ExamCopies (folha única por aluno), QRCodes, PrintedBatches.",
        "Correção & IA: Submissions, SubmissionPages, ExtractedAnswers, Corrections (nota, justificativa e confiança), ReviewAudits.",
        "Operações Longas: BackgroundTasks, ProgressBars, UploadSessions, AuditLogs imutáveis."
    ], space_after=8, font_size=12)
    
    # Right Column: Highlights
    right_w = Inches(4.65)
    r_left = Inches(7.88)
    
    add_stat_card(s8, r_left, Inches(1.8), right_w, Inches(1.1), "UUID v4", "Chaves Primárias Universais e Seguras", color=C_ACCENT_CYAN)
    add_stat_card(s8, r_left, Inches(3.05), right_w, Inches(1.1), "Alembic", "Controle Estrito de Versões de Schema", color=C_PRIMARY)
    add_stat_card(s8, r_left, Inches(4.3), right_w, Inches(1.1), "Imutabilidade", "Versão da Prova Congelada após Publicar", color=C_SUCCESS)
    add_stat_card(s8, r_left, Inches(5.55), right_w, Inches(1.1), "Híbrido", "SQLite (Dev local) / PostgreSQL (Produção)", color=C_WARNING)
    
    # -------------------------------------------------------------
    # SLIDE 9: SEGURANÇA DA INFORMAÇÃO E LGPD
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, prs, C_LIGHT_BG)
    add_header(s9, "Segurança da Informação, LGPD e Mitigação de Riscos", "SEGURANÇA & COMPLIANCE")
    
    table_headers = ["Vetor de Ameaça", "Impacto Potencial", "Controle Implementado no EduGrade", "Conformidade"]
    table_rows = [
        ["Acesso Indevido a Turmas", "Professor visualizar/alterar notas de outro colega", "Permissões contextuais em academic_assignments verificadas em cada requisição", "RBAC Estrito"],
        ["Vazamento de Senhas", "Comprometimento de credenciais institucionais", "Hash Argon2id com salt aleatório e proteção contra timing attacks", "OWASP ASVS"],
        ["Fraude em Notas", "Alteração não autorizada de notas de alunos", "Logs imutáveis em AuditLog com IP, usuário, data e valor anterior/novo", "Rastreabilidade"],
        ["Prompt Injection na Prova", "Aluno escrever comandos na folha para burlar a IA", "Folha tratada como dado não-confiável: prompts fixos e regras isoladas", "Segurança em IA"],
        ["Privacidade / LGPD", "Envio indevido de dados pessoais a terceiros", "Opção de IA 100% local (Ollama); chaves externas criptografadas com chave mestra", "LGPD Art. 6º e 46"]
    ]
    
    add_table_custom(s9, Inches(0.8), Inches(1.8), Inches(11.73), Inches(5.1), table_headers, table_rows,
                     col_widths=[Inches(2.5), Inches(2.8), Inches(4.6), Inches(1.83)])
                     
    # -------------------------------------------------------------
    # SLIDE 10: PORTAL DO ALUNO COM EVIDÊNCIA
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, prs, C_LIGHT_BG)
    add_header(s10, "Portal do Aluno: Transparência e Acompanhamento Contínuo", "EXPERIÊNCIA DO ESTUDANTE")
    
    # Left Text
    create_card(s10, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1), accent_top_color=C_ACCENT_CYAN)
    tb_aluno = s10.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.1), Inches(4.8))
    tf_aluno = tb_aluno.text_frame
    tf_aluno.word_wrap = True
    
    p = tf_aluno.paragraphs[0]
    p.text = "Funcionalidades Centrais do Aluno"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY_DARK
    p.space_after = Pt(10)
    
    add_bullet_points(tf_aluno, [
        "Dashboard Geral: Visão rápida do curso, turma, período letivo, média global ponderada e índice de frequência.",
        "Minhas Notas: Consulta detalhada das avaliações realizadas, notas obtidas e status de publicação oficial.",
        "Minhas Provas: Visualização apenas de provas publicadas das turmas onde está regularmente matriculado.",
        "Frequência Acadêmica: Presenças, faltas registradas, justificativas médicas e percentual por matéria.",
        "Grade Horária: Quadro semanal interativo com horários, salas de aula e professores das disciplinas.",
        "Sigilo Absoluto: Provas e notas em rascunho NUNCA são expostas antes da homologação docente."
    ], space_after=8, font_size=12)
    
    # Right Image
    img_aluno = os.path.join("docs", "QA", "evidencias", "aluno-dashboard.png")
    if os.path.exists(img_aluno):
        create_card(s10, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1), accent_top_color=C_PRIMARY)
        s10.shapes.add_picture(img_aluno, Inches(6.75), Inches(2.0), width=Inches(5.63))
    else:
        create_card(s10, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1))
        
    # -------------------------------------------------------------
    # SLIDE 11: PORTAL DO PROFESSOR COM EVIDÊNCIA
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, prs, C_LIGHT_BG)
    add_header(s11, "Portal do Professor: O Coração da Gestão de Avaliações", "EXPERIÊNCIA DOCENTE")
    
    # Left Text
    create_card(s11, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1), accent_top_color=C_PRIMARY)
    tb_prof = s11.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.1), Inches(4.8))
    tf_prof = tb_prof.text_frame
    tf_prof.word_wrap = True
    
    p = tf_prof.paragraphs[0]
    p.text = "Gerenciamento Completo de Turmas e Provas"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_prof, [
        "Construtor de Provas: Criação de questões objetivas (múltipla escolha) e discursivas com critérios claros de pontuação.",
        "Gabaritos com Rubricas: Definição de respostas-padrão, palavras-chave e conceitos obrigatórios para nortear a IA.",
        "Validação Matemática Rígida: O sistema bloqueia a publicação caso a soma dos pontos das questões discorde do total do exame.",
        "Importação Inteligente de Provas: Leitura de provas existentes em PDF com pré-preenchimento automático via IA.",
        "Envio de Provas Respondidas: Upload em lote ou individual de arquivos PDF ou fotos das folhas de respostas.",
        "Fila de Correção & Diário: Tela dedicada para homologação de notas e publicação instantânea no diário acadêmico."
    ], space_after=8, font_size=12)
    
    # Right Image
    img_prof = os.path.join("docs", "QA", "evidencias", "professor-dashboard.png")
    if os.path.exists(img_prof):
        create_card(s11, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1), accent_top_color=C_PRIMARY)
        s11.shapes.add_picture(img_prof, Inches(6.75), Inches(2.0), width=Inches(5.63))
    else:
        create_card(s11, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1))
        
    # -------------------------------------------------------------
    # SLIDE 12: CRIAÇÃO, VERSIONAMENTO E IMPRESSÃO COM QR CODE
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, prs, C_LIGHT_BG)
    add_header(s12, "Padronização de Provas, Impressão e QR Code Anti-Fraude", "AVALIAÇÃO EM PAPEL")
    
    col_w = Inches(3.64)
    gap = Inches(0.38)
    
    # Card 1: Geração Padronizada
    create_card(s12, Inches(0.8), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_PRIMARY)
    tb1 = s12.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Geração de PDF (ReportLab)"
    p1.font.name = FONT_NAME
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = C_PRIMARY
    p1.space_after = Pt(10)
    add_bullet_points(tf1, [
        "Layout tipográfico padronizado e otimizado para economia de papel.",
        "Campos definidos para preenchimento de nome, RA e assinatura.",
        "Grade de respostas objetivas e áreas demarcadas para respostas discursivas.",
        "Separação física estrita: PDF do aluno NÃO contém informações do gabarito."
    ], space_after=8, font_size=12)
    
    # Card 2: QR Code por Cópia
    create_card(s12, Inches(0.8 + 3.64 + 0.38), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_ACCENT_TEAL)
    tb2 = s12.shapes.add_textbox(Inches(0.8 + 3.64 + 0.38 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "QR Code de Rastreabilidade"
    p2.font.name = FONT_NAME
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = C_ACCENT_TEAL
    p2.space_after = Pt(10)
    add_bullet_points(tf2, [
        "Cada folha de prova recebe um QR Code criptografado exclusivo no cabeçalho.",
        "Vincula univocamente: Aluno, Turma, Disciplina, Avaliação e Versão do Gabarito.",
        "Evita trocas de folhas, fraudes de identificação e confusão de turmas.",
        "Reconhecimento instantâneo na fase de digitalização via OpenCV."
    ], space_after=8, font_size=12)
    
    # Card 3: Impressão Flexível
    create_card(s12, Inches(0.8 + (3.64 + 0.38) * 2), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_SUCCESS)
    tb3 = s12.shapes.add_textbox(Inches(0.8 + (3.64 + 0.38) * 2 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "Impressão em Lote e Avulsa"
    p3.font.name = FONT_NAME
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = C_SUCCESS
    p3.space_after = Pt(10)
    add_bullet_points(tf3, [
        "Impressão em lote com 1 clique para todos os alunos matriculados na turma.",
        "Geração de cópias avulsas identificadas para alunos de segunda chamada.",
        "Impressão paralela da Folha de Gabarito Mestre exclusiva do professor.",
        "Suporte a download direto de pacote ZIP com todas as provas montadas."
    ], space_after=8, font_size=12)
    
    # Bottom Note
    bot_card = create_card(s12, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7), accent_top_color=C_PRIMARY_DARK)
    bot_tb = s12.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.33), Inches(0.55))
    bot_tf = bot_tb.text_frame
    bot_tf.word_wrap = True
    p_b = bot_tf.paragraphs[0]
    p_b.text = "Garantia de Integridade: Ao publicar a prova, a versão é congelada (imutável). Qualquer alteração posterior exige gerar uma nova versão, garantindo que o gabarito utilizado na correção seja exatamente o aplicado na prova."
    p_b.font.name = FONT_NAME
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_PRIMARY_DARK
    
    # -------------------------------------------------------------
    # SLIDE 13: PIPELINE DE IA E OCR (CORREÇÃO ASSISTIDA)
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, prs, C_LIGHT_BG)
    add_header(s13, "Pipeline de Visão Computacional, OCR e Análise por LLM", "IA & PROCESSAMENTO")
    
    steps_ai = [
        ("1. Pré-Processamento (OpenCV)", "Correção automática de ângulo e rotação da folha digitalizada, ajuste de contraste, binarização e isolamento das caixas de respostas."),
        ("2. Reconhecimento OCR (Tesseract)", "Varredura óptica dos caracteres manuscritos e impressos com segmentação por questão demarcada na folha da prova."),
        ("3. Fallback Inteligente de PDF", "Se o PDF enviado já contiver texto digital selecionável (PyMuPDF), o sistema utiliza a camada nativa, garantindo 100% de precisão sem OCR."),
        ("4. Raciocínio Semântico (LLM)", "O modelo de linguagem recebe: enunciado, resposta extraída, gabarito e rubricas com critérios obrigatórios e pontuação máxima."),
        ("5. Estruturação do Veredito", "A IA retorna payload padronizado: nota sugerida, justificativa didática, critérios atendidos/não atendidos e índice de confiança (0-100%).")
    ]
    
    for idx, (st_t, st_d) in enumerate(steps_ai):
        pos_y = Inches(1.8) + idx * Inches(1.02)
        c_color = C_ACCENT_CYAN if idx == 0 else (C_PRIMARY if idx == 1 else (C_ACCENT_TEAL if idx == 2 else (C_WARNING if idx == 3 else C_SUCCESS)))
        create_card(s13, Inches(0.8), pos_y, Inches(11.73), Inches(0.92), accent_top_color=c_color)
        
        tb = s13.shapes.add_textbox(Inches(1.0), pos_y + Inches(0.08), Inches(11.33), Inches(0.76))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = st_t
        p.font.name = FONT_NAME
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = c_color
        p.space_after = Pt(2)
        
        p2 = tf.add_paragraph()
        p2.text = st_d
        p2.font.name = FONT_NAME
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_DARK
        
    # -------------------------------------------------------------
    # SLIDE 14: HUMAN-IN-THE-LOOP & REVISÃO OBRIGATÓRIA
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, prs, C_LIGHT_BG)
    add_header(s14, "Human-in-the-Loop: A IA como Assistente, Nunca Decisora", "CONTROLE HUMANO & ÉTICA")
    
    col_w = Inches(3.64)
    gap = Inches(0.38)
    
    # Card 1: RN06 & RN07
    create_card(s14, Inches(0.8), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_DANGER)
    tb1 = s14.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Regras RN06 & RN07"
    p1.font.name = FONT_NAME
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = C_DANGER
    p1.space_after = Pt(10)
    add_bullet_points(tf1, [
        "A Inteligência Artificial opera sob o papel estrito de sugestora.",
        "NENHUMA nota gerada por algoritmo é lançada diretamente no boletim.",
        "A publicação depende impreterivelmente do clique de aprovação do professor.",
        "Blindagem contra alucinações e variações imprevistas do modelo."
    ], space_after=8, font_size=12)
    
    # Card 2: Interface Lado a Lado
    create_card(s14, Inches(0.8 + 3.64 + 0.38), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_PRIMARY)
    tb2 = s14.shapes.add_textbox(Inches(0.8 + 3.64 + 0.38 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Conferência Lado a Lado"
    p2.font.name = FONT_NAME
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = C_PRIMARY
    p2.space_after = Pt(10)
    add_bullet_points(tf2, [
        "Tela exibe a imagem original da folha escaneada ao lado do texto extraído.",
        "Destaque visual para trechos onde a IA detectou conceitos obrigatórios.",
        "Indicador de Confiança: sinaliza leituras ambíguas para atenção docente imediata.",
        "Professor pode reescrever a justificativa ou corrigir o texto do OCR."
    ], space_after=8, font_size=12)
    
    # Card 3: Ações de Revisão
    create_card(s14, Inches(0.8 + (3.64 + 0.38) * 2), Inches(1.8), col_w, Inches(4.3), accent_top_color=C_SUCCESS)
    tb3 = s14.shapes.add_textbox(Inches(0.8 + (3.64 + 0.38) * 2 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(3.9))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "Poder Decisório Docente"
    p3.font.name = FONT_NAME
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = C_SUCCESS
    p3.space_after = Pt(10)
    add_bullet_points(tf3, [
        "Aprovar Nota: confirma a sugestão da IA com apenas um clique.",
        "Ajustar Pontuação: altera a nota livremente com recalculo instantâneo.",
        "Marcar como Ilegível: encaminha a questão para verificação manual na prova física.",
        "Auditoria de Revisão: salva quem alterou, quando e o motivo do ajuste."
    ], space_after=8, font_size=12)
    
    # Bottom Note
    bot_card = create_card(s14, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7), accent_top_color=C_PRIMARY)
    bot_tb = s14.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.33), Inches(0.55))
    bot_tf = bot_tb.text_frame
    bot_tf.word_wrap = True
    p_b = bot_tf.paragraphs[0]
    p_b.text = "Benefício Real: O docente elimina o esforço braçal e repetitivo de conferir respostas óbvias e somar notas à mão, concentrando seu tempo e julgamento crítico exclusivamente nos casos de borda e dúvidas conceituais."
    p_b.font.name = FONT_NAME
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_PRIMARY_DARK
    
    # -------------------------------------------------------------
    # SLIDE 15: OPERAÇÕES ASSÍNCRONAS E BARRA GLOBAL DE PROGRESSO
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, prs, C_LIGHT_BG)
    add_header(s15, "Operações de Longa Duração e Telemetria em Tempo Real", "UX & ASSINCRONISMO")
    
    # Left Box
    create_card(s15, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.1), accent_top_color=C_PRIMARY)
    tb_prog = s15.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(6.4), Inches(4.8))
    tf_prog = tb_prog.text_frame
    tf_prog.word_wrap = True
    p = tf_prog.paragraphs[0]
    p.text = "Componente Global de Progresso Reativo"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_prog, [
        "Desafio: Upload de dezenas de provas, OCR e inferências de IA são operações demoradas que não podem bloquear a interface nem gerar timeouts de requisição.",
        "Telemetria Baseada no Backend: O backend é a única fonte da verdade, computando o progresso real por questões e páginas processadas.",
        "Uploads Precisos: Percentual real medido byte a byte via XMLHttpRequest.upload, exibindo velocidade e tempo estimado de conclusão.",
        "Resiliência a Falhas de Conexão: Se o usuário recarregar o navegador durante o processamento, a barra reconecta à sessão e retoma o status.",
        "Cancelamento Cooperativo: O professor pode interromper uma tarefa em andamento com rollback seguro das etapas incompletas."
    ], space_after=8, font_size=12)
    
    # Right Column: 3 Operações Monitoradas
    right_w = Inches(4.65)
    r_left = Inches(7.88)
    
    add_stat_card(s15, r_left, Inches(1.8), right_w, Inches(1.5), "Uploads em Lote", "Transferência monitorada de PDFs e múltiplos arquivos de imagem", color=C_ACCENT_CYAN)
    add_stat_card(s15, r_left, Inches(3.55), right_w, Inches(1.5), "Processamento IA", "Acompanhamento em tempo real página a página das correções", color=C_PRIMARY)
    add_stat_card(s15, r_left, Inches(5.3), right_w, Inches(1.5), "Importação CSV", "Carga e validação de até 2.000 alunos e turmas com relatório de erros", color=C_SUCCESS)
    
    # -------------------------------------------------------------
    # SLIDE 16: PAINEL ADMINISTRATIVO E CENTRAL DE IA
    # -------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, prs, C_LIGHT_BG)
    add_header(s16, "Painel Administrativo, Auditoria e Central de IA", "GOVERNANÇA & INFRAESTRUTURA")
    
    # Left Text
    create_card(s16, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1), accent_top_color=C_PRIMARY)
    tb_adm = s16.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.1), Inches(4.8))
    tf_adm = tb_adm.text_frame
    tf_adm.word_wrap = True
    
    p = tf_adm.paragraphs[0]
    p.text = "Controle Central e Provedores de IA"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_adm, [
        "Gestão Acadêmica Completa: Criação e manutenção de cursos, matrizes curriculares, disciplinas, turmas e períodos letivos.",
        "Atribuição Docente: Vínculo seguro de professores a disciplinas específicas por período.",
        "Central de Provedores de IA: Troca dinâmica entre Ollama (local), Claude via FCC, NVIDIA NIM e MockProvider sem reiniciar o servidor.",
        "Cofre de Credenciais Criptografado: Chaves de API armazenadas com criptografia simétrica; nunca expostas no código.",
        "Diagnóstico de Conectividade: Teste em tempo real de comunicação e latência com os servidores de IA.",
        "Painel de Qualidade (QA): Execução da suíte de testes unitários com visualização de métricas e relatório HTML integrado."
    ], space_after=8, font_size=12)
    
    # Right Images (2 Stacked Cards)
    img_adm = os.path.join("docs", "QA", "evidencias", "admin-dashboard.png")
    img_fcc = os.path.join("docs", "QA", "evidencias", "fcc-settings.png")
    
    if os.path.exists(img_adm) and os.path.exists(img_fcc):
        create_card(s16, Inches(6.6), Inches(1.8), Inches(5.93), Inches(2.45), accent_top_color=C_PRIMARY)
        s16.shapes.add_picture(img_adm, Inches(6.75), Inches(1.95), width=Inches(5.63))
        
        create_card(s16, Inches(6.6), Inches(4.45), Inches(5.93), Inches(2.45), accent_top_color=C_ACCENT_TEAL)
        s16.shapes.add_picture(img_fcc, Inches(6.75), Inches(4.6), width=Inches(5.63))
    else:
        create_card(s16, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1))
        
    # -------------------------------------------------------------
    # SLIDE 17: ESTRATÉGIA DE TESTES E COBERTURA DE CÓDIGO
    # -------------------------------------------------------------
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, prs, C_LIGHT_BG)
    add_header(s17, "Garantia da Qualidade de Software: Testes e Cobertura", "QUALIDADE & TESTES")
    
    # Left Stats
    stat_w = Inches(3.64)
    add_stat_card(s17, Inches(0.8), Inches(1.8), stat_w, Inches(1.5), "262 Testes", "Bateria Automatizada (0 Reprovações)", color=C_SUCCESS)
    add_stat_card(s17, Inches(0.8), Inches(3.55), stat_w, Inches(1.5), "81,32%", "Cobertura Global de Código (Gate ≥ 80%)", color=C_PRIMARY)
    add_stat_card(s17, Inches(0.8), Inches(5.3), stat_w, Inches(1.6), "100% Mocked", "Testes de IA Determinísticos e Sem Custos", color=C_ACCENT_TEAL)
    
    # Right Text
    create_card(s17, Inches(4.75), Inches(1.8), Inches(7.78), Inches(5.1), accent_top_color=C_PRIMARY)
    tb_qa = s17.shapes.add_textbox(Inches(5.0), Inches(1.95), Inches(7.3), Inches(4.8))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True
    
    p = tf_qa.paragraphs[0]
    p.text = "Estratégia de Testes Automatizados (Pytest)"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_qa, [
        "Pirâmide de Testes Completa: Suíte composta por testes unitários e de integração cobrindo regras de negócio, persistência e rotas REST.",
        "Módulos Críticos 100% Cobertos: Autenticação JWT, permissões contextuais de docentes, cálculo de notas e médias, versionamento de provas, importação de PDFs e geração de QR Codes.",
        "Isolamento Rigoroso de Dados: Cada teste roda com banco SQLite em memória ou temporário (DADO_DE_TESTE_EDUGRADE), garantindo idempotência total.",
        "Ambiente de IA Desacoplado: MockProvider simula respostas estruturadas de LLM instantaneamente sem requisições de rede ou consumo de tokens.",
        "Relatórios de QA: Geração contínua de relatórios HTML (pytest-cov) e relatórios XML/JUnit consumidos pelo pipeline do GitHub Actions."
    ], space_after=8, font_size=12)
    
    # -------------------------------------------------------------
    # SLIDE 18: DEVOPS E PIPELINE DE CI/CD
    # -------------------------------------------------------------
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, prs, C_LIGHT_BG)
    add_header(s18, "Engenharia DevOps: GitFlow e Pipeline de CI/CD", "INTEGRAÇÃO CONTÍNUA")
    
    # Left Card: GitFlow
    create_card(s18, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1), accent_top_color=C_PRIMARY)
    tb_git = s18.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.1), Inches(4.8))
    tf_git = tb_git.text_frame
    tf_git.word_wrap = True
    p = tf_git.paragraphs[0]
    p.text = "Controle de Versão (GitFlow)"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(10)
    
    add_bullet_points(tf_git, [
        "Branches Padronizadas: main (código estável de produção), develop (integração contínua) e feature/* por área de atuação.",
        "Commits Convencionais: histórico limpo e rastreável com prefixos padronizados (feat:, fix:, test:, docs:, ci:).",
        "Proteção de Branches: merges na branch main exigem Pull Request revisado e aprovação dos testes no CI.",
        "Histórico Auditável: total sincronismo entre as branches locais e o repositório remoto no GitHub."
    ], space_after=8, font_size=12)
    
    # Right Card: CI/CD Pipeline
    create_card(s18, Inches(6.6), Inches(1.8), Inches(5.93), Inches(5.1), accent_top_color=C_ACCENT_TEAL)
    tb_ci = s18.shapes.add_textbox(Inches(6.8), Inches(1.95), Inches(5.53), Inches(4.8))
    tf_ci = tb_ci.text_frame
    tf_ci.word_wrap = True
    p = tf_ci.paragraphs[0]
    p.text = "Pipeline GitHub Actions (.github/workflows/ci.yml)"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_TEAL
    p.space_after = Pt(10)
    
    add_bullet_points(tf_ci, [
        "Trigger Automatizado: disparo em todo push e abertura de Pull Request direcionado a main ou develop.",
        "Job 1 - Linting & Qualidade: ruff check inspeciona sintaxe e boas práticas (falha imediata em erros E/F/W).",
        "Job 2 - Execução de Testes: pytest roda a suíte de testes com validação automática de threshold de cobertura.",
        "Job 3 - Publicação de Artefatos: upload dos relatórios de cobertura XML e HTML mantidos por 7 dias no GitHub.",
        "Job 4 - Syntax & Build Check: verificação de importações de módulos e integridade estrutural da API."
    ], space_after=8, font_size=12)
    
    # -------------------------------------------------------------
    # SLIDE 19: RESULTADOS ALCANÇADOS E ROADMAP
    # -------------------------------------------------------------
    s19 = prs.slides.add_slide(blank_layout)
    set_slide_background(s19, prs, C_LIGHT_BG)
    add_header(s19, "Resultados Alcançados, Limitações e Roadmap Futuro", "RESULTADOS & EVOLUÇÃO")
    
    col_w = Inches(3.64)
    gap = Inches(0.38)
    
    # Card 1: Entregas
    create_card(s19, Inches(0.8), Inches(1.8), col_w, Inches(5.1), accent_top_color=C_SUCCESS)
    tb1 = s19.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Resultados 100% Entregues"
    p1.font.name = FONT_NAME
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = C_SUCCESS
    p1.space_after = Pt(10)
    add_bullet_points(tf1, [
        "Plataforma Full Stack operacional com os 3 portais independentes integrados.",
        "Ciclo ponta a ponta validado: prova -> QR Code -> OCR -> IA -> revisão -> diário.",
        "262 testes automatizados aprovados e cobertura de 81,32% comprovada.",
        "Documentação técnica exaustiva: requisitos, regras de negócio e relatórios de QA.",
        "Pipeline CI/CD configurado e versionamento padronizado no GitHub."
    ], space_after=8, font_size=12)
    
    # Card 2: Limitações
    create_card(s19, Inches(0.8 + 3.64 + 0.38), Inches(1.8), col_w, Inches(5.1), accent_top_color=C_WARNING)
    tb2 = s19.shapes.add_textbox(Inches(0.8 + 3.64 + 0.38 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Limitações Transparentes"
    p2.font.name = FONT_NAME
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = C_WARNING
    p2.space_after = Pt(10)
    add_bullet_points(tf2, [
        "OCR de Caligrafia Cursiva: depende dos binários do Tesseract devidamente instalados no sistema host.",
        "Dependência de Hardware em LLMs Locais: modelos como Llama 3 no Ollama exigem GPU ou CPU potente para respostas rápidas.",
        "Volume de Importação: lote CSV atualmente parametrizado para teto de 2.000 linhas por arquivo.",
        "Dependência de Revisão: a IA não pode publicar sozinha (limitação desenhada por segurança ética)."
    ], space_after=8, font_size=12)
    
    # Card 3: Roadmap
    create_card(s19, Inches(0.8 + (3.64 + 0.38) * 2), Inches(1.8), col_w, Inches(5.1), accent_top_color=C_PRIMARY)
    tb3 = s19.shapes.add_textbox(Inches(0.8 + (3.64 + 0.38) * 2 + 0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "Próximos Passos (Roadmap)"
    p3.font.name = FONT_NAME
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = C_PRIMARY
    p3.space_after = Pt(10)
    add_bullet_points(tf3, [
        "Conteinerização Total: disponibilizar Docker Compose e manifests Kubernetes (K8s) para deploy em nuvem.",
        "Visão Multimodal Nativa: integrar modelos Vision (como Claude 3.5 Sonnet Vision e Llama 3.2 Vision) para dispensar OCR intermediário.",
        "App Mobile para Docentes: aplicativo para fotografar e enviar provas diretamente da câmera do smartphone.",
        "Analytics Avançado: relatórios preditivos de defasagem de conteúdo por matéria."
    ], space_after=8, font_size=12)
    
    # -------------------------------------------------------------
    # SLIDE 20: CONCLUSÃO E MATRIZ DE RESPONSABILIDADES (DARK)
    # -------------------------------------------------------------
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20, prs, C_DARK_BG)
    add_header(s20, "Conclusão e Matriz de Entregas da Equipe", "FECHAMENTO & RESPONSABILIDADES", is_dark=True)
    
    # Top Quote
    q_card = create_card(s20, Inches(0.8), Inches(1.8), Inches(11.73), Inches(1.1), is_dark=True, accent_top_color=C_SUCCESS)
    q_tb = s20.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.33), Inches(0.9))
    q_tf = q_tb.text_frame
    q_tf.word_wrap = True
    p_q = q_tf.paragraphs[0]
    p_q.text = "“O EduGrade comprova que é viável unir o poder da Inteligência Artificial e a disciplina da Engenharia de Software para transformar a rotina pedagógica: devolvendo tempo precioso aos professores, fornecendo feedbacks profundos aos estudantes e garantindo rigor, segurança e transparência em cada nota lançada.”"
    p_q.font.name = FONT_NAME
    p_q.font.size = Pt(12.5)
    p_q.font.bold = True
    p_q.font.color.rgb = C_TEXT_LIGHT
    
    # Table of Deliverables
    deliv_headers = ["Integrante", "RA", "Papel Estratégico", "Principais Entregas Comprovadas"]
    deliv_rows = [
        ["Gabriel Ferreira", "325140970", "DevOps & Gestão", "Organização do GitHub, GitFlow, Pipeline CI/CD (.github/workflows), Roteiro A3, Apresentação PPTX e Pitch."],
        ["Fernando Almeida", "326132695", "Full Stack Developer", "Backend (FastAPI, SQLAlchemy, Alembic), Frontend completo (Portais Aluno, Prof, Admin) e Testes Unitários."],
        ["Lucas Henrique Miranda", "325131396", "QA & Documentação", "Garantia da Qualidade, Matriz de Testes, Documentação Técnica (Requisitos RF, Regras RN, Setup) e Validação."],
        ["Caio Durães", "325132875", "IA & Integrações", "Módulo de IA/OCR (Tesseract, PyMuPDF, OpenCV), Provedores LLM (Ollama, Claude, NIM), Correção Assistida e PDFs."]
    ]
    
    add_table_custom(s20, Inches(0.8), Inches(3.1), Inches(11.73), Inches(3.8), deliv_headers, deliv_rows,
                     col_widths=[Inches(2.5), Inches(1.3), Inches(2.2), Inches(5.73)], is_dark=True)
                     
    # Save Presentation
    output_path = "EduGrade_Apresentacao_A3.pptx"
    prs.save(output_path)
    print(f"Apresentação gerada com sucesso: {output_path}")
    
    # Also save in docs/
    docs_path = os.path.join("docs", "EduGrade_Apresentacao_A3.pptx")
    prs.save(docs_path)
    print(f"Cópia salva em docs: {docs_path}")

if __name__ == "__main__":
    main()

