#!/usr/bin/env python3
"""Render generated reports; preserve PDFs/HTML and collect label evidence."""
from pathlib import Path
import sys,json,hashlib,os
import pymupdf
from playwright.sync_api import sync_playwright
p=Path(sys.argv[1]);out=p/'verification/documents';out.mkdir(parents=True,exist_ok=True)
os.environ['LD_LIBRARY_PATH']='/home/a/miniforge3/envs/biolearn-doclib/lib'+(':'+os.environ['LD_LIBRARY_PATH'] if os.environ.get('LD_LIBRARY_PATH') else '')
records=[]
for f in sorted((p/'output').rglob('*.pdf')):
    doc=pymupdf.open(f);pages=[]
    prefix=str(f.relative_to(p/'output')).replace('/','__')
    for index,page in enumerate(doc):
        text=page.get_text()
        pix=page.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2),alpha=False)
        name=prefix+f'.page{index+1}.png';pix.save(out/name)
        (out/(prefix+f'.page{index+1}.txt')).write_text(text)
        pages.append({'page':index+1,'width':pix.width,'height':pix.height,'text':text,'image':str(out/name)})
    records.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pages':pages})
    doc.close()
(out/'pdf_readback.json').write_text(json.dumps(records,indent=2)+'\n')
reports=sorted((p/'output').rglob('*multiqc_report.html'))
browser_records=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    for f in reports:
        errors=[];page=browser.new_page(viewport={'width':1600,'height':1050})
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(f.resolve().as_uri(),wait_until='networkidle',timeout=60000)
        page.wait_for_function('document.querySelectorAll(".mqc-section").length > 0',timeout=30000)
        name=str(f.relative_to(p/'output')).replace('/','__')
        page.screenshot(path=str(out/(name+'.overview.png')))
        body=page.locator('body').inner_text();(out/(name+'.text.txt')).write_text(body)
        sections=page.locator('.mqc-section').count()
        plots=page.locator('.js-plotly-plot').count()
        expected=['RAP1_IAA_30M_REP1','RAP1_UNINDUCED_REP1','RAP1_UNINDUCED_REP2','WT_REP1','WT_REP2']
        record={'path':str(f),'title':page.title(),'section_count':sections,'plot_count':plots,'page_errors':errors,'expected_sample_labels':{s:s in body for s in expected},'body_text_bytes':len(body),'browser_version':browser.version}
        # Open a plot section below the overview; the table and labels remain
        # inspectable even if report versions use canvas instead of Plotly.
        plot_sections=page.locator('.mqc-section').all()
        for i,section in enumerate(plot_sections[:8]):
            section.scroll_into_view_if_needed()
            section.screenshot(path=str(out/(name+f'.section{i+1}.png')))
        browser_records.append(record);page.close()
    browser.close()
(out/'html_readback.json').write_text(json.dumps(browser_records,indent=2)+'\n')
ok=bool(records) and bool(browser_records) and all(not r['page_errors'] and all(r['expected_sample_labels'].values()) for r in browser_records)
print(json.dumps({'pdf_files':len(records),'pdf_pages':sum(len(r['pages']) for r in records),'html':browser_records,'pass':ok},indent=2));sys.exit(0 if ok else 1)
