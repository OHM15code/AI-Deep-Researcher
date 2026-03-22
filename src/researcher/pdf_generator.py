import markdown
import os
from xhtml2pdf import pisa
from datetime import datetime

def convert_md_to_pdf(md_file_path, pdf_file_path):
    """
    Converts a Markdown file to a professional PDF document using xhtml2pdf.
    Features: Cover page, page numbers, styled headers, and tables.
    """
    if not os.path.exists(md_file_path):
        print(f"Error: {md_file_path} not found.")
        return

    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'tables', 'fenced_code', 'toc'])

        # Prepare date and title for the cover page
        current_date = datetime.now().strftime("%B %d, %Y")
        report_title = "Research Intelligence Report"
        
        # Try to extract the first H1 as the title
        import re
        match = re.search(r'#\s+(.*)', md_content)
        if match:
            report_title = match.group(1).strip()

        # Professional HTML/CSS Template
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: a4 portrait;
                    margin: 2cm;
                    @frame footer {{
                        -pdf-frame-content: footer_content;
                        bottom: 1cm;
                        margin-left: 2cm;
                        margin-right: 2cm;
                        height: 1cm;
                    }}
                }}
                
                /* Global */
                body {{
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.5;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}

                /* Cover Page */
                .cover-table {{
                    width: 100%;
                    height: 20cm; /* Fixed height instead of percentage */
                    border: 0;
                    page-break-after: always;
                    page-break-inside: avoid;
                }}
                
                .cover-content {{
                    text-align: center;
                    vertical-align: middle;
                    padding: 0;
                }}
                
                .report-header-box {{
                    border-bottom: 2pt solid #1a365d;
                    padding-bottom: 15pt;
                    margin-bottom: 30pt;
                    display: inline-block;
                    width: 85%;
                }}
                
                .report-title {{
                    font-size: 28pt;
                    font-weight: bold;
                    color: #1a365d;
                    margin-bottom: 10pt;
                }}
                
                .report-subtitle {{
                    font-size: 14pt;
                    color: #4a5568;
                    letter-spacing: 2pt;
                    text-transform: uppercase;
                }}
                
                .report-meta {{
                    margin-top: 2cm;
                    font-size: 11pt;
                    color: #718096;
                }}
                
                .report-meta p {{
                    margin: 2pt 0;
                    text-align: center;
                }}

                /* Typography */
                h1, h2, h3, h4 {{
                    color: #2b6cb0;
                    margin-top: 20pt;
                    margin-bottom: 10pt;
                }}
                
                h1 {{ font-size: 24pt; border-bottom: 1pt solid #cbd5e0; padding-bottom: 5pt; }}
                h2 {{ font-size: 18pt; }}
                h3 {{ font-size: 14pt; }}
                
                p {{ margin-bottom: 10pt; text-align: justify; }}
                
                /* Tables */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20pt;
                }}
                
                th, td {{
                    padding: 8pt;
                    border: 1px solid #e2e8f0;
                    text-align: left;
                }}
                
                th {{
                    background-color: #f7fafc;
                    font-weight: bold;
                    color: #2d3748;
                }}
                
                /* Code Blocks */
                pre {{
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    padding: 10pt;
                    border-radius: 4pt;
                    font-family: Courier, monospace;
                    font-size: 9pt;
                    overflow: hidden;
                }}
                
                /* Footer */
                #footer_content {{
                    text-align: center;
                    color: #a0aec0;
                    font-size: 9pt;
                    border-top: 0.5pt solid #e2e8f0;
                    padding-top: 5pt;
                }}
            </style>
        </head>
        <body>
            <!-- Cover Page -->
            <table class="cover-table">
                <tr>
                    <td class="cover-content">
                        <div class="report-header-box">
                            <div class="report-title">{report_title}</div>
                            <div class="report-subtitle">Synthetic Intelligence Analysis</div>
                        </div>
                        <div class="report-meta">
                            <p>Generated on: {current_date}</p>
                            <p>Powered by AI Researcher Crew</p>
                        </div>
                    </td>
                </tr>
            </table>

            <!-- Content -->
            <div id="content">
                {html_content}
            </div>

            <!-- Static Footer -->
            <div id="footer_content">
                AI Researcher Report - Page <pdf:pagenumber>
            </div>
        </body>
        </html>
        """

        with open(pdf_file_path, "wb") as f_pdf:
            pisa_status = pisa.CreatePDF(full_html, dest=f_pdf)

        if pisa_status.err:
            print(f"Error during PDF generation: {pisa_status.err}")
        else:
            print(f"Successfully converted {md_file_path} to {pdf_file_path} with enhanced layout.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    convert_md_to_pdf("report.md", "report.pdf")
