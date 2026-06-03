from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

# FIX 1: Save path (use current directory)
doc = SimpleDocTemplate(
    "IoT_QA_KeyPoints.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'T', parent=styles['Title'],
    fontSize=18,
    textColor=colors.HexColor('#2E3192'),
    spaceAfter=4
)

sub_style = ParagraphStyle(
    'S', parent=styles['Normal'],
    fontSize=10,
    textColor=colors.grey,
    alignment=1,
    spaceAfter=14
)

sec_style = ParagraphStyle(
    'SEC', parent=styles['Normal'],
    fontSize=12,
    textColor=colors.white,
    backColor=colors.HexColor('#2E3192'),
    fontName='Helvetica-Bold',
    spaceAfter=10,
    spaceBefore=14,
    borderPadding=6
)

q_style = ParagraphStyle(
    'Q', parent=styles['Normal'],
    fontSize=11,
    fontName='Helvetica-Bold',
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=4,
    spaceBefore=12
)

bullet_style = ParagraphStyle(
    'B', parent=styles['Normal'],
    fontSize=10,
    textColor=colors.HexColor('#222222'),
    leftIndent=14,
    spaceAfter=2,
    leading=14
)

story = []

# Title
story.append(Paragraph("IoT — Question Key Points", title_style))
story.append(Paragraph("Clustering · Data Fusion · Fog Computing", sub_style))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2E3192')))
story.append(Spacer(1, 0.3*cm))

# Helper functions
def section(title):
    story.append(Paragraph(title, sec_style))

def question(text):
    story.append(Paragraph(text, q_style))

def points(pts):
    for p in pts:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 0.2*cm))

# Sample Content
section("SECTION A: Clustering in IoT")

question("What is clustering?")
points([
    "Grouping nodes based on similarity",
    "Reduces communication cost",
    "Improves scalability",
    "Saves energy"
])

section("SECTION B: Data Fusion")

question("What is data fusion?")
points([
    "Combining multiple sensor data",
    "Improves decision accuracy",
    "Reduces redundancy"
])

# Build PDF
doc.build(story)

print("✅ PDF generated successfully!")