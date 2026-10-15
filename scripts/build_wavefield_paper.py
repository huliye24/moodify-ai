"""Build Moodify Open Technology Note 001 as a publication-style PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path("output/pdf/Moodify_From_Waveform_to_Wavefield_Technology_Note_001.pdf")
PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
MARGIN_B = 16 * mm
GUTTER = 7 * mm
HEADER_H = 10 * mm
BLUE = colors.HexColor("#00687F")
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555B65")
PALE = colors.HexColor("#EEF7F9")
LINE = colors.HexColor("#AEB7BC")


class Equation(Flowable):
    def __init__(self, text: str, number: int, width: float):
        super().__init__()
        self.text = text
        self.number = number
        self.width = width
        self.height = 15 * mm

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F5F8F9"))
        canvas.roundRect(0, 0, self.width, self.height, 2 * mm, fill=1, stroke=0)
        canvas.setFillColor(INK)
        font_size = 11 if len(self.text) < 44 else (8.0 if len(self.text) < 64 else 6.7)
        canvas.setFont("Times-Italic", font_size)
        canvas.drawCentredString(self.width / 2, 6 * mm, self.text)
        canvas.setFont("Times-Roman", 8.5)
        canvas.drawRightString(self.width - 3 * mm, 6 * mm, f"({self.number})")
        canvas.restoreState()


class ArchitectureFigure(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 43 * mm

    def draw(self):
        c = self.canv
        labels = [
            ("Waveform", "immutable source"),
            ("HEAR", "source evidence"),
            ("Wavefield", "model or studio"),
            ("Render", "sound occurs"),
            ("HEAR", "field evidence"),
            ("JUDGE", "accept / retry / original"),
        ]
        gap = 2.2 * mm
        box_w = (self.width - gap * (len(labels) - 1)) / len(labels)
        y = 14 * mm
        for index, (title, note) in enumerate(labels):
            x = index * (box_w + gap)
            c.setFillColor(PALE if index not in {0, 5} else colors.white)
            c.setStrokeColor(BLUE)
            c.roundRect(x, y, box_w, 16 * mm, 1.2 * mm, fill=1, stroke=1)
            c.setFillColor(BLUE)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(x + box_w / 2, y + 10 * mm, title)
            if index < len(labels) - 1:
                ax = x + box_w
                ay = y + 8 * mm
                c.setStrokeColor(INK)
                c.line(ax + .5 * mm, ay, ax + gap - .5 * mm, ay)
                c.line(ax + gap - 1.6 * mm, ay + 1.2 * mm, ax + gap - .5 * mm, ay)
                c.line(ax + gap - 1.6 * mm, ay - 1.2 * mm, ax + gap - .5 * mm, ay)
        c.setFillColor(MUTED)
        c.setFont("Times-Roman", 7)
        c.drawString(0, 5 * mm, "Figure 1: Moodify wavefield observation and constrained selection loop.")


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="Times-Roman", fontSize=8.6,
    leading=10.2, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=2.2 * mm,
)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=7.2, leading=8.5)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=10.4,
    leading=12, textColor=BLUE, spaceBefore=3.5 * mm, spaceAfter=1.5 * mm,
)
H2 = ParagraphStyle(
    "H2", parent=H1, fontSize=8.7, leading=10.2, textColor=INK,
    spaceBefore=2.2 * mm, spaceAfter=.8 * mm,
)
CAPTION = ParagraphStyle("Caption", parent=SMALL, fontSize=6.8, leading=8, alignment=TA_LEFT)
REF = ParagraphStyle("Reference", parent=SMALL, leftIndent=4 * mm, firstLineIndent=-4 * mm, spaceAfter=1.2 * mm)


def p(text: str, style=BODY):
    return Paragraph(text, style)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(INK)
    canvas.setLineWidth(.35)
    canvas.line(MARGIN_X, PAGE_H - 13 * mm, PAGE_W - MARGIN_X, PAGE_H - 13 * mm)
    canvas.setFont("Times-Roman", 7.5)
    canvas.drawString(MARGIN_X, PAGE_H - 10 * mm, "Moodify Open Technology Note MFY-TN-001")
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 10 * mm, "From Waveform to Wavefield")
    canvas.drawCentredString(PAGE_W / 2, 8 * mm, str(doc.page))
    canvas.restoreState()


def first_page(canvas, doc):
    header_footer(canvas, doc)
    canvas.saveState()
    top = PAGE_H - 25 * mm
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, top, "Moodify Wavefield Engineering Architecture")
    canvas.setFillColor(INK)
    canvas.setFont("Times-Bold", 20)
    title = "From Waveform to Wavefield: Observable Field"
    canvas.drawCentredString(PAGE_W / 2, top - 12 * mm, title)
    canvas.drawCentredString(PAGE_W / 2, top - 21 * mm, "Optimization for Music Reproduction")
    canvas.setFont("Times-Roman", 11)
    canvas.drawCentredString(PAGE_W / 2, top - 31 * mm, "Xuanzhen Zhu")
    canvas.setFont("Times-Roman", 8.7)
    canvas.drawCentredString(PAGE_W / 2, top - 37 * mm, "Moodify Sound Laboratory, Rongjing Wenchuan (Shenzhen) Technology Co., Ltd., Shenzhen, China")
    canvas.drawCentredString(PAGE_W / 2, top - 42 * mm, "Manuscript type: Open Technology Note - Canon and research program")
    abstract = (
        "<b>Abstract-</b>Digital audio is not the acoustic event itself; it is a condition from which an event may be reproduced. "
        "This note defines Moodify's transition from waveform-only processing to wavefield observation and optimization. "
        "A candidate field includes a target space, reproduction chain, propagation conditions, listener position, and evidence scope. "
        "Moodify HEAR observes the source and reproduced field; Moodify Judge determines whether a candidate improves the listening result while preserving identity, safety, and recoverability. "
        "The north-star formulation is F* = arg max J(Render(Audio,F)), refined in production as constrained robust optimization across target playback conditions. "
        "The note separates measured, simulated, and inferred evidence; rejects claims that a stereo file alone reconstructs a physical three-dimensional sound field; and proposes a Wavefield Profile, conditional renders, Judge records, and rollback as the persistent output."
    )
    frame = Frame(MARGIN_X + 8 * mm, top - 91 * mm, PAGE_W - 2 * (MARGIN_X + 8 * mm), 43 * mm, showBoundary=0)
    story = [p(abstract, ParagraphStyle("Abstract", parent=BODY, fontSize=8.1, leading=9.4)), p("<b>Keywords-</b>wavefield; audio intelligence; spatial reproduction; constrained optimization; auditory evidence; human review", SMALL)]
    frame.addFromList(story, canvas)
    canvas.restoreState()


def table(data, widths, font_size=6.8):
    header_style = ParagraphStyle("TableHead", parent=CAPTION, fontName="Helvetica-Bold", fontSize=font_size, leading=font_size + 1.4)
    cell_style = ParagraphStyle("TableCell", parent=CAPTION, fontName="Times-Roman", fontSize=font_size, leading=font_size + 1.4)
    wrapped = [
        [Paragraph(str(value), header_style if row_index == 0 else cell_style) for value in row]
        for row_index, row in enumerate(data)
    ]
    t = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 1.4),
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("GRID", (0, 0), (-1, -1), .25, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def build_story(column_width: float):
    story = [NextPageTemplate("Later")]
    story += [
        p("1 Introduction", H1),
        p("Most audio software treats a released file as the primary object of intervention. Equalization, dynamics, source separation, restoration, spatial processing, and mastering alter the waveform or generate a derived waveform. This view is useful but incomplete: a digital file does not become an acoustic event until a reproduction chain converts it into pressure variation in a physical or modeled space."),
        p("Moodify therefore distinguishes <i>waveform</i> from <i>wavefield</i>. A waveform is an encoded source. A wavefield is the conditioned event produced by a source, rendering process, transducer configuration, propagation environment, and listener position. The technical objective changes from finding a better file to finding a field in which the work is reproduced more effectively."),
        p("The contribution of this note is architectural rather than a claim of solved three-dimensional acoustics. It defines the optimization target, evidence boundary, persistent artifacts, and a staged research program. Current Moodify production capability remains file-domain analysis and stereo projection; calibrated physical-field capture is future work."),
        p("2 Problem Formulation", H1),
        p("Let A denote immutable source audio and F a candidate wavefield description. Let R(A,F) be a rendering or physical reproduction under field F, and let J be Moodify Judge. The north-star objective is"),
        Equation("F* = arg max_F  J(Render(Audio, F))", 1, column_width),
        Spacer(1, 2 * mm),
        p("Equation (1) is deliberately compact. It states that Moodify searches an acoustic possibility space rather than applying a fixed preset. It does not imply that J is already a calibrated universal scalar, nor that F can be identified from a stereo file alone."),
        p("2.1 Production Objective", H2),
        p("For production, the optimization must be robust across declared playback conditions c drawn from a target set C. It also depends on source identity and creative intent I:"),
        Equation("F* = arg max_(F in Omega) E_c[J(Render(A,F;c), A, I)]", 2, column_width),
        Spacer(1, 2 * mm),
        p("The feasible set is constrained by identity preservation, loudness-matched comparison, reproduction safety, evidence completeness, reproducibility, uncertainty, and human authority. If no feasible candidate demonstrates positive net gain over the original playback baseline, the correct result is KEEP_ORIGINAL."),
        p("3 Definitions and Evidence Classes", H1),
        table([
            ["Term", "Operational meaning"],
            ["Waveform", "Immutable source samples and provenance."],
            ["Wavefield", "Target space, reproduction chain, propagation conditions, and observation positions."],
            ["Render", "Simulated rendering or calibrated physical reproduction."],
            ["HEAR", "Observation of source evidence or reproduced-field evidence."],
            ["Judge", "Scoped authority for accept, retry, adjust, original, or human escalation."],
            ["F*", "Best supported field inside the stated target and evidence scope."],
        ], [31 * mm, column_width - 31 * mm]),
        Spacer(1, 2 * mm),
        p("Evidence is labeled <b>measured</b>, <b>simulated</b>, or <b>inferred</b>. A visualization cannot promote simulated or inferred content into measurement. The label follows the artifact into every report and Judge decision."),
        p("4 System Architecture", H1),
        p("The Wavefield loop preserves the source while allowing the field and rendering conditions to evolve. The same Core owns observations, profiles, verification, and Judge authority across Studio, API, CLI, and App interfaces."),
        ArchitectureFigure(column_width),
        p("4.1 Two-Judge Invariant", H2),
        p("Judge Before establishes what happened in the source, whether intervention is justified, and which traits must be protected. Judge After compares source and candidate under aligned conditions. A renderer, studio, model, or service provider may produce a candidate but cannot certify its own success."),
        p("4.2 Replaceable Realization Providers", H2),
        p("Simulation engines, binaural renderers, loudspeaker systems, rooms, measurement arrays, and external studios are field-realization providers. They may be replaced without creating a second Core or an independent judgment authority."),
        p("5 Observability", H1),
        p("Moodify's claim is not that every acoustic property is recoverable. Its claim is that previously opaque relationships can be represented with explicit limits. A source file supports time-frequency evolution, dynamics, phase, channel correlation, and stereo amplitude-density observations. A calibrated reproduction setup adds transfer responses and position-specific pressure measurements."),
        table([
            ["Observable", "Supported conclusion", "Unsupported conclusion"],
            ["Time-frequency energy", "Spectral evolution in the source", "Complete room pressure field"],
            ["L/R phase and density", "Stereo projection and phase risk", "Stable image at arbitrary positions"],
            ["Binaural or array capture", "Measured field at sampled positions", "Facts at unsampled positions"],
            ["Propagation simulation", "Result under a stated model", "Equivalent physical measurement"],
        ], [25 * mm, 37 * mm, column_width - 62 * mm], 6.1),
        p("5.1 Physical Truth Boundary", H2),
        p("A mono or stereo file cannot establish a real three-dimensional pressure field. Such a field requires a calibrated playback chain, room description, microphones or a binaural head or array, positions, timing, and environmental metadata. The system must refuse a three-dimensional measurement claim when those prerequisites are absent."),
        p("6 Wavefield Search", H1),
        p("The search space can include room scale, early reflection timing, decay structure, diffusion, direct-to-reverberant ratio, channel or object layout, listener position, transducer response, and content-dependent rendering parameters. Search may be Bayesian, evolutionary, gradient-free, or human-guided; the method is secondary to governed evidence and repeatable evaluation."),
        p("6.1 Multi-objective Judge", H2),
        p("Judge should initially produce a structured decision rather than a single aesthetic score. Candidate quality may include identity fidelity, clarity, spatial stability, dynamic integrity, translation, safety, and listening preference. Scalarization weights remain human-governed until calibrated evidence supports a narrower machine authority."),
        Equation("J = {identity, clarity, space, dynamics, translation, safety, uncertainty}", 3, column_width),
        Spacer(1, 2 * mm),
        p("6.2 Robustness Across Conditions", H2),
        p("A field that succeeds only at one chair in one expensive room may still be useful, but its scope must be explicit. A general-purpose profile should be evaluated across target devices, positions, and environments. Expected benefit and worst-case regression should both be reported."),
        p("7 Studio-in-the-loop", H1),
        p("A physical studio closes the gap between source-domain analysis and real acoustic occurrence. The experiment should compare AI-generated and recorded works under the same calibrated chain, matched loudness, fixed listener positions, and blind review. Multi-position measurements should be synchronized with the digital source and room state."),
        table([
            ["Stage", "Required record"],
            ["Source", "Digest, codec, sample rate, channels, rights, intent"],
            ["Playback", "DAC, amplifier, loudspeakers, gain, calibration"],
            ["Space", "Geometry, treatment, temperature, positions"],
            ["Capture", "Microphone or array, orientation, clock, response"],
            ["Review", "Blind protocol, loudness match, reviewer, uncertainty"],
        ], [25 * mm, column_width - 25 * mm]),
        p("The first experiment should seek reproducible differences, not confirm a preferred story. A null or contradictory result is valid evidence and may return the physical-field program to research status."),
        p("8 Persistent Artifacts", H1),
        p("A single stereo WAV cannot reproduce the same physical field on arbitrary equipment. Moodify therefore preserves a compound result rather than an opaque enhanced file."),
        table([
            ["Artifact", "Purpose"],
            ["Wavefield Profile", "Versioned field target, parameters, applicable conditions"],
            ["Conditional renders", "Headphone, stereo, multichannel, object, or named-studio delivery"],
            ["Observation evidence", "Measured, simulated, and inferred evidence with uncertainty"],
            ["Judge record", "Before/after rationale, protected traits, review, final choice"],
            ["Rollback", "Original source, bypass path, and KEEP_ORIGINAL"],
        ], [32 * mm, column_width - 32 * mm]),
        p("9 Implementation Status", H1),
        p("The repository currently contains file-domain wave-spectral analysis, loudness and dynamics measurement, phase and stereo metrics, evidence records, playback profiles, reversible Mix Graph concepts, and rule-based technical judgment with human escalation. A mature learning-based Judge-1 is not implemented. Wavefield schema, calibrated studio integration, physical capture, conditional render contracts, and cross-environment Judge calibration are not implemented."),
        p("10 Open Research Program", H1),
        p("The staged program is: (1) define wavefield vocabulary and observation schema; (2) establish a deterministic Wavefield Profile and render contract; (3) validate a stereo projection baseline and binaural reference renderer; (4) conduct a calibrated studio-in-the-loop experiment; and (5) calibrate field selection and translation judgments."),
        p("11 Discussion", H1),
        p("From waveform to wavefield is a change in the unit of audio engineering. The source remains essential, but value emerges in the controlled relation between source, reproduction, space, observation, and listener. This relation makes the system more demanding: target conditions must be declared, evidence provenance must survive rendering, and claims must remain scoped."),
        p("The approach also changes what openness means. Open code without open theory exposes implementation but hides the reasons that shape it. Moodify Open Technology Notes therefore publish the question, thesis, definitions, formula, method, evidence boundary, failure condition, status, and revision history alongside code."),
        p("12 Conclusion", H1),
        p("Moodify seeks the field in which a musical work is best reproduced under explicit conditions. The compact objective F* = arg max J(Render(Audio,F)) provides a durable research direction, while the production formulation constrains optimization by identity, safety, evidence, robustness, and human authority. The immediate task is not to claim solved spatial intelligence, but to build the vocabulary, contracts, experiments, and Judge calibration required to make wavefield selection observable and accountable."),
        p("Conflict of Interest", H1),
        p("The author is the founder of Rongjing Wenchuan (Shenzhen) Technology Co., Ltd. and the designer of the Moodify project. The architecture is commercially relevant. No independent production-scale validation is claimed in this note."),
        p("Data and Code Availability", H1),
        p("Moodify code, governance, and technical theory are developed in public at https://github.com/huliye24/moodify-ai. Capabilities marked proposed or research are not represented as production implementations."),
        p("AI-Assistance Disclosure", H1),
        p("A generative language model assisted with manuscript structuring, drafting, and typesetting. The author supplied the technical direction and remains responsible for claims, equations, boundaries, and interpretations."),
        p("References", H1),
        p("[1] Moodify, \"Wavefield Core Principle - From Waveform to Wavefield,\" Open Technology Note source, 2026.", REF),
        p("[2] ITU-R, \"Algorithms to measure audio programme loudness and true-peak audio level,\" Recommendation ITU-R BS.1770-5, 2023.", REF),
        p("[3] ITU-R, \"Method for the subjective assessment of intermediate quality level of audio systems,\" Recommendation ITU-R BS.1534-3, 2015.", REF),
        p("[4] ISO, \"Acoustics - Measurement of room acoustic parameters,\" ISO 3382 series.", REF),
        p("[5] AES, \"AES standard for file exchange - Spatial acoustic data file format,\" AES69.", REF),
        p("[6] W3C, \"PROV-O: The PROV Ontology,\" W3C Recommendation, 2013.", REF),
        p("[7] Moodify, \"Judge Core Principle,\" public canonical documentation, 2026.", REF),
    ]
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    col_w = (PAGE_W - 2 * MARGIN_X - GUTTER) / 2
    first_top = PAGE_H - 122 * mm
    first_frames = [
        Frame(MARGIN_X, MARGIN_B, col_w, first_top - MARGIN_B, leftPadding=0, rightPadding=2.5 * mm, topPadding=0, bottomPadding=0),
        Frame(MARGIN_X + col_w + GUTTER, MARGIN_B, col_w, first_top - MARGIN_B, leftPadding=2.5 * mm, rightPadding=0, topPadding=0, bottomPadding=0),
    ]
    regular_top = PAGE_H - 17 * mm
    regular_frames = [
        Frame(MARGIN_X, MARGIN_B, col_w, regular_top - MARGIN_B, leftPadding=0, rightPadding=2.5 * mm, topPadding=0, bottomPadding=0),
        Frame(MARGIN_X + col_w + GUTTER, MARGIN_B, col_w, regular_top - MARGIN_B, leftPadding=2.5 * mm, rightPadding=0, topPadding=0, bottomPadding=0),
    ]
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=17 * mm, bottomMargin=MARGIN_B, title="From Waveform to Wavefield",
        author="Xuanzhen Zhu / Moodify", subject="Moodify Open Technology Note MFY-TN-001",
    )
    doc.addPageTemplates([
        PageTemplate(id="First", frames=first_frames, onPage=first_page),
        PageTemplate(id="Later", frames=regular_frames, onPage=header_footer),
    ])
    doc.build(build_story(col_w))
    print(OUTPUT.resolve())


if __name__ == "__main__":
    main()
