"""
Generates:
1. BMI_DevOps_Viva_Guide.pdf (ReportLab)
2. BMI_DevOps_Viva_Presentation.pptx (python-pptx)
Covering: What, Why, Why this and not that, Architecture, End-to-End flow, and Viva Q&A.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors

# ==============================================================================
# 1. PPTX GENERATION
# ==============================================================================
def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Color Palette
    DARK_BLUE = RGBColor(15, 32, 67)     # #0F2043
    TEAL = RGBColor(0, 150, 136)          # #009688
    LIGHT_BG = RGBColor(245, 247, 250)    # #F5F7FA
    WHITE = RGBColor(255, 255, 255)
    DARK_GRAY = RGBColor(40, 44, 52)      # Text
    ACCENT_ORANGE = RGBColor(230, 100, 40)
    CARD_BG = RGBColor(235, 240, 248)

    slides_data = [
        {
            "title": "BMI Calculator CI/CD Pipeline",
            "subtitle": "Complete Project Architecture, Technology Justification & Viva Preparation",
            "type": "title",
            "points": [
                "Jenkins  ->  Docker  ->  Ansible (Trivy)  ->  Terraform  ->  K3s (Kubernetes)",
                "A Production-Grade Shift-Left Security & Infrastructure-as-Code Pipeline",
                "Prepared for Cloud Computing & DevOps Evaluation"
            ]
        },
        {
            "title": "Problem Statement & Pipeline Flow",
            "subtitle": "Connecting the 5 stages from source code to running container",
            "type": "cards",
            "cards": [
                ("1. Package (Docker)", "Builds lightweight Python 3.11-slim container. Multi-layer caching for fast rebuilds, non-root user for security."),
                ("2. Scan (Ansible + Trivy)", "Automates CVE scanning on built image. Exits with error if CRITICAL or HIGH vulnerabilities found, failing the pipeline."),
                ("3. Push (Registry)", "Pushes only verified, clean images to local registry (localhost:5000), preventing infected code from reaching clusters."),
                ("4. Deploy (Terraform)", "Declarative IaC pushes Deployment (2 replicas) and NodePort Service to K3s cluster. Maintains state and lifecycle."),
                ("5. Run (K3s Kubernetes)", "Lightweight K8s cluster manages pod lifecycles, health probes (/health), traffic routing, and auto-restarts.")
            ]
        },
        {
            "title": "Application Layer: Python Flask BMI App",
            "subtitle": "What it is, why Flask, and why this choice matters",
            "type": "comparison",
            "left_title": "What It Does & Key Features",
            "left_points": [
                "Simple web UI for weight (kg) & height (m) calculation.",
                "Calculates BMI and classifies into Underweight, Normal, Overweight, Obese.",
                "Includes dedicated /health endpoint returning {'status': 'ok'}, 200.",
                "The /health endpoint is CRITICAL for Kubernetes liveness & readiness probes."
            ],
            "right_title": "Why Flask? (Why this & not that?)",
            "right_points": [
                "Flask vs Django: Django is monolithic and heavy with unnecessary ORM/admin for a microservice. Flask is lightweight microframework.",
                "Flask vs Node.js: Python is standard in cloud computing and data science, zero boilerplate for REST/HTTP.",
                "Simplicity: Fast startup (<0.5s), minimal container memory (<40MB), clean separation of concerns."
            ]
        },
        {
            "title": "Packaging Layer: Docker Containerization",
            "subtitle": "Eliminating 'works on my machine' with reproducible runtime environments",
            "type": "comparison",
            "left_title": "Docker Concepts & Dockerfile",
            "left_points": [
                "Image: Immutable, portable blueprint containing code, runtime & dependencies.",
                "Container: Running isolated process created from an image.",
                "FROM python:3.11-slim: Minimal Debian Linux base image.",
                "Layer Caching: 'COPY requirements.txt' and 'RUN pip install' before code copy.",
                "Security: 'USER appuser' ensures container does NOT run as root!"
            ],
            "right_title": "Why Docker? (Why this & not that?)",
            "right_points": [
                "Docker vs Virtual Machines (VMs): VMs emulate full OS hardware (heavy, GBs RAM, slow boot). Containers share the host kernel (light, MBs RAM, seconds boot).",
                "Docker vs Raw Python: No dependency version conflicts on the host system; guarantees identical behavior across dev, Jenkins, and K3s.",
                "Universal artifact: Kubernetes natively orchestrates Docker images."
            ]
        },
        {
            "title": "Orchestration Layer: Jenkins CI/CD",
            "subtitle": "The automated conductor driving continuous integration & delivery",
            "type": "comparison",
            "left_title": "What Jenkins Does in this Project",
            "left_points": [
                "Pipeline-as-Code via declarative Jenkinsfile in Git repository.",
                "Listens for code commits and triggers automated multi-stage builds.",
                "Enforces fail-fast execution: if vulnerability scan fails, downstream deployment is aborted.",
                "Provides console logs and audit trail for every single build."
            ],
            "right_title": "Why Jenkins? (Why this & not that?)",
            "right_points": [
                "Jenkins vs GitHub Actions / GitLab CI: Cloud runners require external internet, token setups, and cost tokens. Jenkins runs 100% locally on-premises.",
                "Jenkins vs Manual Scripts: Manual execution is error-prone, untracked, and cannot self-trigger on git push.",
                "Extensible: Unmatched ecosystem of plugins and native pipeline scriptability."
            ]
        },
        {
            "title": "Security Layer: Ansible + Trivy Vulnerability Scan",
            "subtitle": "Implementing 'Shift-Left Security' inside the CI/CD pipeline",
            "type": "comparison",
            "left_title": "How the Security Gate Operates",
            "left_points": [
                "Ansible playbook (playbook.yml) targets localhost with inventory.ini.",
                "Installs Trivy scanner automatically if not already present on host.",
                "Executes: trivy image --severity CRITICAL,HIGH --exit-code 1 <image>.",
                "If critical CVEs exist, Trivy returns exit code 1, Ansible registers failure, Jenkins halts!"
            ],
            "right_title": "Why Ansible & Trivy? (Why this & not that?)",
            "right_points": [
                "Ansible vs Shell Script: Ansible playbooks are idempotent, structured YAML, self-documenting, and scale to multiple target scan hosts.",
                "Trivy vs Clair / Snyk: Snyk requires commercial API keys; Clair needs a database backend. Trivy is a single zero-config binary with fastest CVE lookup.",
                "Shift-Left Security: Detects vulnerable OS libraries (OpenSSL, glibc) before code ever touches production."
            ]
        },
        {
            "title": "Provisioning Layer: Terraform (IaC)",
            "subtitle": "Infrastructure as Code: Declaring desired state rather than running commands",
            "type": "comparison",
            "left_title": "What Terraform Manages",
            "left_points": [
                "Uses official HashiCorp Kubernetes provider (hashicorp/kubernetes).",
                "Connects directly to K3s cluster API via /etc/rancher/k3s/k3s.yaml.",
                "Creates kubernetes_deployment with 2 replicas and /health liveness probe.",
                "Creates kubernetes_service exposing application via NodePort 30080.",
                "Dynamically receives the new image:tag from Jenkins via -var parameter."
            ],
            "right_title": "Why Terraform? (Why this & not that?)",
            "right_points": [
                "Terraform vs kubectl apply: Kubectl just blindly pushes YAML with no state tracking. Terraform maintains terraform.tfstate, tracks drift, and handles rollbacks.",
                "Declarative vs Imperative: You declare WHAT state you want (2 replicas); Terraform calculates HOW to reach that state.",
                "Enterprise Standard: One unified syntax (HCL) to manage K8s, AWS, Azure, GCP."
            ]
        },
        {
            "title": "Runtime Layer: K3s (Lightweight Kubernetes)",
            "subtitle": "Production-grade container orchestration with minimal footprint",
            "type": "comparison",
            "left_title": "Kubernetes Architecture Used",
            "left_points": [
                "Deployment: Manages ReplicaSet (2 pods). Automatically self-heals if a pod crashes.",
                "Service (NodePort 30080): Exposes static port on every cluster node for browser access.",
                "Liveness Probe: Continuously hits /health every 10s. Restarts pod if it fails.",
                "Readiness Probe: Ensures pod is warm before routing traffic to it."
            ],
            "right_title": "Why K3s? (Why this & not that?)",
            "right_points": [
                "K3s vs Kubeadm / Full K8s: Full K8s requires 4GB+ RAM, multiple binaries, complex etcd setup. K3s is single binary under 100MB and uses <512MB RAM.",
                "K3s vs Minikube / Kind: Minikube is purely a dev simulator. K3s is a CNCF-certified, production-ready Kubernetes distribution created by Rancher.",
                "Ideal for Edge & CI/CD: Boots in 30 seconds on any Linux machine or VM."
            ]
        },
        {
            "title": "Complete 'Why This & Not That' Matrix",
            "subtitle": "Memorize this table for instant high marks in your viva",
            "type": "table",
            "headers": ["Tool Used", "Alternative Considered", "Why We Chose Our Tool"],
            "rows": [
                ["Flask (Python)", "Django / Express", "Microframework, ultra-fast boot, minimal memory, zero boilerplate for microservices."],
                ["Docker", "Virtual Machines (VM)", "Shares host OS kernel; 10x lighter, boots in seconds, standard container packaging."],
                ["Jenkins", "GitHub Actions", "Runs 100% locally on-premise without cloud tokens or internet dependencies."],
                ["Ansible", "Bash Shell Script", "Idempotent, human-readable YAML, structured task reporting, enterprise standard."],
                ["Trivy", "Clair / Snyk", "Zero-dependency single binary, scans OS & language packages, instant exit-code gating."],
                ["Terraform", "kubectl apply -f", "Tracks state (tfstate), provides diff plan, detects drift, manages full lifecycle."],
                ["K3s", "Full K8s (Kubeadm)", "Lightweight single binary (<100MB), CNCF-certified, uses 80% less memory than full K8s."]
            ]
        },
        {
            "title": "Top Viva Questions & Answers (Part 1)",
            "subtitle": "Core Architecture & Pipeline Mechanics",
            "type": "qa",
            "qa_list": [
                ("Q1: What is the main goal of this project?",
                 "Answer: To create an automated end-to-end CI/CD pipeline that packages a Python BMI app into a Docker container, enforces a security quality gate using Ansible and Trivy to scan for CVEs, and safely deploys it to a K3s Kubernetes cluster using Terraform Infrastructure-as-Code."),
                ("Q2: What is the purpose of the vulnerability scan gate?",
                 "Answer: It implements 'Shift-Left Security'. By running Trivy with '--exit-code 1' via Ansible, the Jenkins pipeline immediately halts if CRITICAL or HIGH vulnerabilities are detected, preventing vulnerable code from ever reaching the cluster."),
                ("Q3: What does 'Shift-Left' mean in DevOps?",
                 "Answer: It means moving testing, security checks, and compliance verification to the earliest possible stages of the software development lifecycle (left side of the pipeline), rather than discovering flaws in production."),
                ("Q4: What is the difference between an Image and a Container?",
                 "Answer: An image is a static, read-only template with code, runtime, and libraries (like a class in OOP). A container is a running, stateful instance of that image (like an object in OOP).")
            ]
        },
        {
            "title": "Top Viva Questions & Answers (Part 2)",
            "subtitle": "Terraform, Kubernetes & Operational Security",
            "type": "qa",
            "qa_list": [
                ("Q5: Why use Terraform instead of kubectl apply?",
                 "Answer: Terraform tracks state in 'terraform.tfstate', detects drift between real-world infrastructure and configuration, calculates dependencies, and provides 'terraform plan' to preview changes before applying them."),
                ("Q6: How does Kubernetes know if your application is healthy?",
                 "Answer: Through Liveness and Readiness probes defined in the Terraform deployment. Kubernetes periodically performs an HTTP GET on '/health'. If the container returns anything other than 200 OK, Kubernetes automatically restarts the pod."),
                ("Q7: Why run as non-root user inside Dockerfile?",
                 "Answer: Defense-in-depth security best practice. If an attacker discovers a remote code execution vulnerability in the application, running as 'appuser' prevents them from gaining root privileges on the underlying host kernel."),
                ("Q8: What is idempotency and where is it used?",
                 "Answer: An idempotent operation produces the exact same result no matter how many times it is executed. Both Ansible tasks and Terraform apply are idempotent: if the desired state already exists, no changes are made.")
            ]
        },
        {
            "title": "Viva Traps: What NOT to Say & Pro Tips",
            "subtitle": "Avoid common pitfalls and speak like a professional cloud engineer",
            "type": "comparison",
            "left_title": "DON'T Say This (Common Mistakes)",
            "left_points": [
                "DON'T say: 'Docker is a virtual machine.' (Containers share host kernel; VMs emulate entire hardware!).",
                "DON'T say: 'Terraform runs the application.' (Terraform only PROVISIONS the K8s objects; K3s runs the containers!).",
                "DON'T say: 'Ansible does the deployment.' (Ansible runs the security scan; Terraform handles deployment!).",
                "DON'T say: 'Kubernetes builds the Docker image.' (Jenkins and Docker build the image; Kubernetes only runs it!).",
                "DON'T say: 'NodePort is a load balancer in AWS.' (NodePort is a Kubernetes service type opening a port on cluster nodes)."
            ],
            "right_title": "DO Say This (Pro Phrases)",
            "right_points": [
                "DO say: 'We implemented Shift-Left Security by embedding Trivy scans inside an Ansible playbook.'",
                "DO say: 'Terraform provides declarative Infrastructure as Code with state management and drift detection.'",
                "DO say: 'K3s provides a CNCF-certified, lightweight Kubernetes runtime ideal for resource-constrained environments.'",
                "DO say: 'Our Dockerfile employs layer caching and follows non-root execution principles.'",
                "DO say: 'The pipeline enforces fail-fast architecture: zero vulnerable images reach the registry.'"
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # Background bar
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.2))
        tf = header_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        
        p2 = tf.add_paragraph()
        p2.text = data["subtitle"]
        p2.font.size = Pt(14)
        p2.font.color.rgb = TEAL

        stype = data.get("type")

        if stype == "title":
            box = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(10.3), Inches(4.0))
            tf2 = box.text_frame
            for pt in data["points"]:
                p = tf2.add_paragraph()
                p.text = pt
                p.font.size = Pt(20)
                p.font.color.rgb = DARK_GRAY
                p.space_after = Pt(24)

        elif stype == "cards":
            lefts = [0.8, 3.2, 5.6, 8.0, 10.4]
            width = Inches(2.2)
            height = Inches(4.8)
            for idx, (head, body) in enumerate(data["cards"]):
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(lefts[idx]), Inches(1.8), width, height)
                shape.fill.solid()
                shape.fill.fore_color.rgb = CARD_BG
                shape.line.color.rgb = TEAL
                shape.line.width = Pt(1.5)
                
                tf_card = shape.text_frame
                tf_card.word_wrap = True
                p_c = tf_card.paragraphs[0]
                p_c.text = head
                p_c.font.bold = True
                p_c.font.size = Pt(15)
                p_c.font.color.rgb = DARK_BLUE
                p_c.space_after = Pt(14)
                
                p_b = tf_card.add_paragraph()
                p_b.text = body
                p_b.font.size = Pt(12)
                p_b.font.color.rgb = DARK_GRAY

        elif stype == "comparison":
            w = Inches(5.6)
            h = Inches(5.0)
            
            # Left box
            s1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), w, h)
            s1.fill.solid()
            s1.fill.fore_color.rgb = CARD_BG
            s1.line.color.rgb = TEAL
            tf1 = s1.text_frame
            tf1.word_wrap = True
            p = tf1.paragraphs[0]
            p.text = data["left_title"]
            p.font.bold = True
            p.font.size = Pt(18)
            p.font.color.rgb = DARK_BLUE
            p.space_after = Pt(14)
            for item in data["left_points"]:
                pi = tf1.add_paragraph()
                pi.text = "• " + item
                pi.font.size = Pt(13)
                pi.font.color.rgb = DARK_GRAY
                pi.space_after = Pt(10)

            # Right box
            s2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), w, h)
            s2.fill.solid()
            s2.fill.fore_color.rgb = WHITE
            s2.line.color.rgb = ACCENT_ORANGE
            tf2 = s2.text_frame
            tf2.word_wrap = True
            p = tf2.paragraphs[0]
            p.text = data["right_title"]
            p.font.bold = True
            p.font.size = Pt(18)
            p.font.color.rgb = ACCENT_ORANGE
            p.space_after = Pt(14)
            for item in data["right_points"]:
                pi = tf2.add_paragraph()
                pi.text = "✓ " + item
                pi.font.size = Pt(13)
                pi.font.color.rgb = DARK_GRAY
                pi.space_after = Pt(10)

        elif stype == "table":
            rows = len(data["rows"]) + 1
            cols = len(data["headers"])
            table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
            table = table_shape.table
            table.columns[0].width = Inches(2.2)
            table.columns[1].width = Inches(2.5)
            table.columns[2].width = Inches(7.0)

            # Headers
            for c_idx, h in enumerate(data["headers"]):
                cell = table.cell(0, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = DARK_BLUE
                cell.text = h
                p = cell.text_frame.paragraphs[0]
                p.font.bold = True
                p.font.size = Pt(14)
                p.font.color.rgb = WHITE

            # Data
            for r_idx, row in enumerate(data["rows"]):
                for c_idx, val in enumerate(row):
                    cell = table.cell(r_idx + 1, c_idx)
                    cell.text = val
                    p = cell.text_frame.paragraphs[0]
                    p.font.size = Pt(12)
                    p.font.color.rgb = DARK_GRAY
                    if r_idx % 2 == 1:
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = CARD_BG

        elif stype == "qa":
            box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2))
            tf_qa = box.text_frame
            tf_qa.word_wrap = True
            for q, a in data["qa_list"]:
                pq = tf_qa.add_paragraph()
                pq.text = q
                pq.font.bold = True
                pq.font.size = Pt(15)
                pq.font.color.rgb = DARK_BLUE
                
                pa = tf_qa.add_paragraph()
                pa.text = a
                pa.font.size = Pt(13)
                pa.font.color.rgb = DARK_GRAY
                pa.space_after = Pt(14)

    output_path = "BMI_DevOps_Viva_Presentation.pptx"
    prs.save(output_path)
    print(f"  [PASS] Successfully generated PowerPoint: {output_path}")


# ==============================================================================
# 2. PDF GENERATION
# ==============================================================================
def create_pdf():
    pdf_filename = "BMI_DevOps_Viva_Guide.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F2043")
    c_secondary = colors.HexColor("#009688")
    c_accent = colors.HexColor("#E66428")
    c_dark = colors.HexColor("#2C3E50")
    c_light_bg = colors.HexColor("#F4F7FB")

    # Typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_dark,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_dark,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    question_style = ParagraphStyle(
        'DocQuestion',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )
    answer_style = ParagraphStyle(
        'DocAnswer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_dark,
        leftIndent=12,
        spaceAfter=8
    )
    box_style = ParagraphStyle(
        'DocBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark
    )

    story = []

    # Title & Header
    story.append(Paragraph("BMI Calculator CI/CD Pipeline", title_style))
    story.append(Paragraph("Comprehensive Architecture, Technology Rationale & Viva Master Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_secondary, spaceBefore=0, spaceAfter=15))

    # Executive Overview
    story.append(Paragraph("1. Executive Summary & Problem Statement", h1_style))
    story.append(Paragraph(
        "<b>Problem Statement:</b> Create a local <b>Jenkins</b> pipeline that triggers a <b>Docker</b> build, "
        "runs <b>Ansible</b> scripts to check container vulnerabilities, and deploys the app to <b>K3s (Kubernetes)</b> "
        "using <b>Terraform</b> scripts.",
        body_style
    ))
    story.append(Paragraph(
        "This project models an enterprise-grade, shift-left DevOps delivery pipeline. It unites application development "
        "(Python/Flask), containerization (Docker), continuous integration (Jenkins), automated security governance "
        "(Ansible + Trivy), declarative Infrastructure-as-Code (Terraform), and container orchestration (K3s Kubernetes).",
        body_style
    ))

    # Architecture Table
    arch_data = [
        [Paragraph("<b>Pipeline Stage</b>", box_style), Paragraph("<b>Technology</b>", box_style), Paragraph("<b>Core Responsibility</b>", box_style)],
        [Paragraph("1. Application", box_style), Paragraph("Python 3.11 / Flask", box_style), Paragraph("Calculates BMI and provides <code>/health</code> probe endpoint.", box_style)],
        [Paragraph("2. Packaging", box_style), Paragraph("Docker (multi-layer)", box_style), Paragraph("Packages app into immutable image with non-root security.", box_style)],
        [Paragraph("3. Orchestration", box_style), Paragraph("Jenkins (Declarative)", box_style), Paragraph("Executes stages sequentially and enforces fail-fast error gating.", box_style)],
        [Paragraph("4. Security Scan", box_style), Paragraph("Ansible + Trivy", box_style), Paragraph("Scans image for CVEs; aborts pipeline if CRITICAL/HIGH found.", box_style)],
        [Paragraph("5. Provisioning", box_style), Paragraph("Terraform (IaC)", box_style), Paragraph("Pushes desired state (2 replicas, Service) to K3s cluster.", box_style)],
        [Paragraph("6. Runtime", box_style), Paragraph("K3s (Kubernetes)", box_style), Paragraph("Executes pods, manages self-healing, routes traffic via NodePort.", box_style)]
    ]
    t_arch = Table(arch_data, colWidths=[110, 120, 290])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 15))

    # Deep Dive on Tools: What, Why, Why This and Not That
    story.append(Paragraph("2. Deep Dive: Why This Tool and NOT That?", h1_style))

    tools = [
        ("A. Python Flask (Application Layer)", [
            ("What it is:", "A lightweight WSGI microframework for Python designed for rapid web applications and microservices."),
            ("Why used here:", "Contains minimal overhead, boots instantly (<0.5s), and exposes both the BMI calculation UI and a '/health' JSON probe."),
            ("Why NOT Django?", "Django is a heavyweight, full-stack monolith containing ORM, admin panel, and session engines unnecessary for a microservice. It bloats container image size."),
            ("Why NOT Express/Node.js?", "Python is the ubiquitous language of cloud computing and Linux administration; Flask delivers the smallest attack surface.")
        ]),
        ("B. Docker (Containerization Layer)", [
            ("What it is:", "An operating-system-level virtualization platform that packages software into immutable containers."),
            ("Why used here:", "Guarantees reproducible runtime environments, packaging Python, Flask, and dependencies together. Solves 'it works on my machine.'"),
            ("Why NOT Virtual Machines (VMs)?", "A VM virtualizes the entire hardware stack and boots a guest OS (GBs of memory, minutes to boot). Docker containers share the host Linux kernel (MBs of memory, seconds to boot)."),
            ("Security Highlight:", "The Dockerfile employs layer caching (pip install requirements before copying code) and enforces 'USER appuser' so processes never execute as root.")
        ]),
        ("C. Jenkins (Continuous Integration & Orchestration)", [
            ("What it is:", "An open-source automation server enabling automated building, testing, and deploying via Pipeline-as-Code (Jenkinsfile)."),
            ("Why used here:", "Acts as the pipeline master coordinator. Executes each stage sequentially, prints live console logs, and aborts before deployment if tests fail."),
            ("Why NOT GitHub Actions / GitLab CI?", "GitHub Actions runs on cloud runners, requiring internet connectivity, billing credits, and complex tunneling to access local K3s clusters. Jenkins runs 100% locally on-premises without cloud dependencies."),
            ("Why NOT raw bash scripts?", "Bash scripts lack visual dashboards, stage-by-stage retry capabilities, built-in credential management, and structured failure reporting.")
        ]),
        ("D. Ansible + Trivy (Shift-Left Security Gate)", [
            ("What it is:", "Ansible is an agentless automation engine. Trivy is a comprehensive vulnerability scanner for container images."),
            ("Why used here:", "Ansible executes a playbook that downloads Trivy if missing, scans the built image for CRITICAL/HIGH vulnerabilities, and fails with exit code 1 if CVEs are found."),
            ("Why NOT a direct shell command?", "Ansible playbooks are idempotent, written in human-readable YAML, support structured output registration, and can effortlessly scale to scan across multiple remote registry nodes."),
            ("Why NOT Clair or Snyk?", "Snyk requires proprietary cloud account keys and rate-limits free tiers. Clair requires an external PostgreSQL database. Trivy is a zero-dependency standalone binary.")
        ]),
        ("E. Terraform (Infrastructure as Code - IaC)", [
            ("What it is:", "A declarative Infrastructure-as-Code tool that provisions and manages resources across cloud providers and Kubernetes clusters."),
            ("Why used here:", "Terraform connects directly to the K3s cluster API via the HashiCorp Kubernetes provider, creating the Deployment (2 replicas) and NodePort Service."),
            ("Why NOT 'kubectl apply -f'?", "Kubectl is imperative and stateless—it pushes files without tracking state, cannot preview changes ('plan'), and cannot detect configuration drift. Terraform tracks reality in 'terraform.tfstate' and manages the full resource lifecycle."),
            ("Why NOT Helm?", "Helm is a package manager for pre-built charts. Terraform manages foundational infrastructure and seamlessly passes dynamic variables (such as new image tags) into Kubernetes definitions.")
        ]),
        ("F. K3s (Container Orchestration Layer)", [
            ("What it is:", "A lightweight, CNCF-certified Kubernetes distribution packaged as a single binary under 100MB, created by Rancher."),
            ("Why used here:", "Runs the production containers, handles self-healing (restarting crashed pods), load balances traffic between the 2 replicas, and monitors pod health."),
            ("Why NOT full Kubernetes (Kubeadm)?", "Kubeadm requires at least 4GB of RAM, multiple system services, and complex etcd management. K3s replaces etcd with SQLite/embedded storage, consuming less than 512MB RAM while remaining 100% compliant with Kubernetes APIs."),
            ("Why NOT Minikube?", "Minikube is strictly a development sandbox. K3s is a true production-grade distribution deployed globally in edge, IoT, and lightweight server environments.")
        ])
    ]

    for title, points in tools:
        story.append(Paragraph(title, h2_style))
        for p_head, p_desc in points:
            story.append(Paragraph(f"• <b>{p_head}</b> {p_desc}", bullet_style))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # Comprehensive Comparison Matrix
    story.append(Paragraph("3. Technology Comparison Matrix (Viva Cheat Sheet)", h1_style))
    comp_headers = [Paragraph("<b>Component</b>", box_style), Paragraph("<b>Choice</b>", box_style), Paragraph("<b>Alternative</b>", box_style), Paragraph("<b>Why Our Choice Won</b>", box_style)]
    comp_rows = [
        [Paragraph("Framework", box_style), Paragraph("Flask", box_style), Paragraph("Django", box_style), Paragraph("Zero boilerplate, instant boot, minimal memory footprint.", box_style)],
        [Paragraph("Runtime", box_style), Paragraph("Docker", box_style), Paragraph("Virtual Machine", box_style), Paragraph("Kernel sharing: 10x lighter, boots in seconds, standard packaging.", box_style)],
        [Paragraph("CI/CD", box_style), Paragraph("Jenkins", box_style), Paragraph("GitHub Actions", box_style), Paragraph("100% local, self-hosted, no cloud tokens or internet needed.", box_style)],
        [Paragraph("Security", box_style), Paragraph("Ansible+Trivy", box_style), Paragraph("Shell Script", box_style), Paragraph("Idempotent, YAML-based, structured enterprise scanner pattern.", box_style)],
        [Paragraph("Scanner", box_style), Paragraph("Trivy", box_style), Paragraph("Snyk / Clair", box_style), Paragraph("Single binary, no database required, instant CVE check.", box_style)],
        [Paragraph("IaC", box_style), Paragraph("Terraform", box_style), Paragraph("kubectl apply", box_style), Paragraph("State tracking (tfstate), diff preview (plan), drift detection.", box_style)],
        [Paragraph("Orchestrator", box_style), Paragraph("K3s", box_style), Paragraph("Kubeadm", box_style), Paragraph("CNCF-compliant, <100MB binary, 80% lower RAM footprint.", box_style)]
    ]
    t_comp = Table([comp_headers] + comp_rows, colWidths=[70, 75, 85, 290])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 15))

    # Top 15 Viva Questions & Answers
    story.append(Paragraph("4. Top 15 Viva Questions & Word-for-Word Answers", h1_style))
    story.append(Paragraph("Practice these concise answers to achieve top marks during your viva or project presentation:", body_style))

    viva_qas = [
        ("Q1: Explain the high-level architecture of your project in one sentence.",
         "Jenkins automates the pipeline: it builds a Docker image of our Python BMI web app, uses Ansible to scan that image for vulnerabilities with Trivy, and if it passes, uses Terraform to declare the deployment to a lightweight K3s Kubernetes cluster."),
        ("Q2: What is 'Shift-Left Security' and how is it implemented in this project?",
         "'Shift-Left Security' means performing vulnerability checks early in the development lifecycle rather than in production. We implement this in Stage 3: Ansible triggers a Trivy scan on the newly built container. If CRITICAL or HIGH vulnerabilities are detected, Trivy exits with code 1, which immediately fails the Jenkins build and blocks deployment."),
        ("Q3: What is the difference between a Docker Image and a Container?",
         "A Docker image is a static, read-only, immutable template containing application code, runtime, and libraries. A container is a running, isolated execution instance created from that image."),
        ("Q4: Why did your Dockerfile copy 'requirements.txt' before copying the rest of the application code?",
         "To take advantage of Docker layer caching. Dependencies in 'requirements.txt' rarely change. By copying and installing them first, Docker reuses the cached layer on subsequent builds, reducing rebuild time from minutes to seconds."),
        ("Q5: Why did you add 'USER appuser' inside the Dockerfile?",
         "Security defense-in-depth. By default, containers run as root. If an attacker breaches the application, running as an unprivileged user prevents them from acquiring root privileges on the underlying host kernel."),
        ("Q6: What does 'Infrastructure as Code' (IaC) mean, and why use Terraform over 'kubectl apply'?",
         "IaC means managing infrastructure via version-controlled configuration files rather than manual commands. Terraform maintains a state file ('terraform.tfstate') to track real-world infrastructure, preview changes via 'terraform plan', detect configuration drift, and ensure declarative idempotency."),
        ("Q7: What is the difference between K3s and standard Kubernetes (Kubeadm)?",
         "K3s is a lightweight, fully compliant, CNCF-certified Kubernetes distribution packaged as a single binary under 100MB. It replaces heavyweight etcd with SQLite and strips out legacy cloud providers, using under 512MB RAM compared to Kubeadm's 4GB+ requirement."),
        ("Q8: How does Kubernetes monitor application health in your setup?",
         "Through Liveness and Readiness probes declared in 'terraform/main.tf'. K3s periodically executes an HTTP GET on '/health' on port 5000. If the application crashes or hangs and fails to return HTTP 200, Kubernetes automatically destroys and restarts the pod."),
        ("Q9: What is a Kubernetes Service and why did you select 'NodePort'?",
         "Pods are ephemeral and get new IP addresses whenever recreated. A Service provides a permanent, stable network IP and load-balances traffic across pods. We selected 'NodePort' (port 30080) because it opens that fixed port on every cluster node, allowing direct web browser access without needing a cloud load balancer."),
        ("Q10: What is idempotency and where does it occur in this project?",
         "Idempotency means that running an operation multiple times produces the exact same end state without duplicate side-effects. Both our Ansible playbook and Terraform scripts are idempotent: if the scan or cluster resources already match desired state, re-running them makes zero changes."),
        ("Q11: Why is an Ansible inventory file needed when scanning on localhost?",
         "Ansible requires an inventory to know target hosts and connection plugins. In 'inventory.ini', setting 'localhost ansible_connection=local' tells Ansible to execute tasks locally on the build machine without trying to establish an SSH connection."),
        ("Q12: What happens if Trivy finds a HIGH vulnerability in the container?",
         "Trivy exits with status code 1 because of the '--exit-code 1' flag. Ansible registers this non-zero exit code as a task failure, triggering the 'fail' module. This causes the Jenkins pipeline step to abort immediately, preventing the push to the registry and deployment to K3s."),
        ("Q13: What is the purpose of the local Docker registry running on port 5000?",
         "In a production environment, images are pushed to Docker Hub or AWS ECR. For our local CI/CD environment, running a local registry ('registry:2') allows Jenkins to push images and K3s to pull images locally without requiring internet access or third-party credentials."),
        ("Q14: How does Jenkins pass the dynamic image tag to Terraform?",
         "Jenkins assigns the current build number to an environment variable ('${BUILD_NUMBER}'). It passes this to Terraform during the apply stage via the CLI flag: '-var=\"image_name=localhost:5000/bmi-calculator:${BUILD_NUMBER}\"'. Terraform then updates the Kubernetes deployment definition."),
        ("Q15: What are the common viva mistakes to avoid?",
         "Never confuse containers with virtual machines (containers share the host kernel). Never claim Terraform runs the app (Terraform provisions the K8s objects; K3s runs the containers). Never claim Ansible deploys the app (Ansible executes the security scan; Terraform executes deployment).")
    ]

    for q, a in viva_qas:
        story.append(Paragraph(q, question_style))
        story.append(Paragraph(f"<b>Answer:</b> {a}", answer_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=5, spaceAfter=10))
    story.append(Paragraph("<b>End of Master Guide. Best of luck on your presentation and viva!</b>", subtitle_style))

    doc.build(story)
    print(f"  [PASS] Successfully generated PDF Guide: {pdf_filename}")

if __name__ == "__main__":
    print("=" * 60)
    print(" Generating DevOps Documentation & Presentation Assets...")
    print("=" * 60)
    create_presentation()
    create_pdf()
    print("=" * 60)
    print(" All documentation files generated successfully!")
    print("=" * 60)
