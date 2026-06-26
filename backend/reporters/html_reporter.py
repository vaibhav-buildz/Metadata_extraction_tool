from jinja2 import Template
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
 
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metadata Forensics - {{ filename }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Mono', monospace;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            line-height: 1.6;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid #64748b;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
        }
        header {
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
            padding: 40px;
            border-bottom: 3px solid #f97316;
        }
        h1 {
            font-size: 2.5em;
            color: #f97316;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .report-meta {
            display: flex;
            justify-content: space-around;
            font-size: 0.9em;
            color: #94a3b8;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #475569;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        h2 {
            color: #f97316;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f97316;
            text-transform: uppercase;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid #475569;
        }
        th {
            background: rgba(15, 23, 42, 0.8);
            color: #f97316;
            padding: 15px;
            text-align: left;
            border-bottom: 2px solid #f97316;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #475569;
        }
        tr:hover {
            background: rgba(30, 41, 59, 0.6);
        }
        .anomaly {
            padding: 15px;
            margin: 15px 0;
            background: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
            color: #fecaca;
        }
        .footer {
            text-align: center;
            padding: 20px;
            border-top: 1px solid #475569;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Forensics Report</h1>
            <div class="report-meta">
                <div><strong>File:</strong> {{ filename }}</div>
                <div><strong>Type:</strong> {{ file_type }}</div>
                <div><strong>Generated:</strong> {{ timestamp }}</div>
            </div>
        </header>
        <div class="content">
            {% for section_name, section_data in metadata.items() %}
                {% if section_data and section_name not in ['filename', 'file_type', 'file_size_bytes', 'anomalies'] %}
                <section class="section">
                    <h2>{{ section_name | replace('_', ' ') | title }}</h2>
                    {% if section_data is mapping %}
                        <table>
                            <thead>
                                <tr><th>Property</th><th>Value</th></tr>
                            </thead>
                            <tbody>
                                {% for key, value in section_data.items() %}
                                    <tr>
                                        <td><strong>{{ key }}</strong></td>
                                        <td>{{ value }}</td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div style="padding: 12px 15px; background: rgba(30, 41, 59, 0.4); border: 1px solid #475569; border-radius: 4px; font-weight: bold; margin-bottom: 20px;">
                            {{ section_data }}
                        </div>
                    {% endif %}
                </section>
                {% endif %}
            {% endfor %}
            {% if metadata.anomalies %}
            <section class="section">
                <h2>⚠️ Anomalies</h2>
                {% for anomaly in metadata.anomalies %}
                    <div class="anomaly">{{ anomaly }}</div>
                {% endfor %}
            </section>
            {% endif %}
        </div>
        <div class="footer">
            <p>Metadata Forensics Tool v1.0</p>
        </div>
    </div>
</body>
</html>"""
 
class HTMLReporter:
    @staticmethod
    def generate(metadata: Dict[str, Any], output_path: str | None = None) -> str:
        template = Template(HTML_TEMPLATE)
        render_kwargs = {
            "filename": metadata.get("filename", "Unknown"),
            "file_type": metadata.get("file_type", "Unknown"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": metadata
        }
        for k, v in metadata.items():
            if k not in render_kwargs:
                render_kwargs[k] = v
        html = template.render(**render_kwargs)
        if output_path:
            Path(output_path).write_text(html, encoding="utf-8")
        return html
 
if __name__ == "__main__":
    print("✓ HTMLReporter ready")
